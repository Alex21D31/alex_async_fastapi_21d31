from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import jwt, ExpiredSignatureError, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import settings
security = HTTPBearer()
LIVE_TIME = settings.LIVE_TIME
ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
pwd_context = CryptContext(schemes=['bcrypt'])
def hash_password(password : str) -> str:
    return pwd_context.hash(password)
def verify_password(password : str, hashed : str) -> bool:
    return pwd_context.verify(password,hashed)
def change_password(passwords : dict, hash : str) -> str:
    if not verify_password(passwords['old_password'],hash):
        raise HTTPException(status_code=403, detail='Неверный пароль')
    new_pass = hash_password(passwords['new_password'])
    return new_pass
def create_access_token(data : dict) -> str:
    info = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=LIVE_TIME)
    token_data = {
        'sub' : str(info['id']),
        'email' : info['email'],
        'token' : 'access',
        'exp' : expire,
        'role' : info['role']
    }
    token=jwt.encode(token_data,SECRET_KEY,algorithm=ALGORITHM)
    return token
def create_refresh_token(data : dict) -> str:
    info = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    token_data = {
        'sub' : str(info['id']),
        'email' : info['email'],
        'token' : 'refresh',
        'exp' : expire,
        'role' : info['role']
    }
    token=jwt.encode(token_data,SECRET_KEY,algorithm=ALGORITHM)
    return token
def verify_token(credintals : HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credintals.credentials
    try:
        data = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        return data
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Срок действия токена истек.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    