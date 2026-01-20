"""Application configuration."""

from __future__ import annotations

import importlib.util
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
    tts: TtsSettings


@dataclass(frozen=True)
class TtsSettings:
    """Typed configuration for TTS workers."""

    engine: str
    models_path: Path | None
    default_model: str | None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a mapping.")
    return data


def load_settings(config_path: str = DEFAULT_CONFIG_PATH) -> Settings:
    """Load settings from YAML, failing fast on errors."""

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    config = _load_yaml(path)

    logging_config = config.get("logging")
    if isinstance(logging_config, dict):
        log_directory = logging_config.get("directory", DEFAULT_LOG_DIRECTORY)
    else:
        log_directory = DEFAULT_LOG_DIRECTORY

    tts_config = config.get("tts")
    if not isinstance(tts_config, dict):
        raise ValueError("Missing or invalid 'tts' configuration.")
    engine = tts_config.get("engine")
    if engine not in {"piper", "dummy"}:
        raise ValueError("TTS engine must be 'piper' or 'dummy'.")
    models_path_value = tts_config.get("models_path")
    default_model = tts_config.get("default_model")
    models_path = Path(models_path_value) if models_path_value else None
    if engine == "piper":
        if not models_path_value or not default_model:
            raise ValueError(
                "Piper TTS requires 'models_path' and 'default_model' in config."
            )
        if not models_path or not models_path.is_dir():
            raise ValueError(f"Piper models_path must be a directory: {models_path}")
        model_path = models_path / f"{default_model}.onnx"
        if not model_path.is_file():
            raise ValueError(f"Piper default model not found: {model_path}")
        if importlib.util.find_spec("piper") is None:
            raise RuntimeError("Piper module is not installed.")

    tts_settings = TtsSettings(
        engine=engine,
        models_path=models_path,
        default_model=default_model,
    )

    return Settings(log_directory=Path(log_directory), tts=tts_settings)
