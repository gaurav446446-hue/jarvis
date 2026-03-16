"""Configuration manager for Jarvis AI."""
import os
import yaml
from pathlib import Path


class Config:
    """Load and provide access to configuration from config.yaml."""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config.yaml",
            )
        self._config = self._load(config_path)
        self._ensure_dirs()

    def _load(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return self._defaults()

    def _defaults(self) -> dict:
        return {
            "jarvis": {"name": "Jarvis", "version": "1.0.0", "user": "Gaurav"},
            "user_profile": {
                "wake_times": {"weekday": "05:40", "weekend": "07:00"},
                "comfort_temp_min": 23,
                "comfort_temp_max": 25,
                "preferred_fan_speed": 50,
            },
            "llm": {
                "provider": "ollama",
                "model": "mistral",
                "host": "http://localhost:11434",
                "timeout": 30,
                "max_tokens": 512,
            },
            "presence": {"away_timeout_minutes": 120, "check_interval_seconds": 30},
            "logging": {
                "level": "INFO",
                "log_dir": "data",
                "events_log": "data/events_log.jsonl",
                "conversation_log": "data/conversation_history.jsonl",
            },
            "paths": {
                "models_dir": "models",
                "data_dir": "data",
                "user_profile": "models/user_profile.json",
                "behavior_patterns": "models/behavior_patterns.json",
            },
        }

    def _ensure_dirs(self):
        for key in ("models_dir", "data_dir"):
            path = self.get("paths", key)
            if path:
                Path(path).mkdir(parents=True, exist_ok=True)

    def get(self, *keys, default=None):
        """Retrieve a nested config value using dot-path keys."""
        val = self._config
        for key in keys:
            if not isinstance(val, dict):
                return default
            val = val.get(key, default)
        return val

    # Convenience properties
    @property
    def user_name(self) -> str:
        return self.get("jarvis", "user", default="Gaurav")

    @property
    def weekday_wake_time(self) -> str:
        return self.get("user_profile", "wake_times", "weekday", default="05:40")

    @property
    def weekend_wake_time(self) -> str:
        return self.get("user_profile", "wake_times", "weekend", default="07:00")

    @property
    def preferred_fan_speed(self) -> int:
        return self.get("user_profile", "preferred_fan_speed", default=50)

    @property
    def llm_model(self) -> str:
        return self.get("llm", "model", default="mistral")

    @property
    def llm_host(self) -> str:
        return self.get("llm", "host", default="http://localhost:11434")

    @property
    def away_timeout_minutes(self) -> int:
        return self.get("presence", "away_timeout_minutes", default=120)

    @property
    def user_profile_path(self) -> str:
        return self.get("paths", "user_profile", default="models/user_profile.json")

    @property
    def events_log_path(self) -> str:
        return self.get("logging", "events_log", default="data/events_log.jsonl")

    @property
    def conversation_log_path(self) -> str:
        return self.get("logging", "conversation_log", default="data/conversation_history.jsonl")
