from repositories.product_repo import ProductRepository
from schemas import CreateProduct, UpdateProduct
from models import Product
from fastapi import HTTPException

class ProductService():
    def __init__(self,repo : ProductRepository):
        self.repo = repo
    async def _get_prod_or_404(self, prod_id: int) -> Product:
        prod = await self.repo.get_by_id(prod_id)
        if not prod:
            raise HTTPException(status_code=404, detail='Продукт не найден')
        return prod
    async def get_all_prod(self):
        return await self.repo.get_all()
    async def get_by_id_prod(self, id : int):
        return await self.repo.get_by_id(id)
    async def create(self, prod : CreateProduct) -> dict:
        product = Product(
            name = prod.name,
            description = prod.description,
            price = prod.price,
            quantity = prod.quantity
        )
        return await self.repo.save(product)
    async def update(self,prod_id : int, new_data : UpdateProduct) -> dict:
        prod = await self._get_prod_or_404(prod_id)
        return await self.repo.update(prod, new_data.model_dump(exclude_none=True)) 
    async def delete(self, prod_id : int) -> str:
        prod = await self._get_prod_or_404(prod_id)
        await self.repo.delete(prod)
        return f'Продукт {prod.name} успешно удален из базы данных.'
        