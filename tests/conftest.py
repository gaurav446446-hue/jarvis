"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest

from src.intelligence.appliance_controller import ApplianceController
from src.intelligence.memory_manager import MemoryManager
from src.intelligence.wake_up_detector import WakeUpDetector
from src.intelligence.presence_detector import PresenceDetector
from src.core.intent_classifier import IntentClassifier
from src.core.function_caller import FunctionCaller
from src.core.jarvis_llm import JarvisLLM
from src.hardware.sensor_reader import SensorReader
from src.interfaces.voice_processor import VoiceProcessor


# ---------------------------------------------------------------------------
# Temporary data directory
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Return a temporary directory suitable for data files."""
    d = tmp_path / "data"
    d.mkdir()
    return d


# ---------------------------------------------------------------------------
# Core component fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def appliance() -> ApplianceController:
    return ApplianceController()


@pytest.fixture()
def sensor() -> SensorReader:
    return SensorReader(temperature=24.0, humidity=65.0, motion_probability=0.0)


@pytest.fixture()
def voice() -> MagicMock:
    mock = MagicMock(spec=VoiceProcessor)
    mock.say = MagicMock()
    return mock


@pytest.fixture()
def memory(tmp_data_dir: Path) -> MemoryManager:
    return MemoryManager(data_dir=str(tmp_data_dir))


@pytest.fixture()
def classifier() -> IntentClassifier:
    return IntentClassifier()


@pytest.fixture()
def caller(appliance: ApplianceController, sensor: SensorReader) -> FunctionCaller:
    return FunctionCaller(appliance_controller=appliance, sensor_reader=sensor)


@pytest.fixture()
def jarvis(appliance: ApplianceController, sensor: SensorReader) -> JarvisLLM:
    return JarvisLLM(appliance_controller=appliance, sensor_reader=sensor)


@pytest.fixture()
def wake_detector(appliance: ApplianceController, voice: MagicMock) -> WakeUpDetector:
    return WakeUpDetector(appliance_controller=appliance, voice_processor=voice)


@pytest.fixture()
def presence_detector(appliance: ApplianceController, voice: MagicMock) -> PresenceDetector:
    return PresenceDetector(appliance_controller=appliance, voice_processor=voice)


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_profile() -> dict:
    return {
        "user": {
            "name": "Sir",
            "wake_times": {"weekday": "05:40", "weekend": "07:00"},
            "comfort": {
                "temperature_range": [23, 25],
                "preferred_fan_speed": 50,
                "light_brightness": 80,
            },
            "timezone": "IST",
        }
    }


@pytest.fixture()
def mock_llm_response() -> str:
    return "I have turned on the light, Sir."
