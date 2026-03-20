from repositories.product_repo import ProductRepository
from schemas import CreateProduct
from models import Product
from fastapi import HTTPException

class ProductService():
    def __init__(self,repo : ProductRepository):
        self.repo = repo
    async def _get_prod_or_404(self, prod_id: int) -> Product:
        user = await self.repo.get_by_id(prod_id)
        if not user:
            raise HTTPException(status_code=404, detail='Продукт не найден')
        return user
    async def get_all_prod(self):
        result = await self.repo.get_all()
        return result
    async def get_by_id_prod(self, id : int):
        prod = await self._get_prod_or_404(id)
        return prod
    async def create(self, prod : CreateProduct) -> dict:
        product = Product(
            name = prod.name,
            description = prod.description,
            price = prod.price,
            quantity = prod.quantity
        )
        result = await self.repo.save(product)
        return result
    async def update(self,prod_id : int, new_data : dict) -> dict:
        prod = await self._get_prod_or_404(prod_id)
        new_prod = await self.repo.update(prod, new_data)
        return new_prod
    async def delete(self, prod_id : int) -> str:
        prod = await self._get_prod_or_404(prod_id)
        await self.repo.delete(prod)
        return f'Продукт {prod.name} успешно удален из базы данных.'
        