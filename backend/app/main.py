import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.loader import initialize_database
from app.api.chat import router as chat_router
from app.api.health import router as health_router

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_path = settings.data_path
    if not os.path.isabs(data_path):
        data_path = os.path.join(os.path.dirname(__file__), "..", data_path)
    data_path = os.path.normpath(data_path)

    try:
        initialize_database(data_path)
        logger.info("Application started successfully")
    except FileNotFoundError as e:
        logger.error("Startup error: %s", e)
    except Exception as e:
        logger.exception("Failed to initialize database: %s", e)

    yield

    from app.db.database import db_manager
    db_manager.close()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="NYC 311 Analytics Agent",
    description="AI-powered data analytics for NYC 311 service requests",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "NYC 311 Analytics Agent API", "docs": "/docs"}
