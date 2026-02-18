from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from app.database import get_db
from app.models import Channel, SystemConfig, BlockedIP, ChatLog, Announcement
from app.schemas import (
    ChannelCreate,
    ChannelUpdate,
    ChannelResponse,
    SystemConfigUpdate,
    SystemConfigResponse,
    BlockedIPCreate,
    BlockedIPResponse,
    ChatLogResponse,
    StatsResponse,
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementResponse,
    AdminProfileResponse,
    AdminProfileUpdate,
)
from app.services import ChannelService
from app.utils import decode_access_token, is_ip_in_range
from app.config import settings
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter(prefix="/api/admin", tags=["管理员"])


async def verify_admin(request: Request):
    """验证管理员权限"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权",
        )

    token = auth_header[7:]
    payload = decode_access_token(token)
    if not payload or payload.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权",
        )
    return payload


# 渠道管理
@router.get("/channels", response_model=List[ChannelResponse])
async def get_channels(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """获取渠道列表"""
    channels = await ChannelService.get_channels(db)
    return channels


@router.post("/channels", response_model=ChannelResponse)
async def create_channel(
    channel_data: ChannelCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """创建渠道"""
    channel = await ChannelService.create_channel(db, channel_data)
    return channel


@router.post("/channels/test")
async def test_channel(
    channel_data: ChannelCreate,
    _: dict = Depends(verify_admin),
):
    """测试渠道连接"""
    result = await ChannelService.test_channel(channel_data)
    return result


@router.put("/channels/reorder")
async def reorder_channels(
    channel_orders: List[dict],
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """批量更新渠道顺序"""
    for item in channel_orders:
        channel_id = item.get("id")
        sort_order = item.get("sort_order")
        if channel_id and sort_order is not None:
            result = await db.execute(select(Channel).where(Channel.id == channel_id))
            channel = result.scalar_one_or_none()
            if channel:
                channel.sort_order = sort_order
    await db.commit()
    return {"message": "顺序更新成功"}


@router.put("/channels/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    channel_id: int,
    channel_data: ChannelUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """更新渠道"""
    channel = await ChannelService.update_channel(db, channel_id, channel_data)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="渠道不存在")
    return channel


@router.delete("/channels/{channel_id}")
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """删除渠道"""
    success = await ChannelService.delete_channel(db, channel_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="渠道不存在")
    return {"message": "删除成功"}


# 系统配置
@router.get("/config", response_model=SystemConfigResponse)
async def get_config(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """获取系统配置"""
    result = await db.execute(select(SystemConfig))
    configs = {config.key: config.value for config in result.scalars().all()}

    return SystemConfigResponse(
        guest_rpm=int(configs.get("guest_rpm", settings.GUEST_RPM)),
        user_rpm=int(configs.get("user_rpm", settings.USER_RPM)),
        log_retention_days=int(configs.get("log_retention_days", settings.LOG_RETENTION_DAYS)),
        allow_registration=configs.get("allow_registration", "true").lower() == "true",
    )


@router.put("/config", response_model=SystemConfigResponse)
async def update_config(
    config_data: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """更新系统配置"""
    update_data = config_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        config = result.scalar_one_or_none()

        if config:
            config.value = str(value)
        else:
            config = SystemConfig(key=key, value=str(value))
            db.add(config)

    await db.commit()
    return await get_config(db, _)


# IP 管理
@router.get("/blocked-ips", response_model=List[BlockedIPResponse])
async def get_blocked_ips(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """获取禁用 IP 列表"""
    result = await db.execute(select(BlockedIP))
    return result.scalars().all()


@router.post("/blocked-ips", response_model=BlockedIPResponse)
async def create_blocked_ip(
    ip_data: BlockedIPCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """添加禁用 IP"""
    blocked_ip = BlockedIP(
        ip_address=ip_data.ip_address,
        reason=ip_data.reason,
    )
    db.add(blocked_ip)
    await db.commit()
    await db.refresh(blocked_ip)
    return blocked_ip


@router.delete("/blocked-ips/{ip_id}")
async def delete_blocked_ip(
    ip_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """删除禁用 IP"""
    result = await db.execute(select(BlockedIP).where(BlockedIP.id == ip_id))
    blocked_ip = result.scalar_one_or_none()
    if not blocked_ip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IP 不存在")

    await db.delete(blocked_ip)
    await db.commit()
    return {"message": "删除成功"}


# 日志查询
@router.get("/logs", response_model=List[ChatLogResponse])
async def get_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    model_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """获取日志列表"""
    query = select(ChatLog).order_by(ChatLog.created_at.desc())

    # 筛选条件
    if start_date:
        query = query.where(ChatLog.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(ChatLog.created_at <= datetime.fromisoformat(end_date))
    if username:
        query = query.where(ChatLog.username.like(f"%{username}%"))
    if ip_address:
        query = query.where(ChatLog.ip_address == ip_address)
    if model_id:
        query = query.where(ChatLog.model_id == model_id)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/logs/export")
async def export_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """导出日志（CSV）"""
    query = select(ChatLog).order_by(ChatLog.created_at.desc())

    if start_date:
        query = query.where(ChatLog.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.where(ChatLog.created_at <= datetime.fromisoformat(end_date))

    result = await db.execute(query)
    logs = result.scalars().all()

    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "用户ID", "用户名", "IP地址", "渠道ID", "模型ID",
        "提问Tokens", "回答Tokens", "创建时间"
    ])

    for log in logs:
        writer.writerow([
            log.id,
            log.user_id or "",
            log.username or "",
            log.ip_address,
            log.channel_id or "",
            log.model_id,
            log.prompt_tokens or 0,
            log.completion_tokens or 0,
            log.created_at.isoformat(),
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chat_logs.csv"},
    )


# 统计数据
@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(verify_admin),
):
    """获取统计数据"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    # 今日/本周/本月调用量
    today_result = await db.execute(
        select(func.count(ChatLog.id)).where(ChatLog.created_at >= today_start)
    )
    today_calls = today_result.scalar() or 0

    week_result = await db.execute(
        select(func.count(ChatLog.id)).where(ChatLog.created_at >= week_start)
    )
    week_calls = week_result.scalar() or 0

    month_result = await db.execute(
        select(func.count(ChatLog.id)).where(ChatLog.created_at >= month_start)
    )
    month_calls = month_result.scalar() or 0

    # 模型使用占比
    model_result = await db.execute(
        select(ChatLog.model_id, func.count(ChatLog.id))
        .where(ChatLog.created_at >= month_start)
        .group_by(ChatLog.model_id)
    )
    model_distribution = {model: count for model, count in model_result.all()}

    # 调用趋势（最近7天）
    trend_data = []
    for i in range(7):
        day_start = today_start - timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        day_result = await db.execute(
            select(func.count(ChatLog.id)).where(
                and_(ChatLog.created_at >= day_start, ChatLog.created_at < day_end)
            )
        )
        count = day_result.scalar() or 0
        trend_data.append({"date": day_start.strftime("%Y-%m-%d"), "count": count})

    trend_data.reverse()

    # Token 消耗统计
    token_result = await db.execute(
        select(
            func.sum(ChatLog.prompt_tokens),
            func.sum(ChatLog.completion_tokens),
        ).where(ChatLog.created_at >= month_start)
    )
    prompt_tokens, completion_tokens = token_result.one()
    token_stats = {
        "prompt_tokens": prompt_tokens or 0,
        "completion_tokens": completion_tokens or 0,
        "total_tokens": (prompt_tokens or 0) + (completion_tokens or 0),
    }

    # 活跃用户数量
    active_users_result = await db.execute(
        select(func.count(func.distinct(ChatLog.user_id)))
        .where(and_(ChatLog.created_at >= month_start, ChatLog.user_id.isnot(None)))
    )
    active_users = active_users_result.scalar() or 0

    return StatsResponse(
        today_calls=today_calls,
        week_calls=week_calls,
        month_calls=month_calls,
        model_distribution=model_distribution,
        trend_data=trend_data,
        token_stats=token_stats,
        active_users=active_users,
    )


