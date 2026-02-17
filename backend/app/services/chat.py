from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Channel, ChatLog
from app.schemas import ChatCompletionRequest
from app.services.channel import ChannelService
from app.services.rate_limit import rate_limiter
from app.utils import estimate_tokens
from typing import Optional, AsyncGenerator
import httpx
import json
import time
import uuid


class ChatService:
    @staticmethod
    async def get_available_models(db: AsyncSession) -> list:
        """获取可用模型列表"""
        channels = await ChannelService.get_channels(db, enabled_only=True)
        models = []
        seen = set()
        for channel in channels:
            if channel.model_id not in seen:
                models.append({"id": channel.model_id, "name": channel.model_id})
                seen.add(channel.model_id)
        return models

    @staticmethod
    async def get_channel_for_model(db: AsyncSession, model_id: str) -> Optional[Channel]:
        """获取指定模型的可用渠道"""
        result = await db.execute(
            select(Channel)
            .where(Channel.model_id == model_id, Channel.is_enabled == True)
            .order_by(Channel.id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def stream_chat_completion(
        db: AsyncSession,
        request: ChatCompletionRequest,
        user_id: Optional[int],
        username: Optional[str],
        ip_address: str,
    ) -> AsyncGenerator[str, None]:
        """流式聊天完成"""
        # 获取渠道
        channel = await ChatService.get_channel_for_model(db, request.model)
        if not channel:
            yield f"data: {json.dumps({'error': {'type': 'model_not_found', 'message': '模型不可用'}})}\n\n"
            return

        # 检查渠道限流
        channel_key = f"channel:{channel.id}"
        allowed, retry_after = await rate_limiter.check_rate_limit(
            channel_key, channel.rpm_limit
        )
        if not allowed:
            yield f"data: {json.dumps({'error': {'type': 'upstream_error', 'message': '上游渠道暂时不可用，请稍后再试'}})}\n\n"
            return

        # 调用上游 API
        api_key = channel.api_key
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": request.model,
            "messages": [msg.model_dump() for msg in request.messages],
            "stream": True,
            "temperature": request.temperature,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        prompt_tokens = 0
        completion_tokens = 0

        # 估算 prompt tokens
        for msg in request.messages:
            prompt_tokens += estimate_tokens(msg.content)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{channel.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status_code != 200:
                        yield f"data: {json.dumps({'error': {'type': 'upstream_error', 'message': '上游渠道返回错误'}})}\n\n"
                        return

                    completion_text = ""
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield f"data: [DONE]\n\n"
                                break
                            yield f"{line}\n\n"

                            # 提取完成文本用于 token 估算
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        completion_text += delta["content"]
                            except:
                                pass

            # 估算 completion tokens
            completion_tokens = estimate_tokens(completion_text)

            # 记录日志
            log = ChatLog(
                user_id=user_id,
                username=username,
                ip_address=ip_address,
                channel_id=channel.id,
                model_id=request.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            db.add(log)
            await db.commit()

        except Exception as e:
            yield f"data: {json.dumps({'error': {'type': 'upstream_error', 'message': str(e)}})}\n\n"
