from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Shop

class ShopRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int) -> Shop | None:
        result = await self.db.execute(select(Shop).where(Shop.id == id))
        return result.scalar_one_or_none()
    async def get_by_seller_id(self, seller_id : int) -> Shop | None:
        result = await self.db.execute(select(Shop).where(Shop.seller_id == seller_id))
        return result.scalar_one_or_none()
    async def get_all_verified(self) -> list[Shop]:
        result = await self.db.execute(select(Shop).where(Shop.is_verified == True))
        return result.scalars().all()
    async def save_shop(self, data : Shop) -> Shop:
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)
        return data
    async def update_shop(self, shop : Shop, update_shop : dict) -> Shop:
        for key,value in update_shop.items():
            if value is not None:
                setattr(shop, key,value)
        await self.db.commit()
        await self.db.refresh(shop)
        return shop
    async def delete_shop(self, shop : Shop):
        await self.db.delete(shop)
        await self.db.commit()
    async def set_verified(self, shop : Shop, new_status : bool) -> Shop:
        shop.is_verified = new_status
        await self.db.commit()
        await self.db.refresh(shop)
        return shop