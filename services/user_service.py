from repositories.user_repo import UserRepository
from auth import hash_password, verify_password, create_access_token,create_refresh_token 
from services.redis_service import redis_service
from datetime import datetime,timezone
from schemas import CreateUser, UpdateUser, UpdatePassword
from celery_utils.tasks import send_welcome_email, change_password_email
from models import User, Role
from fastapi import HTTPException
import logging
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self,repo : UserRepository):
        self.repo = repo
    async def register(self, data : CreateUser) -> User:
        """
        Регистрация нового пользователя.

        Проверяет email на уникальность, хеширует пароль, ставит задачу
        в Celery на оправку приветственного письма и сохраняет в БД.

        Args:
            data: Схема CreateUser с данными нового пользователя.
        
        Raises:
            HTTPException: 409, если email уже занят.
        """
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise HTTPException(status_code=409, detail='Email уже занят')
        username_check = await self.repo.get_by_username(data.username)
        if username_check: 
            raise HTTPException(status_code=409, detail='Юзернейм уже занят')
        user = User(
            username = data.username,
            email = data.email,
            password = hash_password(data.password)
        )
        send_welcome_email.delay(user.email)
        return await self.repo.save(user)
    async def _get_user_or_404(self, user_id: int) -> User:
        """
        Вспомогательная функция получения пользователя по ID.

        Args:
            user_id: Айди пользователя
        
        Return:
            Объект User.

        Raises:
            HTTPException: 404, если пользователь не найден.
        """
        user = await self.repo.get_by_id(int(user_id))
        if not user:
            raise HTTPException(status_code=404, detail='Пользователь не найден')
        return user
    async def login(self, email : str, password : str) -> dict:
        """
        Процесс аутентификации пользователя в систему.

        Проходит путем нахождения его в базе данных по email
        Проверкой его пароля с хешем, который привязан к нему.

        Args:
            email: email пользователя.
            password: Пароль пользователя.
        
        Returns:
            Пара JWT токенов: Access и Refresh
        
        Raises:
            HTTPException: 401, неверный email или пароль или аккаунт заблокирован
        """
        user = await self.repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail='Неверный email или пароль')
        if user.role == Role.banned:
            raise HTTPException(status_code=401, detail='Ваш аккаунт заблокирован.')
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401,detail='Неверный email или пароль')
        try:
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
            await redis_service.track_active_user(user.id, today)
        except Exception as e:
            logger.error(f'Проблема занесения в редис: {e}')
        return {
            'access_token' : create_access_token({'sub': user.id, 'email': user.email, 'role': user.role.value}),
            'refresh_token': create_refresh_token({'sub': user.id, 'email': user.email, 'role': user.role.value})
        }
    async def logout_user(self, payload : dict):
        """
        Процесс выхода пользователя из системы.

        JTI токен заноится в blacklist внутри Redis
        Время его живучести = время истечения Access токена.
        Способствует защите от перехвата Access.

        Args:
            payload: Данные о пользователе полученные из Access токена.
        """
        jti = payload.get('jti')
        exp = payload.get('exp')
        if not jti or not exp:
            return
        expite_seconds = int(exp - (datetime.now(timezone.utc).timestamp()))
        if expite_seconds > 0:
            await redis_service.add_to_blacklist(jti, expite_seconds)
    async def get_me(self,username : str) -> dict:
        """
        Получение информации о пользователе.

        Args:
            id: Айди пользователя.

        Returns:
            Данные пользователя.

        Raises:
            HTTPException: 404, если пользователь не найден (через _get_user_or_404).
        """
        user = await self.repo.get_by_username(username)
        return user
    async def update(self, update_data : UpdateUser, data : dict, password : str) -> dict:
        """
        Обновление информации пользователя.

        Процесс изменения подтверждается провекой пароля пользователя.

        Args:
            update_data: измененные данные (name/phone/email).
            data: данные из Access токена.
            password: актуальный пароль пользователя
        
        Raises:
            HTTPException: 403, неверный пароль
            HTTPException: 404, если пользователь не найден (через _get_user_or_404).
        """
        user = await self._get_user_or_404(data['sub'])
        if not verify_password(password, user.password):
            raise HTTPException(status_code=403,detail='Неверный пароль')
        return await self.repo.update(user, update_data.model_dump(exclude_none=True))
    async def change_password(self,data : dict, passwords : UpdatePassword) -> dict:
        """
        Изменение пароля

        Args:
            data: данные из Access токена.
            passwords: словарь из двух паролей: old_password, new_password.
        
        Returns:
            Уведомление об успешной смене пароля.
        
        Raises:
            HTTPException: 403, пароль неверный
            HTTPException: 404, если пользователь не найден (через _get_user_or_404).

        """
        user = await self._get_user_or_404(data['sub'])
        info = verify_password(passwords.old_password, user.password)
        if not info:
            raise HTTPException(status_code=403, detail='Пароль неверный.')
        new_pass = hash_password(passwords.new_password)
        user.password = new_pass
        change_password_email.delay(user.email)
        await self.repo.save(user)
        return "Ваш пароль успешно изменен."
    async def delete(self, data : dict, password : str) -> str:
        """
        Удаление пользователя

        Args:
            data: данные из Access токена.
            password: актуальный пароль пользователя.
        
        Returns:
            Уведомление об удалении.
        
        Raises:
            HTTPException: 403, пароль неверный
            HTTPException: 404, если пользователь не найден (через _get_user_or_404).
        """
        user = await self._get_user_or_404(data['sub'])
        if not verify_password(password, user.password):
            raise HTTPException(status_code=403,detail='Неверный пароль')
        await self.repo.delete(user)
        return 'Вы успешно удалены из базы данных'