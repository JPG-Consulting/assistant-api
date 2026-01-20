"""Application entrypoint module."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI

from assistant_api.app.api.v1 import api_router
from assistant_api.app.core.prewarm import get_prewarm_manager
from assistant_api.app.settings import DEFAULT_CONFIG_PATH, load_settings

if TYPE_CHECKING:
    from assistant_api.app.settings import Settings

LOG_FILENAME = "assistant-api.log"


def resolve_config_path(argv: list[str] | None = None) -> Path:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", dest="config_path")
    args, _ = parser.parse_known_args(argv)
    if args.config_path:
        return Path(args.config_path)
    return Path(DEFAULT_CONFIG_PATH)


def load_settings_or_exit(config_path: Path) -> Settings:
    try:
        return load_settings(config_path=str(config_path))
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


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
    config_path = resolve_config_path(sys.argv[1:])
    settings = load_settings_or_exit(config_path)
    configure_logging(settings)

    app = FastAPI()
    app.state.settings = settings
    app.state.config_path = str(config_path)
    logger = logging.getLogger(__name__)
    logger.info(
        "TTS configuration: engine=%s models_path=%s default_model=%s",
        settings.tts.engine,
        settings.tts.models_path,
        settings.tts.default_model,
    )

    @app.on_event("startup")
    async def on_startup() -> None:
        logger.info("Starting application.")
        prewarm_manager = get_prewarm_manager()
        default_resources = ("tts:default", "tts:piper:default")
        for resource_id in default_resources:
            prewarm_manager.register_default_resource(resource_id)
        logger.info(
            "Registered default prewarm resources: %s",
            ", ".join(default_resources),
        )

    @app.on_event("shutdown")
    async def on_shutdown() -> None:
        logger.info("Shutting down application.")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router)

    return app


app = create_app()
