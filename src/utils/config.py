"""Configuration loader for Jarvis AI."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:  # pragma: no cover
    _YAML_AVAILABLE = False

# Default config path relative to repository root
_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.yaml"


@dataclass
class UserComfort:
    temperature_min: int = 23
    temperature_max: int = 25
    preferred_fan_speed: int = 50


@dataclass
class UserConfig:
    name: str = "Sir"
    wake_time_weekday: str = "05:40"
    wake_time_weekend: str = "07:00"
    comfort: UserComfort = field(default_factory=UserComfort)


@dataclass
class LLMConfig:
    model: str = "mistral"
    local: bool = True
    offline: bool = True


@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "data/events_log.jsonl"
    console: bool = True


@dataclass
class Config:
    user: UserConfig = field(default_factory=UserConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Raw parsed dictionary kept for arbitrary access
    _raw: Dict[str, Any] = field(default_factory=dict, repr=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Dot-separated key lookup into the raw config dictionary."""
        parts = key.split(".")
        node: Any = self._raw
        for part in parts:
            if not isinstance(node, dict):
                return default
            node = node.get(part, default)
        return node


def _build_config(raw: Dict[str, Any]) -> Config:
    user_raw = raw.get("user", {})
    wake_times = user_raw.get("wake_times", {})
    comfort_raw = user_raw.get("comfort", {})
    comfort = UserComfort(
        temperature_min=comfort_raw.get("temperature_min", 23),
        temperature_max=comfort_raw.get("temperature_max", 25),
        preferred_fan_speed=comfort_raw.get("preferred_fan_speed", 50),
    )
    user = UserConfig(
        name=user_raw.get("name", "Sir"),
        wake_time_weekday=wake_times.get("weekday", "05:40"),
        wake_time_weekend=wake_times.get("weekend", "07:00"),
        comfort=comfort,
    )

    llm_raw = raw.get("llm", {})
    llm = LLMConfig(
        model=llm_raw.get("model", "mistral"),
        local=llm_raw.get("local", True),
        offline=llm_raw.get("offline", True),
    )

    log_raw = raw.get("logging", {})
    log_cfg = LoggingConfig(
        level=log_raw.get("level", "INFO"),
        file=log_raw.get("file", "data/events_log.jsonl"),
        console=log_raw.get("console", True),
    )

    return Config(user=user, llm=llm, logging=log_cfg, _raw=raw)


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from *config_path* (defaults to ``config.yaml``).

    Falls back to built-in defaults when the file is missing or YAML is not
    installed.

    Args:
        config_path: Explicit path to the YAML config file.

    Returns:
        Populated :class:`Config` dataclass.
    """
    path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH

    if not _YAML_AVAILABLE:
        return Config()

    if not path.exists():
        return Config()

    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw: Dict[str, Any] = yaml.safe_load(fh) or {}
        return _build_config(raw)
    except Exception:  # pragma: no cover
        return Config()


# Module-level singleton – import and use directly if desired.
_config_singleton: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Return the module-level :class:`Config` singleton."""
    global _config_singleton
    if _config_singleton is None:
        _config_singleton = load_config(config_path)
    return _config_singleton


def reset_config() -> None:
    """Reset the singleton (useful in tests)."""
    global _config_singleton
    _config_singleton = None
