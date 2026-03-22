from schemas import CreateOrder, OutOrder, UpdateOrder
from fastapi import APIRouter, Depends
from dependencies import get_order_service
from services.order_service import OrderService
from auth import verify_token
from decorators import require_role
from models import Status
router = APIRouter(prefix='/orders', tags=['orders'])

@router.post('', response_model=OutOrder)
async def create_order(new_order : CreateOrder, token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.create_order(int(token_data['sub']), new_order)
@router.get('', response_model=list[OutOrder])
async def get_my_orders(token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.get_all_orders(token_data)
@router.get('/{id}', response_model=OutOrder)
async def get_one_order(id : int, token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.get_one_order(id, token_data)
@router.patch('/{id}',response_model=OutOrder)
async def update_order(order_id : int, new_data : UpdateOrder, token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.update_order(order_id, new_data)
@router.patch('/status/{id}',response_model=OutOrder)
@require_role('admin', 'creater')
async def update_status(id : int, new_status : Status,token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.update_status(id, new_status)
@router.delete('/{id}')
@require_role('admin', 'creater')
async def delete_order(id : int,  token_data : dict = Depends(verify_token), service : OrderService = Depends(get_order_service)):
    return await service.delete_order(id)