from fastapi import APIRouter, Depends
from schemas import CreateUser, OutUser,UserLogin
from services.user_service import UserService
from dependencies import get_user_service
from auth import verify_token
router = APIRouter(prefix='/auth', tags=['auth'])
@router.post('/register', response_model=OutUser)
async def register(data : CreateUser, service : UserService = Depends(get_user_service)):
    return await service.register(data)
@router.post('/login')
async def login(data : UserLogin, service : UserService = Depends(get_user_service)):
    return await service.login(data.email, data.password)
@router.post('/logout')
async def logout(token_data : dict = Depends(verify_token), service : UserService = Depends(get_user_service)):
    await service.logout_user(token_data)
    return {'detail' : 'Successfully logged out'}

