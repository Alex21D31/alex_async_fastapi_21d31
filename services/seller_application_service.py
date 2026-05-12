from repositories.seller_applic_repo import SellerApplicationRepository
from repositories.user_repo import UserRepository
from models import SellerApplication, ApplicationStatus
from schemas import CreateSellerApplication
from fastapi import HTTPException

class SellerApplicationService:
    def __init__(self, apply_repo : SellerApplicationRepository, user_repo : UserRepository):
        self.apply_repo = apply_repo
        self.user_repo = user_repo
    async def _get_application_or_404(self, application_id) -> SellerApplication:
        apply = await self.apply_repo.get_by_id(application_id)
        if not apply:
            raise HTTPException(status_code=404, detail='Заявка не найдена.')
        return apply
    async def create_application(self, user_data : dict, new_apply : CreateSellerApplication) -> SellerApplication:
        user = await self.apply_repo.get_by_user_id(user_data['sub'])
        if user:
            raise HTTPException(status_code=409, detail="У вас уже есть активная заявка.")
        applicaton = SellerApplication(
            user_id = user_data['sub'],
            text = new_apply.text  
            )
        return await self.apply_repo.save(applicaton)
    async def get_my_application(self, user_data : dict) -> SellerApplication:
        application = await self.apply_repo.get_by_user_id(user_data['sub'])
        return application
    async def get_pending_application(self) -> SellerApplication:
        applications = await self.apply_repo.get_pending()
        return applications
    async def review_application(self, admin_data : dict, application_id : int, new_status : ApplicationStatus) -> SellerApplication:
        application = await self._get_application_or_404(application_id)
        return await self.apply_repo.update_status(application,new_status, admin_data['sub'])
    