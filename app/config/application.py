from functools import lru_cache

import httpx
from httpx import AsyncClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_KEY: str
    ACCESS_TOKEN: str
    AD_ACCOUNT_ID: str
    APP_ID: int
    APP_SECRET: str
    ASSISTANT_ID: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


http_client: AsyncClient = AsyncClient()
