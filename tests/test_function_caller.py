"""Tests for FunctionCaller."""
from __future__ import annotations

import pytest

from src.core.function_caller import FunctionCaller, _coerce
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
def fc(ctrl, sensor) -> FunctionCaller:
    return FunctionCaller(appliance_controller=ctrl, sensor_reader=sensor)


class TestLightFunctions:
    def test_turn_on_light(self, fc, ctrl):
        result = fc.execute("turn_on_light")
        assert result["state"] == "on"
        assert ctrl.light_state == DeviceState.ON

    def test_turn_off_light(self, fc, ctrl):
        ctrl.turn_on_light()
        result = fc.execute("turn_off_light")
        assert result["state"] == "off"
        assert ctrl.light_state == DeviceState.OFF


class TestFanFunctions:
    def test_set_fan_speed_valid(self, fc, ctrl):
        result = fc.execute("set_fan_speed", speed=75)
        assert result["speed"] == 75
        assert ctrl.fan_speed == 75

    def test_set_fan_speed_zero(self, fc, ctrl):
        result = fc.execute("set_fan_speed", speed=0)
        assert result["speed"] == 0

    def test_set_fan_speed_invalid_above_100(self, fc):
        result = fc.execute("set_fan_speed", speed=150)
        assert result["status"] == "error"

    def test_set_fan_speed_invalid_negative(self, fc):
        result = fc.execute("set_fan_speed", speed=-5)
        assert result["status"] == "error"

    def test_set_fan_speed_non_integer(self, fc):
        result = fc.execute("set_fan_speed", speed="bad")
        assert result["status"] == "error"


class TestQueryFunctions:
    def test_get_room_conditions(self, fc):
        result = fc.execute("get_room_conditions")
        assert "temperature" in result
        assert "humidity" in result

    def test_get_time(self, fc):
        result = fc.execute("get_time")
        assert "time" in result
        assert ":" in result["time"]

    def test_get_day(self, fc):
        result = fc.execute("get_day")
        assert "day" in result
        assert isinstance(result["weekday"], bool)

    def test_predict_comfort(self, fc):
        result = fc.execute("predict_comfort")
        assert "comfortable" in result
        assert isinstance(result["comfortable"], bool)


class TestSayFunction:
    def test_say_returns_ok(self, fc):
        result = fc.execute("say", message="Hello")
        assert result["status"] == "ok"
        assert result["said"] == "Hello"


class TestUnknownFunction:
    def test_unknown_returns_error(self, fc):
        result = fc.execute("nonexistent_function")
        assert result["status"] == "error"


class TestParseCall:
    def test_simple_call_no_args(self, fc):
        parsed = fc.parse_call("turn_on_light()")
        assert parsed is not None
        fn, kwargs = parsed
        assert fn == "turn_on_light"
        assert kwargs == {}

    def test_call_with_int_arg(self, fc):
        parsed = fc.parse_call("set_fan_speed(speed=75)")
        assert parsed is not None
        fn, kwargs = parsed
        assert fn == "set_fan_speed"
        assert kwargs["speed"] == 75

    def test_call_with_string_arg(self, fc):
        parsed = fc.parse_call("say(message='Hello Sir')")
        assert parsed is not None
        fn, kwargs = parsed
        assert fn == "say"
        assert kwargs["message"] == "Hello Sir"

    def test_no_call_returns_none(self, fc):
        result = fc.parse_call("just some text without a call")
        assert result is None


class TestExecuteFromText:
    def test_execute_embedded_call(self, fc, ctrl):
        result = fc.execute_from_text("Please turn_on_light() for me")
        assert result is not None
        assert ctrl.light_state == DeviceState.ON


class TestCoerce:
    def test_coerce_int(self):
        assert _coerce("42") == 42

    def test_coerce_float(self):
        assert _coerce("3.14") == 3.14

    def test_coerce_true(self):
        assert _coerce("true") is True

    def test_coerce_false(self):
        assert _coerce("false") is False

    def test_coerce_string(self):
        assert _coerce("hello") == "hello"


class TestAvailableFunctions:
    def test_returns_list(self, fc):
        fns = fc.available_functions()
        assert isinstance(fns, list)
        assert "turn_on_light" in fns
        assert "set_fan_speed" in fns
