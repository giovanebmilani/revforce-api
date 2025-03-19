from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config.application import get_http_client
from app.config.database import create_tables
from app.routers import insights, todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()

    yield  # Server start taking requests

    # shutdown logic
    await get_http_client().aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(todos.router)
app.include_router(insights.router)
