"""Pydantic 请求/响应模型"""
from typing import Optional

from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class ChatRequest(BaseModel):
    persona_id: int
    message: str


class OutfitAnalyzeRequest(BaseModel):
    occasion: Optional[str] = ""
