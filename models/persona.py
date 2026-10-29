from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Persona(Base):
    """AI 人格档案"""

    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    personality = Column(String(500), nullable=False, comment="性格特点")
    speaking_style = Column(String(500), nullable=False, comment="说话风格")
    background = Column(String(500), default="", comment="人设背景")
    created_at = Column(DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "personality": self.personality,
            "speaking_style": self.speaking_style,
            "background": self.background,
        }
