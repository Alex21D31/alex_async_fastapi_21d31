from repositories.category_repo import CategoryRepository
from services.redis_service import RedisService
from schemas import CreateCategory
from models import Category
from fastapi import HTTPException

class CategoryService:
    def __init__(self, cate_repo : CategoryRepository, redis_service : RedisService):
        self.cate_repo = cate_repo
        self.redis_service = redis_service
    async def _get_category_or_404(self, category_name : str) -> Category:
        category =  await self.cate_repo.get_by_name(category_name)
        if not category:
            raise HTTPException(status_code=404, detail="Категория не найдена.")
        return category
    async def get_all_categories(self) -> list[str]:
        categories_in_redis = await self.redis_service.get_categories_with_redis()
        if categories_in_redis:
            return list(categories_in_redis)
        categories = await self.cate_repo.get_all()
        categories_names = [cate.name for cate in categories]
        await self.redis_service.set_categorites_with_redis(categories_names)
        return categories_names
    async def create_category(self, new_category : CreateCategory) -> Category:
        if await self.cate_repo.get_by_name(new_category.name):
            raise HTTPException(status_code=409, detail="Такая категория уже существует.")
        category = Category(
            name = new_category.name,
            description = new_category.description
            )
        await self.redis_service.clear_redis_key('categories')
        return await self.cate_repo.save(category)
    async def delete_category(self, category_name : str):
        category =await self._get_category_or_404(category_name)
        await self.cate_repo.delete(category)
        await self.redis_service.clear_redis_key('categories')
        return {'detail' : f'Категория {category.name} успешно удалена'}