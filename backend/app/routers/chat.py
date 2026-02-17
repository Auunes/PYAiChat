from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas import ChatCompletionRequest, ModelInfo, AnnouncementResponse
from app.services import ChatService, rate_limiter
from app.utils import decode_access_token
from app.config import settings
from app.models import Announcement
from typing import Optional, List
import json

router = APIRouter(prefix="/api/chat", tags=["聊天"])


async def get_current_user(request: Request, db: AsyncSession) -> tuple[Optional[int], Optional[str]]:
    """获取当前用户（可选）"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, None

    token = auth_header[7:]
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "user":
        return None, None

    user_id = int(payload.get("sub"))

    # 从数据库查询用户邮箱
    from app.models import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    username = user.email if user else None

    return user_id, username


async def check_user_rate_limit(request: Request, user_id: Optional[int]) -> bool:
    """检查用户限流"""
    ip_address = request.client.host

    if user_id:
        # 已登录用户
        key = f"user:{user_id}"
        limit = settings.USER_RPM
    else:
        # 游客
        key = f"ip:{ip_address}"
        limit = settings.GUEST_RPM

    allowed, retry_after = await rate_limiter.check_rate_limit(key, limit)
    if not allowed:
        error_response = {
            "error": {
                "type": "rate_limit_exceeded",
                "message": "您超过当前使用限制，请稍后再试",
                "retry_after": retry_after,
            }
        }
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=error_response,
        )
    return True


@router.get("/models", response_model=list[ModelInfo])
async def get_models(db: AsyncSession = Depends(get_db)):
    """获取可用模型列表"""
    return await ChatService.get_available_models(db)


@router.get("/announcement", response_model=Optional[AnnouncementResponse])
async def get_announcement(db: AsyncSession = Depends(get_db)):
    """获取启用的公告"""
    result = await db.execute(
        select(Announcement)
        .where(Announcement.is_enabled == True)
        .order_by(Announcement.created_at.desc())
        .limit(1)
    )
    announcement = result.scalar_one_or_none()
    return announcement


@router.post("/completions")
async def chat_completions(
    request: Request,
    chat_request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db),
):
    """聊天完成（流式）"""
    # 获取用户信息
    user_id, username = await get_current_user(request, db)

    # 检查用户限流
    await check_user_rate_limit(request, user_id)

    # 获取 IP 地址
    ip_address = request.client.host

    # 流式响应
    return StreamingResponse(
        ChatService.stream_chat_completion(
            db, chat_request, user_id, username, ip_address
        ),
        media_type="text/event-stream",
    )
