from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Order, OrderItem
from sqlalchemy.orm import joinedload

class OrderRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int):
        """
        Один заказ из базы данных.
        
        Args:
            id: Айди заказа для поиска.

        Returns:
            Данные о заказе из базы.
        """
        result = await self.db.execute(select(Order).where(Order.id == id))
        return result.scalar_one_or_none()           
    async def get_all(self) -> list[Order]:
        """
        Все заказы из базы данных.

        Returns:
            список объектов Order.
        """
        result = await self.db.execute(select(Order))
        return result.scalars().all()  
    async def get_by_id_for_user(self, id : int, user_id : int) -> Order | None:
        """
        Поиск одного заказа для пользователя.
        Происходит путем поиска по заказу и пользователю. 

        Args:
            id: Айди заказа
            user_id: Айди пользователя
        
        Return:
            Заказ пользователя или None, если заказ не найден.
        """
        result = await self.db.execute(select(Order).where(Order.id == id, Order.user_id == user_id).options(joinedload(Order.items).joinedload(OrderItem.product)))
        return result.unique().scalar_one_or_none()
    async def get_all_orders_by_user(self, user_id : int):
        """
        Поиск всех заказов одного пользователя

        Args:
            user_id: Айди пользователя для поиска по базе.
        
        Returns:
            Все заказы пользователя.
        """
        result = await self.db.execute(select(Order).where(Order.user_id == user_id).options(joinedload(Order.items).joinedload(OrderItem.product)))
        return result.scalars().unique().all()
    async def save(self, order : Order) -> Order:
        """
        Сохранение заказа в базу данных.

        Args:
            prod: Экземпляр модели Order с данными для сохранения.

        Returns:
            Созданный объект заказа с заполенными системными полями
            (ID, статус)
        """
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    async def update(self, order : Order, update_data : dict) -> Order:
        """
        Обновление данных заказа. 
        
        Происходит через перебор словаря: изменяются только те поля, 
        которые переданы в update_data и не являются None.

        Args:
            prod: Экземпляр модели Order, который подлежит изменению.
            update_data: Словарь с новыми данными (info).

        Returns:
            Обновленный объект из базы данных.
        """
        for key,value in update_data.items():
            if value is not None:
                setattr(order,key,value)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    async def delete(self, order : Order) -> None:
        await self.db.delete(order)
        await self.db.commit()
        """
        Удаление заказа из базы данных.

        Args:
            prod: Экземпляр модели Order для удаления.
        """
