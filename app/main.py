import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.application import get_http_client
from app.config.database import engine
from app.routers import insights, account, account_config, chart, refresh, campaign, ad, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(lambda conn: None)

    yield  # Server start taking requests

    # shutdown logic
    await get_http_client().aclose()


app = FastAPI(lifespan=lifespan)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(insights.router)
app.include_router(account.router)
app.include_router(account_config.router)
app.include_router(chart.router)
app.include_router(refresh.router)
app.include_router(ad.router)
app.include_router(campaign.router)
app.include_router(chat.router)
