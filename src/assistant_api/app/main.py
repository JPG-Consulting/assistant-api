"""Application entrypoint module."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI

from assistant_api.app.settings import load_settings

if TYPE_CHECKING:
    from assistant_api.app.settings import Settings

LOG_FILENAME = "assistant-api.log"


def configure_logging(settings: Settings) -> None:
    log_directory = Path(settings.log_directory)
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / LOG_FILENAME

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)


def create_app() -> FastAPI:
    settings = load_settings()
    configure_logging(settings)

    app = FastAPI()
    logger = logging.getLogger(__name__)

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting application.")

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down application.")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
