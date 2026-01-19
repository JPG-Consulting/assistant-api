"""Application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = "/etc/assistant-api/config.yaml"
DEFAULT_LOG_DIRECTORY = "/var/log/assistant-api"


@dataclass(frozen=True)
class Settings:
    """Typed configuration for the application."""

    log_directory: Path


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        return {}
    return data


def load_settings(config_path: str = DEFAULT_CONFIG_PATH) -> Settings:
    """Load settings from YAML, falling back to defaults if missing."""

    path = Path(config_path)
    config = _load_yaml(path)

    logging_config = config.get("logging")
    if isinstance(logging_config, dict):
        log_directory = logging_config.get("directory", DEFAULT_LOG_DIRECTORY)
    else:
        log_directory = DEFAULT_LOG_DIRECTORY

    return Settings(log_directory=Path(log_directory))
