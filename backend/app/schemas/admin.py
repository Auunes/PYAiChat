from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SystemConfigUpdate(BaseModel):
    guest_rpm: Optional[int] = Field(None, ge=1)
    user_rpm: Optional[int] = Field(None, ge=1)
    log_retention_days: Optional[int] = Field(None, ge=1)
    allow_registration: Optional[bool] = None


class SystemConfigResponse(BaseModel):
    guest_rpm: int
    user_rpm: int
    log_retention_days: int
    allow_registration: bool


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


class AdminProfileResponse(BaseModel):
    username: str


class AdminProfileUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3)
    current_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=6)
