from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models import ApplicationStatus, SellerApplication
from models import User

class SellerApplicationRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_by_id(self, id : int) -> SellerApplication | None:
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.id == id))
        return result.scalar_one_or_none()
    async def get_by_username(self, username: str) -> SellerApplication | None:
        result = await self.db.execute(select(SellerApplication).join(User, SellerApplication.user_id == User.id).where(User.username == username))
        return result.scalar_one_or_none()
    async def get_pending(self) -> list[SellerApplication]:
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.status == ApplicationStatus.pending).options(selectinload(SellerApplication.user), selectinload(SellerApplication.reviewer)))
        return result.scalars().all()
    async def save(self, application : SellerApplication) -> SellerApplication:
        self.db.add(application)
        await self.db.commit() 
        await self.db.refresh(application)
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.id == application.id).options(selectinload(SellerApplication.user), selectinload(SellerApplication.reviewer)))
        return result.scalar_one()
    async def update_status(self, application : SellerApplication, new_status : ApplicationStatus, admin_id : int) -> SellerApplication:
        application.status = new_status
        application.reviewed_by = admin_id
        await self.db.commit()
        await self.db.refresh(application)
        result = await self.db.execute(select(SellerApplication).where(SellerApplication.id == application.id).options(selectinload(SellerApplication.user), selectinload(SellerApplication.reviewer)))
        return result.scalar_one()
