from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    base_url = Column(String(500), nullable=False)
    api_key = Column(Text, nullable=False)  # 明文存储
    model_id = Column(String(255), nullable=False)
    rpm_limit = Column(Integer, default=60)
    is_enabled = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0, nullable=False)  # 排序字段，数值越小越靠前
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
