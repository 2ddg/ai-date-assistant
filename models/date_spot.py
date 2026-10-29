from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from database import Base


class OutfitImage(Base):
    """用户上传的穿搭照片"""

    __tablename__ = "outfit_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    file_path = Column(String(300), nullable=False)
    occasion = Column(String(50), default="", comment="场合：餐厅/公园/电影院...")
    analysis_result = Column(Text, default="", comment="GLM-4V 分析结果")
    created_at = Column(DateTime, default=datetime.now)
