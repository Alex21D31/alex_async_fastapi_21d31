from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product

class ProductRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_all(self) -> list[Product]:
        """
        Все продукты из базы данных.

        Returns:
            список объектов Product.
        """
        result = await self.db.execute(select(Product))
        return result.scalars().all()
    async def get_by_id(self, id : int) -> Product | None:
        """
        Один продукт из базы данных.

        Args:
            id: Айди продукта, которого необходимо найти.
        
        Returns:
            объект Product или None, если продукт не найден.
        """
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()
    async def get_by_name(self,name : str) -> Product | None:
        """
        Один продукт из базы данных.

        Args:
            name: Название продукта, которого необходимо найти.
        
        Returns:
            объект Product или None, если продукт не найден.
        """
        result = await self.db.execute(select(Product).where(Product.name == name))
        return result.scalar_one_or_none()
    async def save(self, prod : Product) -> Product:
        """
        Сохранение продукта в базу данных.

        Args:
            prod: Экземпляр модели Product с данными для сохранения.

        Returns:
            Созданный объект продукта с заполенными системными полями
            (ID, дата создания)
        """
        self.db.add(prod)
        await self.db.commit()
        await self.db.refresh(prod)
        return prod
    async def update(self, prod : Product, update_data : dict) -> Product:
        """
        Обновление данных продукта. 
        
        Происходит через перебор словаря: изменяются только те поля, 
        которые переданы в update_data и не являются None.

        Args:
            prod: Экземпляр модели Product, который подлежит изменению.
            update_data: Словарь с новыми данными (name, description, price, quantity).

        Returns:
            Обновленный объект из базы данных с актуальной датой updated_at.
        """
        for key,value in update_data.items():
            if value is not None:
                setattr(prod,key,value)
        await self.db.commit()
        await self.db.refresh(prod)
        return prod
    async def delete(self, prod : Product) -> None:
        """
        Удаление продукта из базы данных.

        Args:
            prod: Экземпляр модели Product для удаления.
        """
        await self.db.delete(prod)
        await self.db.commit()