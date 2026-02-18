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


async def get_real_ip(request: Request) -> str:
    """获取真实IP地址（支持反向代理和CDN）"""
    # 1. Cloudflare 专用头（最可靠）
    cf_connecting_ip = request.headers.get("CF-Connecting-IP")
    if cf_connecting_ip:
        return cf_connecting_ip.strip()

    # 2. 其他CDN常用头
    true_client_ip = request.headers.get("True-Client-IP")
    if true_client_ip:
        return true_client_ip.strip()

    # 3. X-Forwarded-For（标准代理头，取第一个IP）
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 取第一个IP（真实客户端IP）
        return forwarded_for.split(",")[0].strip()

    # 4. X-Real-IP（Nginx常用）
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # 5. 最后使用直连IP
    return request.client.host


async def check_user_rate_limit(request: Request, user_id: Optional[int], db: AsyncSession) -> bool:
    """检查用户限流"""
    ip_address = await get_real_ip(request)

    # 从数据库读取限流配置
    from app.models import SystemConfig
    result = await db.execute(select(SystemConfig))
    configs = {config.key: config.value for config in result.scalars().all()}

    if user_id:
        # 已登录用户
        key = f"user:{user_id}"
        limit = int(configs.get("user_rpm", settings.USER_RPM))
    else:
        # 游客
        key = f"ip:{ip_address}"
        limit = int(configs.get("guest_rpm", settings.GUEST_RPM))

    allowed, retry_after = await rate_limiter.check_rate_limit(key, limit)
    if not allowed:
        error_response = {
            "error": {
                "type": "user_rate_limit",
                "message": "提问速度太快啦～请休息一下，稍后再尝试。",
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
    await check_user_rate_limit(request, user_id, db)

    # 获取真实 IP 地址
    ip_address = await get_real_ip(request)

    # 流式响应
    return StreamingResponse(
        ChatService.stream_chat_completion(
            db, chat_request, user_id, username, ip_address
        ),
        media_type="text/event-stream",
    )
