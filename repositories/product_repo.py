from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Product

class ProductRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_all(self) -> list[Product]:
        result = await self.db.execute(select(Product))
        return result.scalars().all()
    async def get_by_id(self, id : int) -> Product | None:
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()
    async def save(self, prod : Product) -> Product:
        self.db.add(prod)
        await self.db.commit()
        await self.db.refresh(prod)
        return prod
    async def update(self, prod : Product, data : dict) -> Product:
        for key,value in data.items():
            if value is not None:
                setattr(prod,key,value)
        await self.db.commit()
        await self.db.refresh(prod)
        return prod
    async def delete(self, prod : Product) -> None:
        await self.db.delete(prod)
        await self.db.commit()