from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Channel
from app.schemas import ChannelCreate, ChannelUpdate
from typing import List, Optional, Dict
import httpx
import asyncio


class ChannelService:
    @staticmethod
    async def get_channels(db: AsyncSession, enabled_only: bool = False) -> List[Channel]:
        """获取渠道列表"""
        query = select(Channel).order_by(Channel.sort_order, Channel.id)
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
        channel = Channel(
            name=channel_data.name,
            base_url=channel_data.base_url,
            api_key=channel_data.api_key,
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
    async def test_channel(channel_data: ChannelCreate) -> Dict[str, any]:
        """测试渠道连接"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 构建测试请求
                headers = {
                    "Authorization": f"Bearer {channel_data.api_key}",
                    "Content-Type": "application/json",
                }

                # 发送一个简单的测试请求
                payload = {
                    "model": channel_data.model_id,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 5,
                }

                # 确保base_url正确拼接
                base_url = channel_data.base_url.rstrip("/")
                if not base_url.endswith("/chat/completions"):
                    if base_url.endswith("/v1"):
                        url = base_url + "/chat/completions"
                    else:
                        url = base_url + "/v1/chat/completions"
                else:
                    url = base_url

                response = await client.post(url, json=payload, headers=headers)

                if response.status_code == 200:
                    return {"success": True, "message": "连接成功"}
                else:
                    return {
                        "success": False,
                        "message": f"连接失败: HTTP {response.status_code} - {response.text[:200]}",
                    }
        except httpx.TimeoutException:
            return {"success": False, "message": "连接超时"}
        except Exception as e:
            return {"success": False, "message": f"连接失败: {str(e)}"}
