from repositories.order_repo import OrderRepository
from repositories.user_repo import UserRepository
from fastapi import HTTPException
from models import User, Role, Status, Order

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
        if token['role'] == 'admin' and target.role.value in ['admin', 'creater']:
            raise HTTPException(status_code=403, detail='Недостаточно прав')
        if int(token['sub']) == id:
            raise HTTPException(status_code=400,detail='Нельзя заблокировать самого себя')
        return await self.user_repo.update(target, {'role' : Role.banned})
    async def get_all_orders(self):
        return await self.order_repo.get_all()
    async def update_order_status(self, order_id : int, new_status : Status):
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, {'status' : new_status})
