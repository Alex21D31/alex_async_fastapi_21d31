from schemas import OutUser, OutOrder
from services.admin_service import AdminService
from fastapi import APIRouter, Depends
from dependencies import get_admin_service
from auth import verify_token
from decorators import require_role
from models import Role

router = APIRouter(prefix='/admin', tags=['admin'])
@router.get('/users', response_model=list[OutUser])
@require_role('admin', 'creator')
async def get_all_users(token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Вывод информации обо всех пользователях системы.
    """
    return await service.get_all_users()
@router.get('/users/{id}', response_model=OutUser)
@require_role('admin', 'creator')
async def get_user_by_id(id : int,token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Вывод информации о пользователе по ID.
    """
    return await service.get_user_by_id(id)
@router.patch('/users/{user_id}/role',response_model=OutUser)
@require_role('creator')
async def get_new_role(user_id : int,role : Role, token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Изменение роли пользователя.(Только для Creator)
    """
    return await service.change_role(user_id, role)
@router.patch('/users/{user_id}/ban')
@require_role('admin', 'creator')
async def user_ban(user_id : int, token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Выдача блокировки пользователю.
    """
    return await service.ban_user(user_id, token_data)
@router.get('/orders', response_model=list[OutOrder])
@require_role('admin', 'creator')
async def get_all_orders(token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Получение всех заказов в системе.
    """
    return await service.get_all_orders()
@router.patch('/users/{user_id}/unban')
@require_role('admin', 'creator')
async def user_unban(user_id : int, token_data : dict = Depends(verify_token),service : AdminService = Depends(get_admin_service)):
    """
    Разблокировка пользователя.
    """
    return await service.user_unban(user_id, token_data)
@router.get('/statistics')
@require_role('admin', 'creator')
async def user_statistics(token_data : dict = Depends(verify_token),service : AdminService = Depends(get_admin_service)):
    """
    Получение информации о количестве активных пользователях за сутки.
    """
    return await service.get_statistics()

