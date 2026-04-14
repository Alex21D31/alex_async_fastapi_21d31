from fastapi import APIRouter, Depends
from schemas import CreateUser, OutUser,UserLogin
from services.user_service import UserService
from dependencies import get_user_service
from auth import verify_token
from fastapi import Request
router = APIRouter(prefix='/auth', tags=['auth'])
@router.get("/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}
@router.get("/debug-headers")
async def debug_headers(request: Request):
    return {
        "client_host": request.client.host,
        "headers": dict(request.headers),
    }
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

