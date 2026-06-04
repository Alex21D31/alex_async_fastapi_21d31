from fastapi import APIRouter, Depends, Header
from auth import verify_token
from services.shop_prod_service import ShopProductService
from services.seller_application_service import SellerApplicationService
from services.shop_service import ShopService
from services.moderation_service import ModerationService
from dependencies import get_seller_application_serivce, get_shop_service, get_moderation_service, get_shop_prod_service
from decorators import require_role
from schemas import CreateSellerApplication, OutSellerApplication, UpdateShopProduct, CreateShop, UpdateShop, OutModerationRequest, OutShopProduct, CreateShopProduct, OutShopBySeller


router = APIRouter(prefix='/sellers', tags=['sellers'])

@router.post('/apply', response_model=OutSellerApplication)
async def create_apply(new_apply : CreateSellerApplication, token_data : dict = Depends(verify_token), service : SellerApplicationService = Depends(get_seller_application_serivce)):
    return await service.create_application(token_data, new_apply)
@router.get('/apply/status',response_model=OutSellerApplication)
async def get_apply_status(token_data : dict = Depends(verify_token), service : SellerApplicationService = Depends(get_seller_application_serivce)):
    return await service.get_my_application(token_data)
@router.post('/shop', response_model=OutShopBySeller)
@require_role('seller')
async def create_shop(shop_data : CreateShop, token_data : dict = Depends(verify_token), service : ShopService = Depends(get_shop_service)):
    return await service.create_shop(token_data, shop_data)
@router.get('/shop', response_model=OutShopBySeller)
@require_role('seller')
async def get_my_shop(token_data : dict = Depends(verify_token), service : ShopService = Depends(get_shop_service)):
    return await service.get_by_seller_id(int(token_data['sub']))
@router.patch('/shop', response_model=OutShopBySeller)
@require_role('seller')
async def update_shop(update_shop_data : UpdateShop, password: str = Header(alias='x-password'), token_data : dict = Depends(verify_token), service : ShopService = Depends(get_shop_service)):
    return await service.update_shop(token_data, password, update_shop_data,)
@router.delete('/shop')
@require_role('seller')
async def delete_shop(password: str = Header(alias='x-password'), token_data : dict = Depends(verify_token), service : ShopService = Depends(get_shop_service)):
    return await service.delete_shop(token_data, password)
@router.post('/shop/submit',response_model=OutModerationRequest)
@require_role('seller')
async def create_submit(token_data : dict = Depends(verify_token), service : ModerationService = Depends(get_moderation_service)):
    return await service.submit_for_moderation(token_data)
@router.get('/shop/moderation-status', response_model=list[OutModerationRequest])
@require_role('seller')
async def check_moder_status(token_data : dict = Depends(verify_token), service : ModerationService = Depends(get_moderation_service)):
    return await service.get_my_moderation_status(token_data)
@router.get('/shop/products', response_model=list[OutShopProduct])
@require_role('seller')
async def check_my_products(token_data : dict = Depends(verify_token), service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.get_all_products_by_shop_for_owner(token_data)
@router.get('/shop/products/{prod_name}', response_model=OutShopProduct)
@require_role('seller')
async def get_one_product(prod_name : str, token_data : dict = Depends(verify_token), service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.get_by_name_for_seller(token_data, prod_name)
@router.post('/shop/products', response_model=OutShopProduct)
@require_role('seller')
async def create_product(new_product : CreateShopProduct, token_data : dict = Depends(verify_token), service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.add_product(token_data, new_product)
@router.patch('/shop/products/{prod_name}', response_model=OutShopProduct)
@require_role('seller')
async def update_product(prod_name : str, new_prod_info : UpdateShopProduct, token_data : dict = Depends(verify_token), service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.update_product(token_data,prod_name, new_prod_info)
@router.delete('/shop/products/{prod_name}')
@require_role('seller')
async def delete_product(prod_name : str, token_data : dict = Depends(verify_token), service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.delete_product(token_data, prod_name)