from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from fastapi import Depends
from services.user_service import UserService
from repositories.user_repo import UserRepository
from services.product_service import ProductService
from repositories.product_repo import ProductRepository
from services.order_service import OrderService
from repositories.order_repo import OrderRepository
from services.admin_service import AdminService
def get_user_service(db : AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))
def get_order_service(db : AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(OrderRepository(db),ProductRepository(db), db)
def get_product_service(db : AsyncSession = Depends(get_db)) -> ProductService:
    return ProductService(ProductRepository(db))
def get_admin_service(db : AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(UserRepository(db), OrderRepository(db))


