import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.system import router as health_router
from services.auth.router import router as auth_router
from services.document.router import router as document_router
from services.query.router import router as query_router
from shared.config import settings
from shared.constant import API_DESCRIPTION, API_TITLE, API_V1_PREFIX, APP_VERSION

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("startup environment=%s", settings.environment)
    yield
    logger.info("Shutdown")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.include_router(health_router, tags=["system"])
app.include_router(auth_router, prefix=f"{API_V1_PREFIX}/auth", tags=["auth"])
app.include_router(document_router, prefix=f"{API_V1_PREFIX}/document", tags=["document"])
app.include_router(query_router, prefix=f"{API_V1_PREFIX}/query", tags=["query"])
