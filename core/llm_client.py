"""智谱 GLM-4 系列 LLM 客户端：成本感知路由 + 流式输出"""
import json
import logging

import httpx

from config import ZHIPU_API_KEY, LLM_API_URL, COST_AWARE_MODELS

logger = logging.getLogger(__name__)

# 任务复杂度 → 模型档位
TIER_MAP = {
    "chat": "cheap",        # 人格闲聊回复
    "extract": "cheap",     # 工具参数提取
    "summarize": "cheap",   # 工具结果摘要
    "agent": "premium",     # Agent 推理（要选对工具，用强模型）
    "plan": "premium",      # 约会方案规划
    "outfit": "medium",     # 穿搭评价文本
}


def get_model(tier: str) -> str:
    model = COST_AWARE_MODELS.get(tier, COST_AWARE_MODELS["cheap"])
    return model


async def call_llm(
    prompt: str,
    tier: str = "chat",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: str = None,
) -> str:
    """非流式调用（带错误处理）"""
    if not ZHIPU_API_KEY:
        return "错误：未配置ZHIPU_API_KEY"

    model = get_model(tier)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                LLM_API_URL,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ZHIPU_API_KEY}"},
                json=body,
            )
            if response.status_code != 200:
                logger.error(f"LLM API错误: {response.status_code} {response.text[:200]}")
                return f"AI服务暂时不可用（错误码：{response.status_code}）"
            data = response.json()
            if "choices" not in data or not data["choices"]:
                return "AI服务返回数据格式异常"
            return data["choices"][0]["message"]["content"]
    except httpx.TimeoutException:
        return "AI响应超时，请稍后再试"
    except Exception as e:
        logger.error(f"LLM调用异常: {str(e)}")
        return f"AI服务出错: {str(e)}"


async def call_llm_stream(
    prompt: str,
    tier: str = "chat",
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: str = None,
):
    """流式调用（SSE）"""
    if not ZHIPU_API_KEY:
        yield "错误：未配置ZHIPU_API_KEY"
        return

    model = get_model(tier)
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                LLM_API_URL,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {ZHIPU_API_KEY}"},
                json=body,
            ) as response:
                if response.status_code != 200:
                    yield f"AI服务错误 (HTTP {response.status_code})"
                    return
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    raw = line[6:]
                    if raw.strip() == "[DONE]":
                        return
                    try:
                        data = json.loads(raw)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except httpx.TimeoutException:
        yield "AI响应超时，请稍后再试"
    except Exception as e:
        yield f"流式调用出错: {str(e)}"
