from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka_utils.producer import get_producer
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from middleware import LogMiddleware, RateLimitMiddleware
from routers import auth, admins, users, orders, products
from models import User, Product, Order, OrderItem
from services.redis_service import redis_service
from database import engine, Base

@asynccontextmanager
async def lifespan(app : FastAPI):
    await get_producer()
    yield
    await redis_service.close()
    producer = await get_producer()
    await producer.stop()
app = FastAPI(lifespan=lifespan)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LogMiddleware)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admins.router)