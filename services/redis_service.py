import redis.asyncio as redis
from config import settings

class RedisService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='redis',
            port=6379,
            decode_responses=True
        )
    async def add_to_blacklist(self,jti : str, expire_seconds : int):
        await self.redis_client.setex(name=jti, time=expire_seconds, value='true')
    async def is_blacklisted(self, jti : str) -> bool:
        token = await self.redis_client.get(jti)
        return token is not None
redis_service = RedisService()