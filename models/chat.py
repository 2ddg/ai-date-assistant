from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from database import Base


class ChatMessage(Base):
    """与 AI 人格的对话记录"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, comment="user/assistant")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
