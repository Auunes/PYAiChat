from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)  # 可为空（游客）
    username = Column(String(255))  # 用户邮箱或标识
    ip_address = Column(String(255), nullable=False, index=True)
    channel_id = Column(Integer)
    model_id = Column(String(255), nullable=False)
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
