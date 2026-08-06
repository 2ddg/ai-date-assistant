"""GLM-4V 视觉理解客户端：穿搭评价、照片分析"""
import base64
import logging

import httpx

from config import ZHIPU_API_KEY, LLM_API_URL, VISION_MODEL

logger = logging.getLogger(__name__)

OUTFIT_SYSTEM_PROMPT = """你是一位专业的形象顾问和穿搭专家。请根据用户上传的照片，从以下维度给出专业、友好、具体的穿搭评价：
1. 整体风格：判断穿搭风格类型（休闲/商务/约会/运动等），是否适合约会场合
2. 颜色搭配：分析主色调与配色和谐度，指出问题并给出改进建议
3. 单品细节：指出亮点单品和短板单品
4. 场合适配：评价是否适合所去的场合（如餐厅/公园/电影院）
5. 改进建议：给出 2-3 条具体的、可执行的搭配建议（换什么颜色、配什么单品）
要求：语气专业但不刻板，用中文回答，分点输出，每条建议具体可执行。"""


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


async def analyze_outfit(image_path: str, occasion: str = None) -> str:
    """调用 GLM-4V 分析穿搭照片"""
    if not ZHIPU_API_KEY:
        return "错误：未配置ZHIPU_API_KEY"

    image_data_url = f"data:image/jpeg;base64,{_encode_image(image_path)}"
    user_text = "请帮我评价一下这套穿搭。"
    if occasion:
        user_text += f"我打算去{occasion}。"
    user_text += "请从风格、颜色搭配、细节、场合适配和具体建议几个方面分析。"

    body = {
        "model": VISION_MODEL,
        "messages": [
            {"role": "system", "content": OUTFIT_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": image_data_url}},
                ],
            },
        ],
        "temperature": 0.6,
        "max_tokens": 1024,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                LLM_API_URL,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ZHIPU_API_KEY}"},
                json=body,
            )
            if response.status_code != 200:
                logger.error(f"视觉API错误: {response.status_code} {response.text[:200]}")
                return f"图片分析服务暂时不可用（错误码：{response.status_code}）"
            data = response.json()
            if "choices" not in data or not data["choices"]:
                return "视觉服务返回数据格式异常"
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        return "图片分析超时，请稍后再试"
    except Exception as e:
        logger.error(f"视觉调用异常: {str(e)}")
        return f"图片分析出错: {str(e)}"
