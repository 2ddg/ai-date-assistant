"""自研 ReAct Agent：Thought → Action → Observation 循环
实现思路与 LangChain Agent 一致：LLM 自主决策调用哪个工具，观察结果后继续推理，直到给出最终回答。
"""
import json
import logging
import re

from core.llm_client import call_llm
from core.tools import TOOL_DESCRIPTIONS, TOOL_FUNCTIONS
from config import AGENT_MAX_ITERATIONS, AGENT_MAX_RETRY

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """你是一个贴心的 AI 约会助手，性格开朗、幽默、有分寸。
你可以调用以下工具来帮助用户：

{tool_descriptions}

使用规则：
1. 当需要工具信息时，只输出一个 JSON 对象，格式：
{{"action": "工具名", "action_input": {{"参数名": "参数值"}}}}
2. 收到工具结果后，结合结果继续推理或给出最终回答
3. 如果工具结果不足，可以再次调用其他工具
4. 最终回答要口语化、自然、带一点幽默感，直接面向用户输出最终答案（不要输出JSON）
5. 工具都解决不了时，用你的常识直接回答用户"""


def _build_system_prompt(persona: dict = None) -> str:
    tool_desc = "\n".join(
        f"- {t['name']}: {t['description']}（参数: {t['parameters']}）"
        for t in TOOL_DESCRIPTIONS
    )
    base = AGENT_SYSTEM_PROMPT.format(tool_descriptions=tool_desc)
    if persona:
        base += f"""

【当前人格】
你是「{persona['name']}」，性格特点：{persona['personality']}
说话风格：{persona['speaking_style']}
人设背景：{persona['background'] or '无'}
请严格用这个人格的口吻回答用户。"""
    return base


def _parse_action(text: str):
    """从 LLM 输出中解析工具调用 JSON（容错：支持被自然语言包裹）"""
    text = text.strip()
    match = re.search(r"\{[^{}]*\"action\"[^{}]*\}", text)
    if match:
        try:
            data = json.loads(match.group())
            if "action" in data and "action_input" in data:
                return data["action"], data["action_input"]
        except json.JSONDecodeError:
            pass
    return None, None


async def run_agent(
    user_message: str,
    conversation_history: list,
    persona: dict = None,
    db=None,
) -> str:
    """执行 Agent 循环，返回最终回答"""
    system_prompt = _build_system_prompt(persona)

    history_text = "\n".join(
        f"{'用户' if h.get('role') == 'user' else '助手'}: {h.get('content', '')[:200]}"
        for h in conversation_history[-6:]
    )

    prompt = f"""【对话历史】
{history_text or '（无）'}

【用户最新消息】
{user_message}

请根据以上信息决定如何回应。"""

    for i in range(AGENT_MAX_ITERATIONS):
        response = await call_llm(
            prompt,
            tier="agent",
            temperature=0.5,
            max_tokens=800,
            system_prompt=system_prompt,
        )

        action, action_input = _parse_action(response)
        if action is None:
            return response.strip()

        func = TOOL_FUNCTIONS.get(action)
        if func is None:
            return f"抱歉，我还没有这个能力（未知工具：{action}），让我直接回答你：\n{response}"

        logger.info(f"Agent 调用工具: {action} 参数: {action_input}")
        observation = "工具执行失败"
        for attempt in range(AGENT_MAX_RETRY + 1):
            try:
                observation = await func(**action_input, db=db)
                break
            except Exception as e:
                logger.warning(f"工具 {action} 执行失败（第{attempt + 1}次）: {e}")
                observation = f"工具执行失败：{e}"

        prompt = (
            f"""【对话历史】
{history_text or '（无）'}

【用户最新消息】
{user_message}

【上一次思考】调用工具 {action}，参数 {action_input}

【工具结果】
{observation}

请根据工具结果继续。如果需要更多信息，再次输出工具调用JSON；否则给出最终回答。"""
        )

    return "抱歉，我思考太久了，请再问我一次～"


async def run_agent_stream(
    user_message: str,
    conversation_history: list,
    persona: dict = None,
    db=None,
):
    """Agent 流式版本：工具调用阶段静默执行，最终回答流式输出"""
    final_answer = await run_agent(user_message, conversation_history, persona, db)
    for chunk in _chunk_text(final_answer, size=4):
        yield chunk


def _chunk_text(text: str, size: int = 4):
    for i in range(0, len(text), size):
        yield text[i : i + size]
