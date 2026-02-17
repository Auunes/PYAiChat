from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SystemConfigUpdate(BaseModel):
    guest_rpm: Optional[int] = Field(None, ge=1)
    user_rpm: Optional[int] = Field(None, ge=1)
    log_retention_days: Optional[int] = Field(None, ge=1)


class SystemConfigResponse(BaseModel):
    guest_rpm: int
    user_rpm: int
    log_retention_days: int


class BlockedIPCreate(BaseModel):
    ip_address: str = Field(..., min_length=1)
    reason: Optional[str] = None


class BlockedIPResponse(BaseModel):
    id: int
    ip_address: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    ip_address: str
    channel_id: Optional[int]
    model_id: str
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    today_calls: int
    week_calls: int
    month_calls: int
    model_distribution: dict
    trend_data: List[dict]
    token_stats: dict
    active_users: int
