from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import ModerationRequest, ApplicationStatus

class ModerationRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def create_request(self,mod_request: ModerationRequest) -> ModerationRequest:
        self.db.add(mod_request)
        await self.db.commit()
        await self.db.refresh(mod_request)
        return mod_request
    async def get_pending(self) -> list[ModerationRequest]:
        result = await self.db.execute(select(ModerationRequest).where(ModerationRequest.status == ApplicationStatus.pending))
        return result.scalars().all()
    async def get_by_id(self, id : int) -> ModerationRequest | None:
        result = await self.db.execute(select(ModerationRequest).where(ModerationRequest.id == id))
        return result.scalar_one_or_none()
    async def get_by_shop_id(self, shop_id : int) -> list[ModerationRequest]:
        result = await self.db.execute(select(ModerationRequest).where(ModerationRequest.shop_id == shop_id))
        return result.scalars().all()
    async def update_status(self,mod_request: ModerationRequest,new_status: ApplicationStatus, admin_id: int) -> ModerationRequest:
        mod_request.status = new_status
        mod_request.reviewed_by = admin_id
        await self.db.commit()
        await self.db.refresh(mod_request)
        return mod_request
