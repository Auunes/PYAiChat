from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChannelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    base_url: str = Field(..., min_length=1)
    api_key: str = Field(..., min_length=1)
    model_id: str = Field(..., min_length=1, max_length=255)
    rpm_limit: int = Field(default=60, ge=1)
    is_enabled: bool = True


class ChannelCreate(ChannelBase):
    pass


class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    base_url: Optional[str] = Field(None, min_length=1)
    api_key: Optional[str] = Field(None, min_length=1)
    model_id: Optional[str] = Field(None, min_length=1, max_length=255)
    rpm_limit: Optional[int] = Field(None, ge=1)
    is_enabled: Optional[bool] = None


class ChannelResponse(BaseModel):
    id: int
    name: str
    base_url: str
    api_key: str
    model_id: str
    rpm_limit: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelInfo(BaseModel):
    id: str
    name: str
