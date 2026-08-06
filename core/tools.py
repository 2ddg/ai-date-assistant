"""Agent 工具集：Agent 可调用的外部能力"""
import logging
import urllib.parse

import httpx

from core.baidu_map_client import place_search, normalize_poi

logger = logging.getLogger(__name__)

TOOL_DESCRIPTIONS = [
    {
        "name": "search_date_spots",
        "description": "搜索约会地点。基于百度地图真实 POI 数据，根据用户需求（场景/预算/偏好）检索任意城市的真实约会地点，返回带地址/电话/评分的推荐列表。参数：query（完整需求描述，如'三里屯附近适合聊天的咖啡馆'）、city（城市，必填，如'北京市'）",
        "parameters": {"query": "string", "city": "string"},
    },
    {
        "name": "get_weather",
        "description": "查询指定城市的当前天气，用于判断约会是否适合户外活动。参数：city（城市名）",
        "parameters": {"city": "string"},
    },
    {
        "name": "analyze_outfit",
        "description": "分析穿搭照片，给出约会穿搭建议。参数：image_id（用户已上传的图片ID）、occasion（场合，可选）",
        "parameters": {"image_id": "string", "occasion": "string (可选)"},
    },
    {
        "name": "make_date_plan",
        "description": "生成完整的约会方案（时间线安排 + 建议 + 备选方案）。参数：date_type（约会类型，如'初次见面'、'周年纪念'）、city（城市）、budget（预算范围，可选）、preferences（偏好，可选）",
        "parameters": {"date_type": "string", "city": "string", "budget": "string (可选)", "preferences": "string (可选)"},
    },
]


async def search_date_spots(query: str, city: str = "", db=None) -> str:
    """调用百度地图 place API 检索真实约会地点"""
    if not city:
        return "请告诉我想在哪个城市约会。"

    result = await place_search(
        user_raw_request=query,
        region=city,
        sort="relevance",
    )

    pois = result.get("results", [])
    if not pois:
        return f"百度地图在 {city} 没找到匹配的地点，换个关键词或城市试试。"

    spots = [normalize_poi(p, city) for p in pois if p.get("name")][:5]
    lines = [f"在 {city} 找到 {len(spots)} 个真实约会地点："]
    for s in spots:
        rating = f"，评分{s['overall_rating']}" if s.get("overall_rating") else ""
        addr = f"，地址：{s['address']}" if s.get("address") else ""
        lines.append(f"• {s['name']}（{s['category']}，{s.get('price_level','')}{rating}）{addr}")
    return "\n".join(lines)


async def get_weather(city: str) -> str:
    """调用 wttr.in 免费天气 API"""
    from config import WEATHER_API_URL

    url = WEATHER_API_URL.format(city=urllib.parse.quote(city))
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                text = response.text.strip()
                if text and "Unknown location" not in text:
                    return f"{city}当前天气：{text}"
                return f"未能查询到 {city} 的天气信息，请确认城市名。"
            return f"天气服务不可用（HTTP {response.status_code}）"
    except Exception as e:
        logger.warning(f"天气查询失败: {e}")
        return f"天气查询失败：{str(e)}"


async def analyze_outfit(image_id: str, occasion: str = None, db=None) -> str:
    """穿搭分析：先查图片路径，再调 GLM-4V"""
    from models.date_spot import OutfitImage
    from sqlalchemy.orm import Session

    if db is None:
        return "穿搭分析需要登录后使用。"
    image = db.get(OutfitImage, int(image_id))
    if image is None:
        return f"未找到图片（id={image_id}），请先上传照片。"
    if not image.analysis_result:
        return "这张照片还没有分析结果，请先在上传页面发起分析。"
    return f"【{image.occasion or '通用场合'}穿搭分析】\n{image.analysis_result}"


async def make_date_plan(
    date_type: str, city: str, budget: str = None, preferences: str = None, db=None
) -> str:
    """生成约会方案：先用百度地图搜真实地点，再让 LLM 规划时间线"""
    from core.llm_client import call_llm

    # 用百度地图拿真实地点作为方案素材
    raw_req = f"帮我找{city}适合{date_type}约会的地方"
    if preferences:
        raw_req += f"，{preferences}"
    if budget:
        raw_req += f"，{budget}"

    result = await place_search(user_raw_request=raw_req, region=city, sort="relevance")
    pois = [normalize_poi(p, city) for p in result.get("results", []) if p.get("name")][:6]

    spots_text = "\n".join(
        f"- {s['name']}（{s['category']}，{s.get('price_level','')}，{s.get('address','')}）"
        for s in pois
    ) or "（百度地图暂无匹配地点，可结合常识推荐）"

    prompt = f"""请为用户生成一份完整的约会方案。
约会类型：{date_type}
城市：{city}
预算：{budget or '不限'}
用户偏好：{preferences or '无特别偏好'}

百度地图真实可选地点：
{spots_text}

要求：
1. 给出 3 个时间段安排（如 15:00-17:00 / 17:30-19:30 / 20:00-22:00）
2. 每个时段推荐 1 个具体地点（优先上面百度地图的真实地点）
3. 附 2 条约会小建议（如穿搭提醒、提前预约）
4. 附 1 个备选方案（天气不好时）
用 Markdown 分点输出。"""

    result_text = await call_llm(prompt, tier="plan", temperature=0.7, max_tokens=1200)
    return result_text


TOOL_FUNCTIONS = {
    "search_date_spots": search_date_spots,
    "get_weather": get_weather,
    "analyze_outfit": analyze_outfit,
    "make_date_plan": make_date_plan,
}
