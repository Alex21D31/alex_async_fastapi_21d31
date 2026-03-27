from repositories.user_repo import UserRepository
from auth import hash_password, verify_password, create_access_token,create_refresh_token 
from services.redis_service import redis_service
from datetime import datetime,timezone
from schemas import CreateUser, UpdateUser, UpdatePassword
from models import User, Role
from fastapi import HTTPException

class UserService:
    def __init__(self,repo : UserRepository):
        self.repo = repo
    async def register(self, data : CreateUser) -> User:
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=409, detail='Email уже занят')
        user = User(
            name = data.name,
            phone = data.phone,
            email = data.email,
            password = hash_password(data.password)
        )
        return await self.repo.save(user)
    async def _get_user_or_404(self, user_id: int) -> User:
        user = await self.repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        return user
    async def login(self, email : str, password : str) -> dict:
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail='Неверный email или пароль')
        if user.role == Role.banned:
            raise HTTPException(status_code=409, detail='Ваш аккаунт заблокирован.')
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401,detail='Неверный email или пароль')
        return {
            'access_token' : create_access_token({'id': user.id, 'email': user.email, 'role': user.role.value}),
            'refresh_token': create_refresh_token({'id': user.id, 'email': user.email, 'role': user.role.value})
        }
    async def logout_user(self, payload : dict):
        jti = payload.get('jti')
        exp = payload.get('exp')
        if not jti or not exp:
            return
        expite_seconds = int(exp - (datetime.now(timezone.utc).timestamp()))
        if expite_seconds > 0:
            await redis_service.add_to_blacklist(jti, expite_seconds)
    async def get_me(self,id : int) -> dict:
        user = await self._get_user_or_404(id)
        return user
    async def update(self, update_data : UpdateUser, data : dict, password : str) -> dict:
        user = await self._get_user_or_404(data['sub'])
        if not verify_password(password, user.password):
            raise HTTPException(status_code=403,detail='Неверный пароль')
        return await self.repo.update(user, update_data.model_dump(exclude_none=True))
    async def change_password(self,data : dict, passwords : UpdatePassword) -> dict:
        user = await self._get_user_or_404(data['sub'])
        info = verify_password(passwords.old_password, user.password)
        if not info:
            raise HTTPException(status_code=403, detail='Пароль неверный.')
        new_pass = hash_password(passwords.new_password)
        user.password = new_pass
        await self.repo.save(user)
        return "Ваш пароль успешно изменен."
    async def delete(self, password : str,  data : dict) -> str:
        user = await self._get_user_or_404(data['sub'])
        if not verify_password(password, user.password):
            raise HTTPException(status_code=403,detail='Неверный пароль')
        await self.repo.delete(user)
        return 'Вы успешно удалены из базы данных'