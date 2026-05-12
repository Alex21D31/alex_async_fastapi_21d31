from repositories.moderation_repo import ModerationRepository
from repositories.shop_repo import ShopRepository
from models import ModerationRequest, ApplicationStatus
from fastapi import HTTPException

class ModerationService:
    def __init__(self, moder_repo : ModerationRepository, shop_repo : ShopRepository):
        self.moder_repo = moder_repo
        self.shop_repo = shop_repo
    async def submit_for_moderation(self, user_data : dict) -> ModerationRequest:
        shop = await self.shop_repo.get_by_seller_id(user_data['sub'])
        existing = await self.moder_repo.get_by_shop_id(shop.id)
        if existing:
            raise HTTPException(status_code=409, detail='Заявка на модерацию уже существует.')
        request = ModerationRequest(
            shop_id = shop.id
            )
        return await self.moder_repo.create_request(request)
    async def get_my_moderation_status(self, user_data : dict) -> ModerationRequest:
        shop = await self.shop_repo.get_by_seller_id(user_data['sub'])
        return await self.moder_repo.get_by_shop_id(shop.id)
    async def get_pendings(self) -> list[ModerationRequest]:
        return await self.moder_repo.get_pending()
    async def review(self, req_id : int, new_status : ApplicationStatus, admin_data : dict) -> ModerationRequest:
        request = await self.moder_repo.get_by_id(req_id)
        if not request:
            raise HTTPException(status_code=404, detail='Заявка не найдена.')
        if new_status == ApplicationStatus.approved:
            shop = await self.shop_repo.get_by_id(request.shop_id)
            await self.shop_repo.set_verified(shop, True)
        return await self.moder_repo.update_status(request, new_status, admin_data['sub'])

        