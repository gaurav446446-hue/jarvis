"""Tests for ApplianceController."""
from __future__ import annotations

import pytest

from src.intelligence.appliance_controller import ApplianceController
from src.utils.constants import DeviceState


@pytest.fixture()
def ctrl() -> ApplianceController:
    return ApplianceController()


class TestLightControl:
    def test_initial_state_off(self, ctrl):
        assert ctrl.light_state == DeviceState.OFF

    def test_turn_on(self, ctrl):
        ctrl.turn_on_light()
        assert ctrl.light_state == DeviceState.ON

    def test_turn_off(self, ctrl):
        ctrl.turn_on_light()
        ctrl.turn_off_light()
        assert ctrl.light_state == DeviceState.OFF

    def test_turn_on_returns_state_dict(self, ctrl):
        result = ctrl.turn_on_light()
        assert result["light"] == "on"

    def test_custom_brightness(self, ctrl):
        ctrl.turn_on_light(brightness=50)
        assert ctrl.light_brightness == 50

    def test_brightness_clamped_to_100(self, ctrl):
        ctrl.turn_on_light(brightness=200)
        assert ctrl.light_brightness == 100

    def test_brightness_clamped_to_0(self, ctrl):
        ctrl.turn_on_light(brightness=-10)
        assert ctrl.light_brightness == 0


class TestFanControl:
    def test_initial_fan_speed_zero(self, ctrl):
        assert ctrl.fan_speed == 0

    def test_set_fan_speed_50(self, ctrl):
        ctrl.set_fan_speed(50)
        assert ctrl.fan_speed == 50

    def test_set_fan_speed_100(self, ctrl):
        ctrl.set_fan_speed(100)
        assert ctrl.fan_speed == 100

    def test_set_fan_speed_0(self, ctrl):
        ctrl.set_fan_speed(0)
        assert ctrl.fan_speed == 0

    def test_invalid_speed_above_100(self, ctrl):
        with pytest.raises(ValueError):
            ctrl.set_fan_speed(101)

    def test_invalid_speed_negative(self, ctrl):
        with pytest.raises(ValueError):
            ctrl.set_fan_speed(-1)

    def test_set_fan_returns_state_dict(self, ctrl):
        result = ctrl.set_fan_speed(75)
        assert result["fan_speed"] == 75


class TestGetState:
    def test_get_state_returns_dict(self, ctrl):
        state = ctrl.get_state()
        assert "light" in state
        assert "fan_speed" in state

    def test_turn_off_all(self, ctrl):
        ctrl.turn_on_light()
        ctrl.set_fan_speed(80)
        ctrl.turn_off_all()
        assert ctrl.light_state == DeviceState.OFF
        assert ctrl.fan_speed == 0


class TestFadeIn:
    def test_fade_in_turns_on_light(self, ctrl):
        ctrl.fade_in(duration=0.1, target_brightness=80)
        assert ctrl.light_state == DeviceState.ON

    def test_fade_in_reaches_target_brightness(self, ctrl):
        ctrl.fade_in(duration=0.1, target_brightness=60)
        assert ctrl.light_brightness == 60
