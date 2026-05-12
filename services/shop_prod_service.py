from repositories.shop_prod_repo import ShopProductRepository
from repositories.shop_repo import ShopRepository
from repositories.product_repo import ProductRepository
from repositories.category_repo import CategoryRepository
from models import ShopProduct
from schemas import CreateShopProduct, UpdateShopProduct
from fastapi import HTTPException

class ShopProductService:
    def __init__(self, categ_repo : CategoryRepository, shop_prod_repo : ShopProductRepository, shop_repo : ShopRepository, prod_repo : ProductRepository):
        self.shop_prod_repo = shop_prod_repo
        self.shop_repo = shop_repo
        self.prod_repo = prod_repo
        self.categ_repo = categ_repo
    async def get_by_name_for_seller(self, seller_data : dict, prod_name : str) -> ShopProduct:
        shop = await self.shop_repo.get_by_seller_id(seller_data['sub'])
        product = await self.shop_prod_repo.get_one_product_for_seller_by_name(prod_name, shop.id)
        if not product:
            raise HTTPException(status_code=404,detail="Продукт не найден в базе данных.")
        return product
    async def get_all_products_by_shop(self, shop_name: str) -> list[ShopProduct]:
        return await self.shop_prod_repo.get_all_products_by_shop(shop_name)
    async def add_product(self, seller_data : dict, new_product : CreateShopProduct) -> ShopProduct:
        shop = await self.shop_repo.get_by_seller_id(seller_data['sub'])
        if shop.name != new_product.shop_name:
            raise HTTPException(status_code=403, detail='Вы не можете добавлять товары в чужой магазин.')
        if new_product.quantity > 200:
            raise HTTPException(status_code=400, detail='Максимальное количество за раз - 200 единиц товара.')
        existing = await self.shop_prod_repo.get_one_product_for_seller_by_name(new_product.product_name, shop.id)
        if existing:
            existing.quantity += new_product.quantity
            await self.shop_prod_repo.update(existing, {'quantity': existing.quantity})
            return existing
        product_obj = await self.prod_repo.get_by_name(new_product.product_name)
        if not product_obj:
            raise HTTPException(status_code=404, detail='Товар не найден в каталоге.')
        product_category = await self.categ_repo.get_by_name(product_obj.category)
        product = ShopProduct(
            quantity=new_product.quantity,
            price=new_product.price,
            shop_id=shop.id,
            product_id=product_obj.id,
            category_id=product_category.id
        )
        return await self.shop_prod_repo.save(product)
    async def update_product(self,seller_data : dict, product_name : str, update_data : UpdateShopProduct) -> ShopProduct:
        shop = await self.shop_repo.get_by_seller_id(seller_data['sub'])
        product = await self.shop_prod_repo.get_one_product_for_seller_by_name(product_name, shop.id)
        if not product:
            raise HTTPException(status_code=404, detail='Продукт не найден в вашем магазине.')
        return await self.shop_prod_repo.update(product, update_data)
    async def delete_product(self, seller_data : dict, product_name : str):
        shop = await self.shop_repo.get_by_seller_id(seller_data['sub'])
        product = await self.shop_prod_repo.get_one_product_for_seller_by_name(product_name, shop.id)
        if not product:
            raise HTTPException(status_code=404, detail='Продукт не найден в вашем магазине.')
        return await self.shop_prod_repo.delete(product)

        