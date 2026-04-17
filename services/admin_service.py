from repositories.order_repo import OrderRepository
from repositories.user_repo import UserRepository
from services.redis_service import redis_service
from fastapi import HTTPException
from models import User, Role, Status, Order
from datetime import datetime, timezone
import logging
logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self, user_repo : UserRepository, order_repo : OrderRepository):
        self.user_repo = user_repo
        self.order_repo = order_repo
        

        # ----- ВСЕ ФУНКЦИИ ДАННОГО СЕРВИСА ДОСТУПНЫ ТОЛЬКО ОТ РОЛИ ADMIN И ВЫШЕ! -----
        # ----- ЕСЛИ ВЫ ПОЛУЧАЕТЕ 403 ОШИБКУ, НО ЕЕ НЕТ В ФУНКЦИИ, ТО У ВАС НЕДОСТАТОЧНО ПРАВ!
        
    async def _get_user_or_404(self, user_id: int) -> User:
        """
        Вспомогательная функция получения пользователя по ID.

        Args:
            user_id: Айди пользователя
        
        Return:
            Объект User.

        Raises:
            HTTPException: 404, если пользователь не найден.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        return user
    async def get_all_users(self):
        """
        Поиск всех пользователей системы.
        """
        return  await self.user_repo.get_all()
    async def get_user_by_id(self, id : int):
        """
        Поиск пользователя по айди
        """
        return await self._get_user_or_404(id)
    async def change_role(self, id : int, role : Role):
        """
        Данная функция предназначена для выдачи ролей.
        Доступная только для Creator
        """
        user = await self._get_user_or_404(id)
        return await self.user_repo.update(user, {'role' : role})
    async def ban_user(self, id : int, token : dict):
        """
        Блокировка пользователя.
        Данная функция имеет несколько этапов проверки перед блокировокой, главные правила:
        1. Администратору нельзя заблокировать администратора или создателя (создатель - может).
        2. Нельзя заблокировать самого себя.
        После блокировки пользователь автоматически попадает в черный список Redis.
        С ролью Banned пользователю недоступны никакие функции внутри сервиса.

        Args:
            id: Айди пользователя, котрого необходимо заблокировать.
            token: данные из Access токена.

        Returns:
            Уведомление о блокировке.

        Raises:
            HTTPException: 403, если блокируешь админа\крейтера будучи админом или пользователь уже заблокирован.
            HTTPException: 400, если блокируешь сам себя.
            HTTPException: 404, если пользователя нет в базе данных. (через _get_user_or_404).
        """
        target = await self._get_user_or_404(id)
        if token['role'] == 'admin' and target.role.value in ['admin', 'creator']:
            raise HTTPException(status_code=403, detail='Недостаточно прав')
        if int(token['sub']) == id:
            raise HTTPException(status_code=400,detail='Нельзя заблокировать самого себя')
        if target.role == Role.banned:
            raise HTTPException(status_code=403, detail="Пользователь уже заблокирован")
        await self.user_repo.update(target, {'role' : Role.banned})
        try:
            await redis_service.ban_user(id)
        except Exception as e:
            logger.error(f"Ошибка при добавлении {id} в редис: {e}")
        return {'detail' : f"Пользователь с ID {id} успешно заблокирован"}
    async def user_unban(self, id : int, token : dict):
        """
        Разблокировка пользователя.
        Позволяет разблокировать забаненного пользователя.

        Args:
            id: Айди пользователя, котрого необходимо раззаблокировать.
            token: данные из Access токена.
        
        Returns:
            Уведомление о разблокировке.

        Raises:
            HTTPException: 400, если пытаешься разблокировать сам себя.
            HTTPException: 403, если пользователь не заблокирован
            HTTPException: 404, если пользователя нет в базе данных. (через _get_user_or_404).
        """
        target = await self._get_user_or_404(id)
        if int(token['sub']) == id:
            raise HTTPException(status_code=400,detail='Нельзя разблокировать самого себя')
        if target.role != Role.banned:
            raise HTTPException(status_code=403, detail="Пользователь не заблокирован.")
        await self.user_repo.update(target, {'role' : Role.user})
        try:
            await redis_service.unban_user(id)
        except Exception as e:
            logger.error(f"Ошибка при удалении {id} из редис: {e}")
        return {'detail' : f'Пользователь {id} успешно разблокирован'}
    async def get_all_orders(self):
        """
        Все заказы всех пользователей.
        """
        return await self.order_repo.get_all()
    async def get_statistics(self):
        """
        Посмотреть количество активных пользователей за сутки.
        """
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        count = await redis_service.get_active_users_count(today)
        return {'date': today, 'active_users': count}