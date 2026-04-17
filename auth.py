from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, Depends
from services.redis_service import redis_service
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import settings
import uuid
import logging
logger = logging.getLogger(__name__)
security = HTTPBearer()
LIVE_TIME = settings.LIVE_TIME
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
pwd_context = CryptContext(schemes=['bcrypt'])
def hash_password(password : str) -> str:
    """
    Хеширует пароль с помощью bcrypt.

    Args:
        password: Пароль в открытом виде.

    Returns:
        Хеш пароля.
    """
    return pwd_context.hash(password)
def verify_password(password : str, hashed : str) -> bool:
    """
    Сравнивает пароль пользователя с хешем из базы данных.

    Args:
        password: Пароль в открытом виде.
        hashed: Хеш пароля из базы данных.

    Returns:
        True если пароль верный, False если нет.
    """
    return pwd_context.verify(password,hashed)
def change_password(passwords : dict, hashed_password : str) -> str:
    """
    Изменяет пароль пользователя.

    Args:
        passwords: Словарь с ключами old_password и new_password.
        hash: Хеш текущего пароля из базы данных.

    Returns:
        Хеш нового пароля.

    Raises:
        HTTPException 403: если старый пароль неверный.
    """
    if not verify_password(passwords['old_password'],hashed_password):
        raise HTTPException(status_code=403, detail='Неверный пароль')
    new_pass = hash_password(passwords['new_password'])
    return new_pass
def create_access_token(data : dict) -> str:
    """
    Создаёт JWT access токен для аутентификации пользователя.

    Args:
        data: словарь с данными пользователя (id, email, role).

    Returns:
        подписанный JWT access токен со сроком жизни 30 минут,
        содержит уникальный идентификатор jti для возможности инвалидации.
    """
    info = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=LIVE_TIME)
    uid = str(uuid.uuid4())
    token_data = {
        'sub' : str(info['id']),
        'email' : info['email'],
        'token' : 'access',
        'exp' : expire,
        'jti' : uid,
        'role' : info['role']
    }
    token=jwt.encode(token_data,SECRET_KEY,algorithm=ALGORITHM)
    return token
def create_refresh_token(data : dict) -> str:
    """
    Создаёт JWT refresh токен для получения новых access токенов.

    Args:
        data: Словарь с данными пользователя (id, email, role).

    Returns:
        Подписанный JWT refresh токен со сроком жизни 30 дней,
        содержит уникальный идентификатор jti для возможности инвалидации.
    """
    info = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    uid = str(uuid.uuid4())
    token_data = {
        'sub' : str(info['id']),
        'email' : info['email'],
        'token' : 'refresh',
        'exp' : expire,
        'jti' : uid,
        'role' : info['role']
    }
    token=jwt.encode(token_data,SECRET_KEY,algorithm=ALGORITHM)
    return token
async def verify_token(credentials : HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Верифицирует JWT access токен и проверяет права доступа пользователя.
    Для проверки бана и аннулирования токена обращается к Redis.

    Args:
        credintals: Bearer токен из заголовка Authorization

    Returns:
        Словарь с данными пользователя (id, email, role, jti)

    Raises:
        HTTPException 401: если токен истёк, невалидный или аннулирован
        HTTPException 401: если аккаунт пользователя заблокирован
    """
    token = credentials.credentials
    try:
        data = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        jti = data.get('jti')
        user_id = str(data.get('sub'))
        try:
            if await redis_service.is_banned(user_id):
                raise HTTPException(status_code=401, detail="Ваш аккаунт заблокирован.")
            if await redis_service.is_blacklisted(jti):
                raise HTTPException(status_code=401,detail="Токен аннулирован. Пожалуйста, войдите снова." )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ошибка Redis при проверке токена: {e}")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    return data