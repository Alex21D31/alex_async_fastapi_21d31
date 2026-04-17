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
        """
        Добавление JTI в черный список.

        Используется при логаауте.
        Токен после этого действия явялется недействительным.

        Args:
            jti: уникальный идентификатор токена.
            expire_seconds: Оставшее время действия токена.
        """
        await self.redis_client.setex(name=jti, time=expire_seconds, value='true')
    async def is_blacklisted(self, jti : str) -> bool:
        """
        Проверка токена на нахождение в черном списке.
        Используется для пропуска пользователя к дальнейшим функциям.
        Проверяется при каждом запросе.

        Args:
            jti уникальный идентификатор токена.

        Returns:
            True если токен найден в Redis, иначе False.
        """
        token = await self.redis_client.get(jti)
        return token is not None
    
    async def ban_user(self, user_id : int):
        """
        Процесс блокировки пользователя.
        Айди вносится в множество заблокированных пользователей.
        После этого действия пользователь больше не сможет попасть в систему до разблокировки.
        """
        await self.redis_client.sadd('banned_users', str(user_id))
    async def is_banned(self, user_id : str) -> bool:
        """
        Проверка, находится ли пользователь в списке заблокированных.
        Срабатывает при каждом запросе, который требует аутентификации внутри системы.
        """
        return await self.redis_client.sismember('banned_users', user_id)
    async def unban_user(self, user_id : int):
        """
        Функция разблокировки пользователя в системе.
        Удаляет его айди из списка заблокированных.
        После чего он сможет зайти в систему под старыми данными.
        """
        await self.redis_client.srem('banned_users', str(user_id))

    async def track_active_user(self, user_id : int, date_key : str):
        """
        Функция занесение пользователя во множество активных.
        Срабатывает при логине
        """
        key = f'active_users:{date_key}'
        await self.redis_client.sadd(key, str(user_id))
        await self.redis_client.expireat(key, self._end_of_day())
    async def get_active_users_count(self, date_key : str) -> int:
        """
        Вывод активности на сервере.
        Показывае число пользователей, что залогинились в сервис за сутки.
        При каждом логине число пользователей увеличивается.
        Срабатывает лишь на уникальные айди, вход с одного айди несколько раз не засчитывается.
        Число обнуляется каждые сутки.
        """
        return await self.redis_client.scard(f'active_users:{date_key}')
    def _end_of_day(self) -> int:
        """
        Внутренний метод, вспомогательный для функции track_active_user.
        Предназначен для определении времени, когда необходимо обнулить список активных пользователей.
        """
        now = datetime.now(timezone.utc)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0)
        return int(end.timestamp())
redis_service = RedisService()