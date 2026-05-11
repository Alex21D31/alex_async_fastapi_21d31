from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ShopProduct, Product, Shop

class ShopProductRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int) -> ShopProduct | None:
        result = await self.db.execute(select(ShopProduct).where(ShopProduct.id == id))
        return result.scalar_one_or_none()
    async def get_by_product_name(self, name : str) -> list[ShopProduct] | None:
        result = await self.db.execute(select(ShopProduct).join(Product, ShopProduct.product_id == Product.id).where(Product.name == name))
        return result.scalars().all()
    async def get_all_products_by_shop(self, shop_name : str) -> list[ShopProduct]:
        result = await self.db.execute(select(ShopProduct).join(Shop, ShopProduct.shop_id == Shop.id).where(Shop.name == shop_name))
        return result.scalars().all()
    async def save(self, shop_product : ShopProduct) -> ShopProduct:
        self.db.add(shop_product)
        await self.db.commit()
        await self.db.refresh(shop_product)
        return shop_product
    async def update(self, shop_product : ShopProduct, update_data : dict) -> ShopProduct:
        for key,value in update_data.items():
            if value is not None:
                setattr(shop_product,key,value)
        await self.db.commit()
        await self.db.refresh(shop_product)
        return shop_product
    async def delete(self, shop_product : ShopProduct):
        await self.db.delete(shop_product)
        await self.db.commit()