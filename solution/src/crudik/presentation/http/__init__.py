import logging

from fastapi import FastAPI
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError

from crudik.domain.error.base import AppError
from crudik.presentation.http.endpoint.ad import router as ad_router
from crudik.presentation.http.endpoint.advertiser import (
    router as advertiser_router,
)
from crudik.presentation.http.endpoint.client import router as client_router
from crudik.presentation.http.endpoint.day import router as day_router
from crudik.presentation.http.endpoint.relevance import (
    router as relevance_router,
)
from crudik.presentation.http.endpoint.root import router as root_router
from crudik.presentation.http.endpoint.stats import router as stats_router
from crudik.presentation.http.exception_handlers import (
    app_exception_handler,
    dbapi_error_handler,
    validation_error_handler,
)


def include_routers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(client_router)
    app.include_router(advertiser_router)
    app.include_router(relevance_router)
    app.include_router(day_router)
    app.include_router(ad_router)
    app.include_router(stats_router)

    logging.debug("Routers was included.")


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_exception_handler)  # type: ignore
    app.add_exception_handler(DBAPIError, dbapi_error_handler)  # type: ignore
    app.add_exception_handler(ValidationError, validation_error_handler)  # type:ignore

    logging.debug("Exception handlers was included.")


__all__ = [
    "include_exception_handlers",
    "include_routers",
]
