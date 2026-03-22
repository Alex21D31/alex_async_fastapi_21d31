from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Order, OrderItem
from sqlalchemy.orm import joinedload

class OrderRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int):
        result = await self.db.execute(select(Order).where(Order.id == id))
        return result            
    async def get_all(self):
        result = await self.db.execute(select(Order))
        return result.scalars().all()  
    async def get_by_id_for_user(self, id : int, user_id : int) -> Order | None:
        result = await self.db.execute(select(Order).where(Order.id == id, Order.user_id == user_id).options(joinedload(Order.items).joinedload(OrderItem.product)))
        return result.scalar_one_or_none()
    async def get_all_orders_by_user(self, user_id : int):
        result = await self.db.execute(select(Order).where(Order.user_id == user_id).options(joinedload(Order.items).joinedload(OrderItem.product)))
        return result.scalars().unique().all()
    async def save(self, order : Order) -> Order:
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    async def update(self, order : Order, data : dict) -> Order:
        for key,value in data.items():
            if value is not None:
                setattr(order,key,value)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    async def delete(self, order : Order) -> None:
        await self.db.delete(order)
        await self.db.commit()
    async def get_by_user_id(self,id : int) -> list[Order]:
        result = await self.db.execute(select(Order).where(Order.user_id == id).options(joinedload(Order.items).joinedload(OrderItem.product)))
        return result.scalars().unique().all()
    