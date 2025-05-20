import os
from functools import lru_cache

import httpx
from httpx import AsyncClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "postgresql+asyncpg://postgres:postgres@localhost:5432/revforce"
    OPENAI_KEY: str = os.getenv("OPENAI_KEY") 
    
# Environment settings
@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


http_client: AsyncClient = AsyncClient()
