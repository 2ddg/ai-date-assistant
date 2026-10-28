import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.agent import run_agent, run_agent_stream
from database import get_db
from models.chat import ChatMessage
from models.persona import Persona
from models.schemas import ChatRequest
from security import get_current_user_id

router = APIRouter(prefix="/api/chat", tags=["AI对话"])


@router.get("/history/{persona_id}")
async def get_history(
    persona_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.persona_id == persona_id)
        .order_by(ChatMessage.id)
        .limit(100)
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "time": m.created_at.isoformat()}
        for m in messages
    ]


@router.post("/send")
async def send_message(
    data: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    persona = db.get(Persona, data.persona_id)
    if persona is None:
        return {"answer": "人格不存在，请先选择一个人格。"}

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.persona_id == data.persona_id)
        .order_by(ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    history.reverse()
    history_data = [{"role": m.role, "content": m.content} for m in history]

    db.add(ChatMessage(user_id=user_id, persona_id=data.persona_id, role="user", content=data.message))
    db.commit()

    answer = await run_agent(
        user_message=data.message,
        conversation_history=history_data,
        persona=persona.to_dict(),
        db=db,
    )

    db.add(ChatMessage(user_id=user_id, persona_id=data.persona_id, role="assistant", content=answer))
    db.commit()

    return {"answer": answer, "persona": persona.name}


@router.post("/stream")
async def send_message_stream(
    data: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """SSE 流式对话"""
    persona = db.get(Persona, data.persona_id)
    if persona is None:
        async def _error():
            yield f"data: {json.dumps({'type': 'error', 'data': '人格不存在'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_error(), media_type="text/event-stream")

    # 关键：在返回流之前把 ORM 数据取出来，否则生成器执行时 session 已关闭
    persona_dict = persona.to_dict()

    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id, ChatMessage.persona_id == data.persona_id)
        .order_by(ChatMessage.id.desc())
        .limit(10)
        .all()
    )
    history.reverse()
    history_data = [{"role": m.role, "content": m.content} for m in history]

    db.add(ChatMessage(user_id=user_id, persona_id=data.persona_id, role="user", content=data.message))
    db.commit()

    async def event_stream():
        # 流式生成器在后台执行，请求的 db session 已关闭，必须用独立 session
        from database import SessionLocal
        stream_db = SessionLocal()
        try:
            full_answer = ""
            async for chunk in run_agent_stream(
                user_message=data.message,
                conversation_history=history_data,
                persona=persona_dict,
                db=stream_db,
            ):
                full_answer += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"
            stream_db.add(ChatMessage(user_id=user_id, persona_id=data.persona_id, role="assistant", content=full_answer))
            stream_db.commit()
        finally:
            stream_db.close()
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
