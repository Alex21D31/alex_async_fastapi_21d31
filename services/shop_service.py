from repositories.shop_repo import ShopRepository
from repositories.user_repo import UserRepository
from schemas import UpdateShop, CreateShop
from fastapi import HTTPException
from models import Shop, Role
from auth import verify_password


class ShopService:
    def __init__(self, shop_repo : ShopRepository, user_repo : UserRepository):
        self.shop_repo = shop_repo
        self.user_repo = user_repo
    async def _get_shop_or_404(self,shop_name : str) -> Shop:
        shop = await self.shop_repo.get_by_shop_name(shop_name)
        if not shop:
            raise HTTPException(status_code=404, detail="Магазин не найден")
        return shop
    async def get_by_seller_id(self, seller_id : int) -> Shop:
        shop = await self.shop_repo.get_by_seller_id(seller_id)
        if not shop:
            raise HTTPException(status_code=404, detail="У данного пользователя нет магазинов или пользователя не существует.")
        return shop
    async def get_all_verified(self) -> list[Shop]:
        shops = await self.shop_repo.get_all_verified()
        return shops
    async def create_shop(self, user_data : dict, shop_data : CreateShop) -> Shop:
        if await self.shop_repo.get_by_shop_name(shop_data.name):
            raise HTTPException(status_code=409, detail='Магазин с таким названием уже существует.')
        if await self.shop_repo.get_by_seller_id(user_data['sub']):
            raise HTTPException(status_code=409, detail='У вас уже есть магазин.')
        shop = Shop(
            name = shop_data.name,
            description = shop_data.description,
            seller_id=user_data['sub']
            )
        return await self.shop_repo.save_shop(shop)
    async def update_shop(self, user_data : dict, shop_name : str, password : str, update_data : UpdateShop) -> Shop:
        user = await self.user_repo.get_by_id(user_data['sub'])
        if not verify_password(password,user.password):
            raise HTTPException(status_code=403, detail="Неверный пароль")
        shop = await self._get_shop_or_404(shop_name)
        if shop.seller_id != user_data['sub']:
            raise HTTPException(status_code=403,detail='Этот магазин вам не принадлежит.')
        return await self.shop_repo.update_shop(shop, update_data)
    async def delete_shop(self, user_data : dict, shop_name : str, password : str):
        user = await self.user_repo.get_by_id(user_data['sub'])
        if not verify_password(password,user.password):
            raise HTTPException(status_code=403, detail="Неверный пароль")
        shop = await self._get_shop_or_404(shop_name)
        if shop.seller_id != user_data['sub']:
            raise HTTPException(status_code=403,detail='Этот магазин вам не принадлежит.')
        await self.shop_repo.delete_shop(shop)
        await self.user_repo.update_role(user, Role.user)
        return {'detail' : 'Ваш магазин успешно удален.'}
