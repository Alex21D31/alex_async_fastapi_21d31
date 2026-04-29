from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Category

class CategoryRepository:
    def __init__(self,db : AsyncSession):
        self.db = db
    async def get_by_id(self,id : int) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == id))
        return result.scalar_one_or_none()
    async def get_by_name(self,name : str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.name == name))
        return result.scalar_one_or_none()
    async def get_all(self) -> list[Category]:
        result = await self.db.execute(select(Category))
        return result.scalars().all()
    async def save(self, category : Category) -> Category:
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
    async def delete(self, category : Category):
        await self.db.delete(category)
        await self.db.commit()