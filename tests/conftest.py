"""Test configuration and shared fixtures."""
import os
import sys
import pytest
import tempfile
import json

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.config import Config
from src.intelligence.memory_manager import MemoryManager


@pytest.fixture
def tmp_dir(tmp_path):
    """Provide a temporary directory."""
    return tmp_path


@pytest.fixture
def config(tmp_path):
    """Provide a Config instance that uses a temporary directory."""
    cfg_data = {
        "jarvis": {"name": "Jarvis", "version": "1.0.0", "user": "TestUser"},
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
            "timeout": 5,
            "max_tokens": 128,
        },
        "presence": {"away_timeout_minutes": 120, "check_interval_seconds": 30},
        "logging": {
            "level": "DEBUG",
            "log_dir": str(tmp_path),
            "events_log": str(tmp_path / "events_log.jsonl"),
            "conversation_log": str(tmp_path / "conversation_history.jsonl"),
        },
        "paths": {
            "models_dir": str(tmp_path / "models"),
            "data_dir": str(tmp_path / "data"),
            "user_profile": str(tmp_path / "models" / "user_profile.json"),
            "behavior_patterns": str(tmp_path / "models" / "behavior_patterns.json"),
        },
    }

    cfg_path = tmp_path / "config.yaml"
    import yaml
    cfg_path.write_text(yaml.dump(cfg_data))

    return Config(config_path=str(cfg_path))


@pytest.fixture
def memory(config):
    """Provide a MemoryManager with temp paths."""
    return MemoryManager(config)
