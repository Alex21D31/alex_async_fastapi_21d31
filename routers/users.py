from schemas import OutUser, UpdatePassword, UpdateUser
from dependencies import get_user_service
from fastapi import APIRouter, Depends, Header
from auth import verify_token
from services.user_service import UserService
router = APIRouter(prefix='/users', tags=['users'])
@router.get('/me',response_model=OutUser)
async def get_user_info(token_data : dict = Depends(verify_token), service : UserService = Depends(get_user_service)):
    return await service.get_me(int(token_data['sub']))
@router.patch('/me', response_model=OutUser)
async def patch_user(new_data : UpdateUser, password : str = Header(alias='x-password'), token_data : dict = Depends(verify_token), service : UserService = Depends(get_user_service)):
    return await service.update(new_data, token_data,password)
@router.patch('/me/password')
async def change_password(passwords : UpdatePassword, token_data : dict = Depends(verify_token), service : UserService = Depends(get_user_service)):
    return await service.change_password(token_data, passwords)
@router.delete('/me')
async def delete_user(password : str = Header(alias='x-password'), token_data : dict = Depends(verify_token), service : UserService = Depends(get_user_service)):
    return await service.delete(password, token_data)
    

