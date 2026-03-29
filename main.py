from contextlib import asynccontextmanager
from fastapi import FastAPI
from middleware import LogMiddleware, RateLimitMiddleware
from routers import auth, admins, users, orders, products
from models import User, Product, Order, OrderItem
from services.redis_service import redis_service
from database import engine, Base

@asynccontextmanager
async def lifespan(app : FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await redis_service.close()
app = FastAPI(lifespan=lifespan)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LogMiddleware)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admins.router)