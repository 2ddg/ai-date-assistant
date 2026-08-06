"""百度地图 Agent Plan 客户端：真实 POI 检索 + 地理编码"""
import logging
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BAIDU_MAP_AUTH_TOKEN = os.getenv("BAIDU_MAP_AUTH_TOKEN", "")
BASE_URL = "https://api.map.baidu.com"
HEADERS = {"Authorization": f"Bearer {BAIDU_MAP_AUTH_TOKEN}"}


def _has_token() -> bool:
    if not BAIDU_MAP_AUTH_TOKEN:
        logger.error("BAIDU_MAP_AUTH_TOKEN 未配置，请到 https://lbs.baidu.com/apiconsole/agentplan 申请")
        return False
    return True


async def place_search(user_raw_request: str, region: str, sort: str = "relevance", center: str = "") -> dict:
    """语义化 AI 地点检索：返回真实 POI（地址/电话/评分/评论/图片/经纬度）

    Args:
        user_raw_request: 用户完整原始需求，保留定语/约束词，如"帮我找三里屯附近评分最高可带宠物的咖啡馆"
        region: 城市或区域限制，如"北京市"、"成都市"
        sort: relevance（默认，按相关性）或 distance（按距离，需传 center）
        center: 检索中心点 "lat,lng"（gcj02），sort=distance 时必传

    Returns:
        百度地图 API 原始响应 dict，包含 results 和 resource_key
    """
    if not _has_token():
        return {"message": "error", "results": [], "error": "BAIDU_MAP_AUTH_TOKEN 未配置"}

    params = {
        "user_raw_request": user_raw_request,
        "region": region,
        "sort": sort,
    }
    if center:
        params["center"] = center

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{BASE_URL}/agent_plan/v1/place",
                headers=HEADERS,
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"百度地图 place 检索成功：{len(data.get('results', []))} 条结果")
            return data
    except Exception as e:
        logger.error(f"百度地图 place 检索失败: {e}")
        return {"message": "error", "results": [], "error": str(e)}


async def geocode(address: str, region: str = "") -> dict:
    """地理编码：地址 -> 经纬度"""
    if not _has_token():
        return {"message": "error", "error": "BAIDU_MAP_AUTH_TOKEN 未配置"}

    params = {"address": address}
    if region:
        params["region"] = region

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                f"{BASE_URL}/agent_plan/v1/geocoding",
                headers=HEADERS,
                params=params,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        logger.error(f"百度地图 geocoding 失败: {e}")
        return {"message": "error", "error": str(e)}


def map_render_url(resource_key: str) -> str:
    """生成地图展示链接（前端打开即可看可视化地图）"""
    return f"https://lbs.baidu.com/mapstatic/agentui_resource.html?resource_key={resource_key}"


def normalize_poi(poi: dict, city: str = "") -> dict:
    """把百度地图 POI 标准化为前端卡片需要的格式"""
    detail = poi.get("detail_info") or {}
    comments = poi.get("comments") or []
    # 取最高评分
    overall_rating = ""
    if comments:
        ratings = [c.get("overall_rating") for c in comments if c.get("overall_rating")]
        if ratings:
            overall_rating = f"{sum(ratings) / len(ratings):.1f}"

    # 分类标签
    classified = poi.get("classified_poi_tag", "") or ""
    tags_raw = [t for t in classified.replace("；", ";").replace(";", ",").split(",") if t.strip()]
    tags = ",".join(tags_raw[:4]) if tags_raw else (poi.get("category", "") or "")

    # 图片
    image_url = detail.get("image") or (comments[0].get("images", [None])[0] if comments and comments[0].get("images") else "")
    if isinstance(image_url, list):
        image_url = image_url[0] if image_url else ""

    # 价格等级（百度地图没有标准价格字段，根据 comment 内容粗略推断）
    price_level = "¥¥"
    if detail.get("avg_price"):
        price_level = f"人均¥{detail['avg_price']}"
    else:
        price_level = "¥¥"

    return {
        "name": poi.get("name", ""),
        "category": tags_raw[0] if tags_raw else "其他",
        "city": poi.get("city", city),
        "area": poi.get("area", ""),
        "address": poi.get("address", ""),
        "description": _build_description(poi, comments),
        "price_level": price_level,
        "tags": tags,
        "image_url": image_url or "",
        "overall_rating": overall_rating,
        "comment_num": detail.get("comment_num", ""),
        "phone": detail.get("telephone", "") or poi.get("telephone", ""),
        "lat": poi.get("location", {}).get("lat", ""),
        "lng": poi.get("location", {}).get("lng", ""),
        "detail_url": detail.get("detail_url", ""),
        "is_real_poi": True,  # 标识这是真实地图 POI
    }


def _build_description(poi: dict, comments: list) -> str:
    """从评论里提取一段简短描述"""
    if comments:
        # 取第一条评论的前 80 字
        c = comments[0].get("content", "")
        if c:
            return c[:80] + ("..." if len(c) > 80 else "")
    classified = poi.get("classified_poi_tag", "")
    brand = (poi.get("detail_info") or {}).get("brand", "")
    parts = [p for p in [brand, classified, poi.get("area", "")] if p]
    return " · ".join(parts) if parts else poi.get("address", "")
