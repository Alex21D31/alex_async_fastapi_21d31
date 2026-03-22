from schemas import CreateProduct, OutProduct, UpdateProduct
from fastapi import APIRouter, Depends
from auth import verify_token
from services.product_service import ProductService
from dependencies import get_product_service
from decorators import require_role
router = APIRouter(prefix='/products', tags=['products'])
@router.get('',response_model=list[OutProduct])
async def get_all_products(service : ProductService = Depends(get_product_service)):
    return await service.get_all_prod()
@router.get('/{id}',response_model=OutProduct)
async def get_product(id : int, service : ProductService = Depends(get_product_service)):
    return await service.get_by_id_prod(id)
@router.post('', response_model=OutProduct)
@require_role('admin', 'creater')
async def create_product(new_product : CreateProduct, token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    return await service.create(new_product)
@router.patch('/{id}',response_model=OutProduct)
@require_role('admin', 'creater')
async def patch_product(id : int, new_data : UpdateProduct,token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    return await service.update(id, new_data)
@router.delete('/{id}')
@require_role('admin', 'creater')
async def delete_product(id : int,token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    return await service.delete(id)
