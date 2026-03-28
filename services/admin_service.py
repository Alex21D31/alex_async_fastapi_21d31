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
    async def _get_user_or_404(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        return user
    async def _get_order_or_404(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail='Продукт не найден')
        return order
    async def get_all_users(self):
        return  await self.user_repo.get_all()
    async def get_user_by_id(self, id : int):
        return await self._get_user_or_404(id)
    async def change_role(self, id : int, role : Role):
        user = await self._get_user_or_404(id)
        return await self.user_repo.update(user, {'role' : role})
    async def ban_user(self, id : int, token : dict):
        target = await self._get_user_or_404(id)
        if token['role'] == 'admin' and target.role.value in ['admin', 'creator']:
            raise HTTPException(status_code=403, detail='Недостаточно прав')
        if int(token['sub']) == id:
            raise HTTPException(status_code=400,detail='Нельзя заблокировать самого себя')
        await self.user_repo.update(target, {'role' : Role.banned})
        try:
            await redis_service.ban_user(id)
        except Exception as e:
            logger.error(f"Ошибка при добавлении {id} в редис: {e}")
        return {'detail' : f"Пользователь с ID {id} успешно заблокирован"}
    async def user_unban(self, id : int, token : dict):
        target = await self._get_user_or_404(id)
        if int(token['sub']) == id:
            raise HTTPException(status_code=400,detail='Нельзя разблокировать самого себя')
        await self.user_repo.update(target, {'role' : Role.user})
        try:
            await redis_service.unban_user(id)
        except Exception as e:
            logger.error(f"Ошибка при удалении {id} из редис: {e}")
        return {'detail' : f'Пользователь {id} успешно разблокирован'}
    async def get_all_orders(self):
        return await self.order_repo.get_all()
    async def update_order_status(self, order_id : int, new_status : Status):
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, {'status' : new_status})
    async def get_statistics(self):
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        count = await redis_service.get_active_users_count(today)
        return {'date': today, 'active_users': count}