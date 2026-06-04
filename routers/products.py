from schemas import CreateProduct, OutProduct, UpdateProduct, OutCategory
from fastapi import APIRouter, Depends
from auth import verify_token
from services.product_service import ProductService
from services.category_service import CategoryService
from dependencies import get_product_service, get_category_service
from decorators import require_role
router = APIRouter(prefix='/products', tags=['products'])
@router.get('',response_model=list[OutProduct])
async def get_all_products(service : ProductService = Depends(get_product_service)):
    """
    Получение информации обо всех продуктах.
    """
    return await service.get_all_prod()
@router.get('/category/{name}',response_model=list[OutProduct])
async def get_products_by_category_name(name : str, service : ProductService = Depends(get_product_service)):
    return await service.get_all_products_by_category(name)
@router.get('/category',response_model=list[str])
async def get_all_categories(service : CategoryService = Depends(get_category_service)):
    return await service.get_all_categories()
@router.get('/{product_name}',response_model=OutProduct)
async def get_product(product_name : str, service : ProductService = Depends(get_product_service)):
    """
    Получение информации о продукте по названию.
    """
    return await service.get_by_prod_name(product_name)
@router.post('', response_model=OutProduct)
@require_role('admin', 'creator')
async def create_product(new_product : CreateProduct, token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    """
    Создание продукта.
    """
    return await service.create(new_product)
@router.patch('/{product_name}',response_model=OutProduct)
@require_role('admin', 'creator')
async def patch_product(product_name : str, new_data : UpdateProduct,token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    """
    Изменение продукта.
    """
    return await service.update(product_name, new_data)
@router.delete('/{product_name}')
@require_role('admin', 'creator')
async def delete_product(product_name : str,token_data : dict = Depends(verify_token),service : ProductService = Depends(get_product_service)):
    """
    Удаление продукта.
    """
    return await service.delete(product_name)


    
