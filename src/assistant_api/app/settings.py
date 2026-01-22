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
    llm: LlmSettings
    assistant: AssistantSettings


@dataclass(frozen=True)
class TtsSettings:
    """Typed configuration for TTS workers."""

    engine: str
    models_path: Path | None
    default_model: str | None


@dataclass(frozen=True)
class LlmSettings:
    """Typed configuration for LLM providers."""

    provider: str
    model: str
    host: str
    temperature: float
    max_tokens: int
    persona: PersonaSettings


@dataclass(frozen=True)
class PersonaSettings:
    """Typed configuration for persona behavior."""

    enabled: bool
    content: str | None


@dataclass(frozen=True)
class AssistantSettings:
    """Typed configuration for assistant behavior."""

    default_language: str


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

    llm_config = config.get("llm")
    if not isinstance(llm_config, dict):
        raise ValueError("Missing or invalid 'llm' configuration.")
    provider = llm_config.get("provider", "ollama")
    if provider != "ollama":
        raise ValueError("LLM provider must be 'ollama'.")
    model = llm_config.get("model")
    if not model:
        raise ValueError("LLM config requires a 'model'.")
    host = llm_config.get("host", "http://localhost:11434")
    temperature = float(llm_config.get("temperature", 0.7))
    max_tokens = int(llm_config.get("max_tokens", 256))
    persona_config = llm_config.get("persona", {})
    if not isinstance(persona_config, dict):
        raise ValueError("LLM 'persona' must be a mapping.")
    persona_enabled = bool(persona_config.get("enabled", True))
    persona_file_value = persona_config.get("file")
    persona_file = Path(persona_file_value) if persona_file_value else None
    persona_content: str | None = None
    if persona_enabled:
        if not persona_file:
            raise ValueError("Persona is enabled but no persona file was provided.")
        if not persona_file.is_file():
            raise ValueError(f"Persona file not found: {persona_file}")
        try:
            content = persona_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ValueError(
                f"Persona file is not a readable text file: {persona_file}"
            ) from exc
        stripped = content.strip()
        if not stripped:
            raise ValueError(f"Persona file is empty: {persona_file}")
        persona_content = stripped
    persona_settings = PersonaSettings(enabled=persona_enabled, content=persona_content)

    llm_settings = LlmSettings(
        provider=provider,
        model=str(model),
        host=str(host),
        temperature=temperature,
        max_tokens=max_tokens,
        persona=persona_settings,
    )

    assistant_config = config.get("assistant", {})
    if not isinstance(assistant_config, dict):
        raise ValueError("Missing or invalid 'assistant' configuration.")
    language = assistant_config.get("default_language")
    if not isinstance(language, str) or not language.strip():
        raise ValueError("assistant.default_language must be a non-empty string.")
    assistant_settings = AssistantSettings(default_language=language.strip())

    return Settings(
        log_directory=Path(log_directory),
        tts=tts_settings,
        llm=llm_settings,
        assistant=assistant_settings,
    )
