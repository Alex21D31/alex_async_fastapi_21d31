from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import ShopProduct, Product, Shop

class ShopProductRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def _get_shop_by_name(self, shop_name : str) -> Shop | None:
        shop = await self.db.execute(select(Shop).where(Shop.name == shop_name))
        return shop.scalar_one_or_none()
    async def get_by_id(self, id : int) -> ShopProduct | None:
        result = await self.db.execute(select(ShopProduct).where(ShopProduct.id == id))
        return result.scalar_one_or_none()
    async def get_by_product_name(self, name : str) -> list[ShopProduct] | None:
        result = await self.db.execute(select(ShopProduct).join(Product, ShopProduct.product_id == Product.id).where(Product.name == name).options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop)))
        return result.scalars().all()
    async def get_all_products_by_shop(self, shop_name : str) -> list[ShopProduct]:
        result = await self.db.execute(select(ShopProduct).join(Shop, ShopProduct.shop_id == Shop.id).where(Shop.name == shop_name).options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop)))
        return result.scalars().all()
    async def get_one_product_for_seller_by_name(self, prod_name : str, shop_id : int) -> ShopProduct | None:
        result = await self.db.execute(select(ShopProduct).join(Product, ShopProduct.product_id == Product.id).where(Product.name == prod_name, ShopProduct.shop_id == shop_id).options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop)))
        return result.scalar_one_or_none()
    async def save(self, shop_product: ShopProduct) -> ShopProduct:
        self.db.add(shop_product)
        await self.db.commit()
        await self.db.refresh(shop_product)
        result = await self.db.execute(
            select(ShopProduct).where(ShopProduct.id == shop_product.id)
            .options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop))
        )
        return result.scalar_one()
    async def update(self, shop_product: ShopProduct, update_data: dict) -> ShopProduct:
        for key, value in update_data.items():
            if value is not None:
                setattr(shop_product, key, value)
        await self.db.commit()
        result = await self.db.execute(
            select(ShopProduct).where(ShopProduct.id == shop_product.id)
            .options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop))
        )
        return result.scalar_one()
    async def delete(self, shop_product : ShopProduct):
        await self.db.delete(shop_product)
        await self.db.commit()
    async def get_products_by_price(self, shop_name : str, min_price : int, max_price : int) -> list[ShopProduct]:
        shop = await self._get_shop_by_name(shop_name)
        if shop:
            products = await self.db.execute(select(ShopProduct).where(ShopProduct.shop_id == shop.id, ShopProduct.price >= min_price, ShopProduct.price <= max_price).options(selectinload(ShopProduct.product), selectinload(ShopProduct.category), selectinload(ShopProduct.shop)))
            return products.scalars().all()
        return None