from contextlib import asynccontextmanager
from fastapi import FastAPI
from kafka_utils.producer import get_producer
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from middleware import LogMiddleware, RateLimitMiddleware
from routers import auth, admins, users, orders, products, sellers, shops
from models import User, Product, Order, OrderItem
from services.redis_service import redis_service
from aiokafka import AIOKafkaProducer
from config import settings
import json
from database import engine, Base
from kafka_utils.consumer import start_order_consumer
from kafka_utils.notify_consumer import start_notify_consumer
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    await producer.start()
    app.state.producer = producer
    order_consumer_task = asyncio.create_task(start_order_consumer())
    notify_consumer_task = asyncio.create_task(start_notify_consumer())
    yield
    order_consumer_task.cancel()
    notify_consumer_task.cancel()
    await producer.stop()
    await redis_service.close()
app = FastAPI(lifespan=lifespan)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LogMiddleware)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admins.router)
app.include_router(sellers.router)
app.include_router(shops.router)