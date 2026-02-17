from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional
import asyncio


class RateLimiter:
    def __init__(self):
        # 存储限流数据：{key: [(timestamp, count)]}
        self._limits: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, key: str, limit: int, window: int = 60) -> tuple[bool, Optional[int]]:
        """
        检查是否超过限流
        :param key: 限流键（IP、用户ID、渠道ID等）
        :param limit: 限制次数
        :param window: 时间窗口（秒）
        :return: (是否允许, 重试等待时间)
        """
        async with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(seconds=window)

            # 清理过期记录
            self._limits[key] = [
                (ts, count) for ts, count in self._limits[key] if ts > cutoff
            ]

            # 计算当前窗口内的请求数
            current_count = sum(count for _, count in self._limits[key])

            if current_count >= limit:
                # 计算最早的请求何时过期
                if self._limits[key]:
                    oldest_ts = self._limits[key][0][0]
                    retry_after = int((oldest_ts + timedelta(seconds=window) - now).total_seconds())
                    return False, max(retry_after, 1)
                return False, window

            # 记录本次请求
            self._limits[key].append((now, 1))
            return True, None

    async def cleanup(self):
        """清理过期数据"""
        async with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=5)
            for key in list(self._limits.keys()):
                self._limits[key] = [
                    (ts, count) for ts, count in self._limits[key] if ts > cutoff
                ]
                if not self._limits[key]:
                    del self._limits[key]


# 全局限流器实例
rate_limiter = RateLimiter()
