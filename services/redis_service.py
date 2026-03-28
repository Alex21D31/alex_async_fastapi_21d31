import redis.asyncio as redis
from config import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
    async def close(self):
        await self.redis_client.aclose()

    async def add_to_blacklist(self,jti : str, expire_seconds : int):
        await self.redis_client.setex(name=jti, time=expire_seconds, value='true')
    async def is_blacklisted(self, jti : str) -> bool:
        token = await self.redis_client.get(jti)
        return token is not None
    
    async def ban_user(self, user_id : int):
        await self.redis_client.sadd('banned_users', str(user_id))
    async def is_banned(self, user_id : str) -> bool:
        return await self.redis_client.sismember('banned_users', user_id)
    async def unban_user(self, user_id : int):
        await self.redis_client.srem('banned_users', str(user_id))

    async def track_active_user(self, user_id : int, date_key : str):
        key = f'active_users:{date_key}'
        await self.redis_client.sadd(key, str(user_id))
        await self.redis_client.expireat(key, self._end_of_day())
    async def get_active_users_count(self, date_key : str) -> int:
        return await self.redis_client.scard(f'active_users:{date_key}')
    def _end_of_day(self) -> int:
        now = datetime.now(timezone.utc)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        return int(end.timestamp())
redis_service = RedisService()