# ==================== 公告管理 ====================


@router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """获取所有公告"""
    result = await db.execute(select(Announcement).order_by(Announcement.created_at.desc()))
    announcements = result.scalars().all()
    return announcements


@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement_data: AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """创建公告"""
    announcement = Announcement(**announcement_data.model_dump())
    db.add(announcement)
    await db.commit()
    await db.refresh(announcement)
    return announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    announcement_data: AnnouncementUpdate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """更新公告"""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    update_data = announcement_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(announcement, key, value)

    await db.commit()
    await db.refresh(announcement)
    return announcement


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_admin),
):
    """删除公告"""
    result = await db.execute(select(Announcement).where(Announcement.id == announcement_id))
    announcement = result.scalar_one_or_none()
    if not announcement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="公告不存在")

    await db.delete(announcement)
    await db.commit()
    return {"message": "删除成功"}


# ==================== 管理员个人资料 ====================


@router.get("/profile", response_model=AdminProfileResponse)
async def get_admin_profile(
    admin: dict = Depends(verify_admin),
):
    """获取管理员个人资料"""
    return AdminProfileResponse(username=admin.get("sub", settings.ADMIN_USERNAME))


@router.put("/profile")
async def update_admin_profile(
    profile_data: AdminProfileUpdate,
    admin: dict = Depends(verify_admin),
):
    """更新管理员个人资料"""
    import os
    from dotenv import load_dotenv, set_key

    # 获取.env文件路径
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "..", ".env")

    # 验证当前密码（如果要修改密码）
    if profile_data.new_password:
        if not profile_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码需要提供当前密码"
            )
        if profile_data.current_password != settings.ADMIN_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="当前密码错误"
            )

    # 更新用户名
    if profile_data.username and profile_data.username != settings.ADMIN_USERNAME:
        if os.path.exists(env_path):
            set_key(env_path, "ADMIN_USERNAME", profile_data.username)
            settings.ADMIN_USERNAME = profile_data.username

    # 更新密码
    if profile_data.new_password:
        if os.path.exists(env_path):
            set_key(env_path, "ADMIN_PASSWORD", profile_data.new_password)
            settings.ADMIN_PASSWORD = profile_data.new_password

    return {"message": "更新成功，请重新登录"}
