from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from core.baidu_map_client import place_search, map_render_url, normalize_poi
from security import get_current_user_id

router = APIRouter(prefix="/api/spots", tags=["约会地点"])


class AiRecommendRequest(BaseModel):
    city: str = Field(..., description="城市，如：成都、北京、上海")
    categories: list[str] = Field(default_factory=list, description="场景/分类")
    tags: list[str] = Field(default_factory=list, description="标签偏好")
    budget: str = Field("", description="预算")
    extra: str = Field("", description="额外偏好，如‘三里屯附近’")
    center: str = Field("", description="检索中心点 lat,lng（可选，用于距离排序）")


def _build_raw_request(req: AiRecommendRequest) -> str:
    """把结构化需求拼成百度地图能理解的自然语言查询"""
    parts = []
    if req.categories:
        parts.append("、".join(req.categories))
    if req.tags:
        parts.append("偏好" + "、".join(req.tags))
    if req.budget:
        parts.append(req.budget)
    if req.extra:
        parts.append(req.extra)

    if parts:
        return f"帮我找{req.city}适合约会的地方，" + "，".join(parts)
    return f"帮我找{req.city}适合约会的好去处"


@router.post("/ai-recommend")
async def ai_recommend(
    req: AiRecommendRequest,
    user_id: int = Depends(get_current_user_id),
):
    """基于真实百度地图 POI 的约会地点推荐

    调用百度地图 Agent Plan place 接口，返回带真实地址/电话/评分/评论/经纬度的地点。
    """
    user_raw_request = _build_raw_request(req)
    sort = "distance" if req.center else "relevance"

    result = await place_search(
        user_raw_request=user_raw_request,
        region=req.city,
        sort=sort,
        center=req.center or "",
    )

    if result.get("message") != "ok" and not result.get("results"):
        return {
            "spots": [],
            "resource_key": "",
            "map_url": "",
            "error": result.get("error") or result.get("message", "未知错误"),
            "raw_request": user_raw_request,
        }

    pois = result.get("results", [])
    spots = [normalize_poi(p, req.city) for p in pois if p.get("name")]

    resource_key = result.get("resource_key", "")
    return {
        "spots": spots,
        "resource_key": resource_key,
        "map_url": map_render_url(resource_key) if resource_key else "",
        "raw_request": user_raw_request,
        "source": "baidu_map",
    }


@router.post("/map-view")
async def get_map_view(
    req: AiRecommendRequest,
    user_id: int = Depends(get_current_user_id),
):
    """单独获取地图展示链接（调一次 place 拿 resource_key）"""
    user_raw_request = _build_raw_request(req)
    result = await place_search(
        user_raw_request=user_raw_request,
        region=req.city,
        sort="relevance",
    )
    resource_key = result.get("resource_key", "")
    return {
        "resource_key": resource_key,
        "map_url": map_render_url(resource_key) if resource_key else "",
    }
