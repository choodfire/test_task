import logging

from fastapi import FastAPI

from app.api.v1.tasks import router as tasks_router
from app.core.config import settings
from app.core.logger import init_logger

logger = logging.getLogger()


def create_app() -> FastAPI:
    init_logger()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}openapi.json",
    )

    app.include_router(tasks_router, prefix=settings.API_V1_STR)

    logger.info("initialized app")

    return app


app = create_app()
