"""
ChatFlow - Redis Configuration & Manager
"""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings


class RedisManager:
    """Redis connection manager for caching and pub/sub."""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await self.redis.ping()

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        if self.redis:
            return await self.redis.get(key)
        return None

    async def set(
        self, key: str, value: str, expire: Optional[int] = None
    ) -> None:
        """Set a value in Redis."""
        if self.redis:
            await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        if self.redis:
            await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if self.redis:
            return await self.redis.exists(key) > 0
        return False

    async def set_json(
        self, key: str, value: Any, expire: Optional[int] = None
    ) -> None:
        """Set a JSON value in Redis."""
        await self.set(key, json.dumps(value), expire)

    async def get_json(self, key: str) -> Optional[Any]:
        """Get a JSON value from Redis."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None

    # =========================================
    # Online Status Management
    # =========================================

    async def set_user_online(self, user_id: str) -> None:
        """Mark a user as online."""
        await self.set(f"user:online:{user_id}", "1", expire=300)  # 5 minutes

    async def set_user_offline(self, user_id: str) -> None:
        """Mark a user as offline."""
        await self.delete(f"user:online:{user_id}")

    async def is_user_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return await self.exists(f"user:online:{user_id}")

    async def get_online_users(self, user_ids: list[str]) -> list[str]:
        """Get list of online users from given user IDs."""
        online_users = []
        for user_id in user_ids:
            if await self.is_user_online(user_id):
                online_users.append(user_id)
        return online_users

    # =========================================
    # Typing Status
    # =========================================

    async def set_user_typing(
        self, user_id: str, chat_id: str, is_typing: bool = True
    ) -> None:
        """Set user typing status in a chat."""
        key = f"typing:{chat_id}:{user_id}"
        if is_typing:
            await self.set(key, "1", expire=5)  # 5 seconds
        else:
            await self.delete(key)

    async def get_typing_users(self, chat_id: str) -> list[str]:
        """Get users currently typing in a chat."""
        if self.redis:
            keys = await self.redis.keys(f"typing:{chat_id}:*")
            return [key.split(":")[-1] for key in keys]
        return []

    # =========================================
    # Pub/Sub for Real-time Messages
    # =========================================

    async def publish(self, channel: str, message: dict) -> None:
        """Publish a message to a channel."""
        if self.redis:
            await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str) -> redis.client.PubSub:
        """Subscribe to a channel."""
        if self.redis:
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(channel)
            return self.pubsub
        raise RuntimeError("Redis not connected")

    # =========================================
    # Rate Limiting
    # =========================================

    async def check_rate_limit(
        self, key: str, limit: int, window: int
    ) -> tuple[bool, int]:
        """Check rate limit. Returns (is_allowed, remaining)."""
        if self.redis:
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, window)
            remaining = max(0, limit - current)
            return current <= limit, remaining
        return True, limit

    # =========================================
    # Unread Messages Counter
    # =========================================

    async def increment_unread(self, user_id: str, chat_id: str) -> int:
        """Increment unread message counter."""
        if self.redis:
            return await self.redis.hincrby(f"unread:{user_id}", chat_id, 1)
        return 0

    async def clear_unread(self, user_id: str, chat_id: str) -> None:
        """Clear unread messages for a chat."""
        if self.redis:
            await self.redis.hdel(f"unread:{user_id}", chat_id)

    async def get_unread_counts(self, user_id: str) -> dict[str, int]:
        """Get all unread counts for a user."""
        if self.redis:
            counts = await self.redis.hgetall(f"unread:{user_id}")
            return {k: int(v) for k, v in counts.items()}
        return {}


# Global Redis manager instance
redis_manager = RedisManager()


async def get_redis() -> RedisManager:
    """Dependency to get Redis manager."""
    return redis_manager

