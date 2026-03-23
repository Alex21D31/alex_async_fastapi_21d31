from repositories.order_repo import OrderRepository
from repositories.product_repo import ProductRepository
from schemas import CreateOrder, UpdateOrder
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Order, OrderItem, Status

class OrderService:
    def __init__(self,order_repo: OrderRepository, product_repo: ProductRepository, db: AsyncSession):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.db = db
    async def _get_order_or_404(self, order_id: int) -> Order:
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail='Заказ не найден')
        return order
    async def create_order(self, user_id: int, data: CreateOrder) -> Order:
        order = Order(user_id=user_id, info=data.info)
        self.db.add(order)
        await self.db.flush()
        for item in data.items:
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(404, f'Товар {item.product_id} не найден')
            if product.quantity < item.quantity:
                raise HTTPException(400, f'Недостаточно товара {product.name} на складе')
            product.quantity -= item.quantity
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.db.add(order_item)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    async def get_all_orders(self, data : dict):
        result = await self.order_repo.get_all_orders_by_user(int(data['sub']))
        return result
    async def get_one_order(self, order_id : int, data : dict):
        result = await self.order_repo.get_by_id_for_user(order_id, int(data['sub']))
        if not result:
            raise HTTPException(404, 'Заказ не найден')
        return result
    async def update_order(self, order_id : int, patch_order : UpdateOrder):
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, patch_order.model_dump(exclude_none=True)) 
    async def delete_order(self, order_id):
        order = await self._get_order_or_404(order_id)
        await self.order_repo.delete(order)
        return f'Заказ под номером {order_id} успешно удален.'
    async def update_status(self, order_id : int, new_status : Status):
        order = await self._get_order_or_404(order_id)
        return await self.order_repo.update(order, {'status' : new_status})
