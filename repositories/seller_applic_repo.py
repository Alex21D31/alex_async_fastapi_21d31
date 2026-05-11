from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ApplicationStatus, SellerApplication

class SellerApplicationRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int) -> SellerApplication | None:
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.id == id))
        return result.scalar_one_or_none()
    async def get_by_username(self, username: str) -> SellerApplication | None:
        from models import User
        result = await self.db.execute(select(SellerApplication).join(User, SellerApplication.user_id == User.id).where(User.username == username))
        return result.scalar_one_or_none()
    async def get_pending(self) -> list[SellerApplication]:
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.status == ApplicationStatus.pending))
        return result.scalars().all()
    async def save(self, application : SellerApplication) -> SellerApplication:
        self.db.add(application)
        await self.db.commit() 
        await self.db.refresh(application)
        return application
    async def update_status(self, application : SellerApplication, new_status : ApplicationStatus, admin_id : int) -> SellerApplication:
        application.status = new_status
        application.reviewed_by = admin_id
        await self.db.commit()
        await self.db.refresh(application)
        return application