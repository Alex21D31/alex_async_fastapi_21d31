from repositories.product_repo import ProductRepository
from schemas import CreateProduct, UpdateProduct
from models import Product
from fastapi import HTTPException

class ProductService():
    def __init__(self,repo : ProductRepository):
        self.repo = repo
    async def _get_prod_or_404(self, prod_id: int) -> Product:
        """
        Получение информации о продукте из базы данных.
        Внутренняя функция, используется для проверки на наличие в основных функциях.

        Args:
            prod_id: Айди продукта.
        
        Returns:
            Информация о продукте.

        Raises:
            HTTPException: 404, продукт не найден.
        """
        prod = await self.repo.get_by_id(prod_id)
        if not prod:
            raise HTTPException(status_code=404, detail='Продукт не найден')
        return prod
    async def get_all_prod(self):
        """
        Получение информации обо всех продуктах.
        """
        return await self.repo.get_all()
    async def get_by_id_prod(self, id : int):
        """
        Получение информации о продукте по Айди.

        Raises:
            HTTPException: 404, если продукт не найден (через _get_prod_or_404).
        """
        return await self._get_prod_or_404(id)
    async def create(self, prod : CreateProduct, user_data : dict) -> dict:
        """
        Создание нового продукта.
        Функция доступна только для ролей Admin и выше.

        Args:
            prod: словарь обязательных параметров(name, description, price, quantity).
        
        Retruens:
            Результат создания.
        
        Raises:
            HTTPException: 409, конфликт существующих объектов.
        """
        if await self.repo.get_by_name(prod.name):
            raise HTTPException(status_code=409, detail='Такой продукт уже существует.')
        product = Product(
            name = prod.name,
            description = prod.description,
            price = prod.price,
            quantity = prod.quantity
        )
        return await self.repo.save(product)
    async def update(self,prod_id : int, new_data : UpdateProduct) -> dict:
        """
        Обновление информации о продукте.
        Функция доступна только для ролей Admin и выше.

        Args:
            prod_id: Айди продукта для поиска по базе.
            new_data: Словарь измененных элементов.
        
        Returns:
            Измененный продукт.

        Raises:
            HTTPException: 404, если продукт не найден (через _get_prod_or_404).
        """
        prod = await self._get_prod_or_404(prod_id)
        return await self.repo.update(prod, new_data.model_dump(exclude_none=True)) 
    async def delete(self, prod_id : int) -> str:
        """
        Удаление продукта.
        Функция доступна только для ролей Admin и выше.

        Args:
            prod_id: Айди продукта для поиска по базе.

        Returns:
            Уведомление об удалении.

        Raises:
            HTTPException: 404, если продукт не найден (через _get_prod_or_404).
        """
        prod = await self._get_prod_or_404(prod_id)
        await self.repo.delete(prod)
        return f'Продукт {prod.name} успешно удален из базы данных.'
        