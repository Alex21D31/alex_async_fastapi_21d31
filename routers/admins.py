from schemas import OutUser, OutOrder, OutSellerApplication
from services.admin_service import AdminService
from services.seller_application_service import SellerApplicationService
from services.moderation_service import ModerationService
from fastapi import APIRouter, Depends
from dependencies import get_admin_service, get_seller_application_serivce, get_moderation_service
from auth import verify_token
from decorators import require_role
from models import Role, ApplicationStatus

router = APIRouter(prefix='/admin', tags=['admin'])
@router.get('/users', response_model=list[OutUser])
@require_role('admin', 'creator')
async def get_all_users(token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Вывод информации обо всех пользователях системы.
    """
    return await service.get_all_users()
@router.get('/users/{username}', response_model=OutUser)
@require_role('admin', 'creator')
async def get_user_by_id(username : str,token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Вывод информации о пользователе по ID.
    """
    return await service.get_user_by_username(username)
@router.patch('/users/{username}/role',response_model=OutUser)
@require_role('creator')
async def get_new_role(username : str, role : Role, token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Изменение роли пользователя.(Только для Creator)
    """
    return await service.change_role(username, role)
@router.patch('/users/{username}/ban')
@require_role('admin', 'creator')
async def user_ban(username : str, token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Выдача блокировки пользователю.
    """
    return await service.ban_user(username, token_data)
@router.get('/orders', response_model=list[OutOrder])
@require_role('admin', 'creator')
async def get_all_orders(token_data : dict = Depends(verify_token), service : AdminService = Depends(get_admin_service)):
    """
    Получение всех заказов в системе.
    """
    return await service.get_all_orders()
@router.patch('/users/{username}/unban')
@require_role('admin', 'creator')
async def user_unban(username : str, token_data : dict = Depends(verify_token),service : AdminService = Depends(get_admin_service)):
    """
    Разблокировка пользователя.
    """
    return await service.user_unban(username, token_data)
@router.get('/statistics')
@require_role('admin', 'creator')
async def user_statistics(token_data : dict = Depends(verify_token),service : AdminService = Depends(get_admin_service)):
    """
    Получение информации о количестве активных пользователях за сутки.
    """
    return await service.get_statistics()
@router.get('/seller-applications')
@require_role('admin', 'creator')
async def get_pending_applications(token_data : dict = Depends(verify_token),service : SellerApplicationService = Depends(get_seller_application_serivce)):
    return await service.get_pending_application()
@router.patch('/seller-applications/{application_id}/review')
@require_role('admin', 'creator')
async def update_application_status(application_id: int, new_status: ApplicationStatus, token_data : dict = Depends(verify_token), service : SellerApplicationService = Depends(get_seller_application_serivce)):
    return await service.review_application(token_data, application_id, new_status)
@router.get('/moderation')
@require_role('admin', 'creator')
async def get_requests_for_moderation(token_data : dict = Depends(verify_token), service : ModerationService = Depends(get_moderation_service)):
    return await service.get_pendings()
@router.patch('/moderation/{request_id}/review')
@require_role('admin', 'creator')
async def moderation_review(request_id: int, new_status: ApplicationStatus, token_data : dict = Depends(verify_token), service : ModerationService = Depends(get_moderation_service)):
    return await service.review(request_id, new_status, token_data)