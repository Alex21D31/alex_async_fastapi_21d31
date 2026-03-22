from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import CreateUser, OutUser,UserLogin
from services.user_service import UserService
from repositories.user_repo import UserRepository


router = APIRouter(prefix='/auth', tags=['auth'])
def get_user_service(db : AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))
@router.post('/register', response_model=OutUser)
async def register(data : CreateUser, service : UserService = Depends(get_user_service)):
    return await service.register(data)
@router.post('/login')
async def login(data : UserLogin, service : UserService = Depends(get_user_service)):
    return await service.login(data.email, data.password)



