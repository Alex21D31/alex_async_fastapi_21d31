from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User

class UserRepository:
    def __init__(self, db : AsyncSession):
        self.db = db
    async def get_all(self) -> list[User]:
        """
        Все пользователи из базы данных.

        Returns:
            список объектов User.
        """
        result = await self.db.execute(select(User))
        return result.scalars().all()
    async def get_by_id(self, id : int) -> User | None:
        """
        Один пользователь из базы данных.

        Args:
            id: айди пользователя, которого необходимо найти.
        
        Returns:
            объект User или None, если пользователь не найден.
        """
        result = await self.db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()
    async def get_by_email(self,email : str) -> User | None:
        """
        Один пользователь из базы данных.

        Args:
            email: email пользователя, которого необходимо найти.
        
        Returns:
            объект User или None, если пользователь не найден.
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    async def save(self, user : User) -> User:
        """
        Сохранение пользователя в базу данных.

        Args:
            user: Экземпляр модели User с данными для сохранения.
        
        Returns:
            Созданный объект пользователя с заполненными системными полями 
            (ID, роль по умолчанию и дата регистрации).
        """
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def update(self, user : User, update_data : dict) -> User:
        """
        Обновление данных пользователя. 
        
        Происходит через перебор словаря: изменяются только те поля, 
        которые переданы в update_data и не являются None.

        Args:
            user: Экземпляр модели User, который подлежит изменению.
            update_data: Словарь с новыми данными (name, phone, email).

        Returns:
            Обновленный объект из базы данных с актуальной датой updated_at.
        """
        for key,value in update_data.items():
            if value is not None:
                setattr(user,key,value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    async def delete(self, user : User) -> None:
        """
        Удаление пользователя из базы данных.

        Args:
            user: Экземпляр модели User для удаления.
        """
        await self.db.delete(user)
        await self.db.commit()
    async def update_role(self, user: User, new_role) -> None:
        user.role = new_role
        await self.db.commit()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
    