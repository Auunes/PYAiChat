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
                models.append({"id": channel.model_id, "name": channel.name})
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
            yield f"data: {json.dumps({'error': {'type': 'upstream_rate_limit', 'message': '问的人太多啦，换一个模型试试吧'}})}\n\n"
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
                    if response.status_code == 429:
                        yield f"data: {json.dumps({'error': {'type': 'upstream_rate_limit', 'message': '问的人太多啦，换一个模型试试吧'}})}\n\n"
                        return
                    if response.status_code != 200:
                        yield f"data: {json.dumps({'error': {'type': 'upstream_error', 'message': '上游渠道返回错误'}})}\n\n"
                        return

                    completion_text = ""
                    in_think = False  # 跟踪是否在 <think> 块内（如 Grok）
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                yield f"data: [DONE]\n\n"
                                break

                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    content = delta.get("content", "")

                                    # 处理 <think>...</think> 标签，转换为 reasoning_content
                                    if content and (in_think or "<think>" in content or "</think>" in content):
                                        reasoning_text = ""
                                        content_text = ""
                                        pos = 0
                                        while pos < len(content):
                                            if in_think:
                                                end = content.find("</think>", pos)
                                                if end != -1:
                                                    reasoning_text += content[pos:end]
                                                    pos = end + 8
                                                    in_think = False
                                                else:
                                                    reasoning_text += content[pos:]
                                                    pos = len(content)
                                            else:
                                                start = content.find("<think>", pos)
                                                if start != -1:
                                                    content_text += content[pos:start]
                                                    pos = start + 7
                                                    in_think = True
                                                else:
                                                    content_text += content[pos:]
                                                    pos = len(content)

                                        new_delta = {k: v for k, v in delta.items() if k != "content"}
                                        if reasoning_text:
                                            new_delta["reasoning_content"] = reasoning_text
                                        if content_text:
                                            new_delta["content"] = content_text
                                            completion_text += content_text

                                        if reasoning_text or content_text:
                                            chunk["choices"][0]["delta"] = new_delta
                                            yield f"data: {json.dumps(chunk)}\n\n"
                                        continue

                                    if content:
                                        completion_text += content
                            except:
                                pass

                            yield f"{line}\n\n"

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
