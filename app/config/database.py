from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.config.application import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Creates a database engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Class that allows SQLAlchemy to keep track of our table models and to generate sql
Base = declarative_base()


# Async function to create database tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Database connection
async def get_db():
    async with AsyncSessionLocal() as async_session:
        yield async_session


session: AsyncSession = Depends(get_db)
