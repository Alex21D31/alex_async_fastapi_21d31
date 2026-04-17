from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings
engine = create_async_engine(settings.DATABASE_URL)
session = async_sessionmaker(engine,expire_on_commit=False)
class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    """
    pass
async def get_db():
    """
    Генератор для получения асинхронной сессии базы данных.
    """
    async with session() as db:
        yield db