from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    nickname = Column(String(50), default="")
    created_at = Column(DateTime, default=datetime.now)
