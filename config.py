from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    LIVE_TIME : int
    model_config = {"env_file": ".env"}
settings = Settings()  