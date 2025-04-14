import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from crudik.bootstrap.di.container import get_async_container
from crudik.presentation.http import include_exception_handlers, include_routers

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console"],
    },
    "python_multipart.multipart": {
        "level": "ERROR",
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


app = FastAPI(
    lifespan=lifespan,
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

container = get_async_container()

setup_dishka(container=container, app=app)

logging.info("Fastapi app created.")

include_routers(app)
include_exception_handlers(app)


def run_api(_argv: list[str]) -> None:
    bind = "REDACTED"
    uvicorn.run(
        app,
        port=int(os.environ["SERVER_PORT"]),
        host=bind,
        log_config=log_config,
        access_log=False,
    )


if __name__ == "__main__":
    run_api(sys.argv)
