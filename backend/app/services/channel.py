from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Channel
from app.schemas import ChannelCreate, ChannelUpdate
from app.utils import encrypt_api_key, decrypt_api_key
from typing import List, Optional


class ChannelService:
    @staticmethod
    async def get_channels(db: AsyncSession, enabled_only: bool = False) -> List[Channel]:
        """获取渠道列表"""
        query = select(Channel)
        if enabled_only:
            query = query.where(Channel.is_enabled == True)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_channel(db: AsyncSession, channel_id: int) -> Optional[Channel]:
        """获取单个渠道"""
        result = await db.execute(select(Channel).where(Channel.id == channel_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_channel(db: AsyncSession, channel_data: ChannelCreate) -> Channel:
        """创建渠道"""
        # 加密 API Key
        encrypted_key = encrypt_api_key(channel_data.api_key)

        channel = Channel(
            name=channel_data.name,
            base_url=channel_data.base_url,
            api_key=encrypted_key,
            model_id=channel_data.model_id,
            rpm_limit=channel_data.rpm_limit,
            is_enabled=channel_data.is_enabled,
        )
        db.add(channel)
        await db.commit()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def update_channel(
        db: AsyncSession, channel_id: int, channel_data: ChannelUpdate
    ) -> Optional[Channel]:
        """更新渠道"""
        result = await db.execute(select(Channel).where(Channel.id == channel_id))
        channel = result.scalar_one_or_none()
        if not channel:
            return None

        # 更新字段
        update_data = channel_data.model_dump(exclude_unset=True)
        if "api_key" in update_data:
            update_data["api_key"] = encrypt_api_key(update_data["api_key"])

        for key, value in update_data.items():
            setattr(channel, key, value)

        await db.commit()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def delete_channel(db: AsyncSession, channel_id: int) -> bool:
        """删除渠道"""
        result = await db.execute(select(Channel).where(Channel.id == channel_id))
        channel = result.scalar_one_or_none()
        if not channel:
            return False

        await db.delete(channel)
        await db.commit()
        return True

    @staticmethod
    def get_decrypted_api_key(channel: Channel) -> str:
        """获取解密后的 API Key"""
        return decrypt_api_key(channel.api_key)
