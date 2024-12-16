# src/utils/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    TON_API_KEY: str
    DB_USER: str = 'ton_user'
    DB_PASSWORD: str = 'ton_password'
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_NAME: str = 'ton_transactions'
    BATCH_SIZE: int = 1000
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()