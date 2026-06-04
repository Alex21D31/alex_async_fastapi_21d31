from fastapi import APIRouter, Depends
from schemas import OutShopByUsers, OutShopProduct
from services.shop_service import ShopService
from services.shop_prod_service import ShopProductService
from dependencies import get_shop_prod_service, get_shop_service

router = APIRouter(prefix='/shops', tags=['shops'])

@router.get('',response_model=list[OutShopByUsers])
async def get_all_verified_shops(service : ShopService = Depends(get_shop_service)):
    return await service.get_all_verified()
@router.get('/{name}/products/price', response_model=list[OutShopProduct])
async def get_all_products_by_price(name : str, min_price : int, max_price : int, service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.get_products_by_price(name, min_price, max_price)
@router.get('/{name}/products',response_model=list[OutShopProduct])
async def get_all_products_by_shop(name : str, service : ShopProductService = Depends(get_shop_prod_service)):
    return await service.get_all_products_by_shop_by_name(name)
@router.get('/{name}',response_model=OutShopByUsers)
async def get_shop_by_name(name : str, service : ShopService = Depends(get_shop_service)):
    return await service.get_by_name(name)
