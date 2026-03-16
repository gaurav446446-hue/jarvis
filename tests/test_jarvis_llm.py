"""Tests for JarvisLLM."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.core.jarvis_llm import JarvisLLM
from src.intelligence.appliance_controller import ApplianceController
from src.hardware.sensor_reader import SensorReader
from src.utils.constants import DeviceState


@pytest.fixture()
def ctrl() -> ApplianceController:
    return ApplianceController()


@pytest.fixture()
def sensor() -> SensorReader:
    return SensorReader(temperature=24.0, humidity=65.0, motion_probability=0.0)


@pytest.fixture()
def llm(ctrl, sensor) -> JarvisLLM:
    return JarvisLLM(appliance_controller=ctrl, sensor_reader=sensor)


class TestGreetingIntent:
    def test_good_morning(self, llm):
        response = llm.chat("Good morning")
        assert response
        assert isinstance(response, str)

    def test_hello(self, llm):
        response = llm.chat("Hello Jarvis")
        assert "Sir" in response or "help" in response.lower()


class TestControlIntent:
    def test_turn_on_light(self, llm, ctrl):
        llm.chat("Turn on the light")
        assert ctrl.light_state == DeviceState.ON

    def test_turn_off_light(self, llm, ctrl):
        ctrl.turn_on_light()
        llm.chat("Turn off the light")
        assert ctrl.light_state == DeviceState.OFF

    def test_set_fan_speed(self, llm, ctrl):
        llm.chat("Set fan speed to 75%")
        assert ctrl.fan_speed == 75


class TestQueryIntent:
    def test_time_query(self, llm):
        response = llm.chat("What's the time?")
        assert response
        # Response should mention AM or PM or HH:MM
        assert any(char in response for char in [":", "AM", "PM", "time", "Time"])

    def test_temperature_query(self, llm):
        response = llm.chat("What's the temperature?")
        assert response
        assert "24" in response or "°C" in response or "temperature" in response.lower()


class TestContextIntent:
    def test_arrival(self, llm, ctrl):
        llm.chat("I'm home")
        assert ctrl.light_state == DeviceState.ON

    def test_departure(self, llm, ctrl):
        ctrl.turn_on_light()
        ctrl.set_fan_speed(50)
        llm.chat("I'm leaving")
        assert ctrl.light_state == DeviceState.OFF
        assert ctrl.fan_speed == 0


class TestComfortIntent:
    def test_too_hot(self, llm, ctrl):
        llm.chat("It's too hot")
        assert ctrl.fan_speed > 50

    def test_too_cold(self, llm, ctrl):
        ctrl.set_fan_speed(75)
        llm.chat("Too cold")
        assert ctrl.fan_speed <= 50


class TestHistory:
    def test_history_grows(self, llm):
        llm.chat("Hello")
        llm.chat("Turn on the light")
        assert len(llm.history) >= 2

    def test_reset_clears_history(self, llm):
        llm.chat("Hello")
        llm.reset_history()
        assert llm.history == []


class TestEdgeCases:
    def test_empty_input(self, llm):
        response = llm.chat("")
        assert response  # Should still return something

    def test_whitespace_input(self, llm):
        response = llm.chat("   ")
        assert response

    def test_unknown_input_returns_response(self, llm):
        response = llm.chat("xyzzy frobznittle")
        # Should return fallback (LLM or generic)
        assert isinstance(response, str)
