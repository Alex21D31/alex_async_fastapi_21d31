from repositories.seller_applic_repo import SellerApplicationRepository
from repositories.user_repo import UserRepository
from models import SellerApplication, ApplicationStatus, Role
from datetime import datetime, timezone
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
        user = await self.user_repo.get_by_id(int(user_data['sub']))
        user_have = await self.apply_repo.get_by_username(user.username)
        if user_have:
            if user_have.reviewed_by is None:
                raise HTTPException(status_code=409, detail="У вас уже есть активная заявка, дождитесь вердикта администрации.")
            diff = datetime.now(timezone.utc).replace(tzinfo=None) - user_have.created_at
            if diff.days < 7:
                raise HTTPException(status_code=409, detail="За последнюю неделю у вас уже есть рассмотренная заявка.")
        applicaton = SellerApplication(
            user_id = user.id,
            text = new_apply.text  
            )
        return await self.apply_repo.save(applicaton)
    async def get_my_application(self, user_data : dict) -> SellerApplication:
        user = await self.user_repo.get_by_id(int(user_data['sub']))
        application = await self.apply_repo.get_by_username(user.username)
        return application
    async def get_pending_application(self) -> SellerApplication:
        applications = await self.apply_repo.get_pending()
        return applications
    async def review_application(self, admin_data : dict, application_id : int, new_status : ApplicationStatus) -> SellerApplication:
        application = await self._get_application_or_404(application_id)
        user = await self.user_repo.get_by_id(application.user_id)
        if application.status == new_status:
            raise HTTPException(status_code=401, detail='Такой статус объявление имеет сейчас.')
        if new_status == ApplicationStatus.approved:
            await self.user_repo.update(user, {'role' : Role.seller})
        return await self.apply_repo.update_status(application,new_status, int(admin_data['sub']))
    