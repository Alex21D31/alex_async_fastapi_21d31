from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User

class UserRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_all(self) -> list[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()
    async def get_by_id(self, id : int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
    async def get_by_email(self,email : str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    async def save(self, user : User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def update(self, user : User, data : dict) -> User:
        for key,value in data.items():
            if value is not None:
                setattr(user,key,value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def delete(self, user : User) -> None:
        await self.db.delete(user)
        await self.db.commit()