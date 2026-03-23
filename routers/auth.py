from fastapi import APIRouter, Depends
from schemas import CreateUser, OutUser,UserLogin
from services.user_service import UserService
from dependencies import get_user_service
router = APIRouter(prefix='/auth', tags=['auth'])
@router.post('/register', response_model=OutUser)
async def register(data : CreateUser, service : UserService = Depends(get_user_service)):
    return await service.register(data)
@router.post('/login')
async def login(data : UserLogin, service : UserService = Depends(get_user_service)):
    return await service.login(data.email, data.password)



