from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    LIVE_TIME : int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    REDIS_HOST: str
    REDIS_PORT: int
    model_config = {"env_file": ".env"}
settings = Settings()  