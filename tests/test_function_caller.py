"""Tests for FunctionCaller."""
import pytest

from src.core.function_caller import FunctionCaller, _parse_args
from src.hardware.esp32_controller import ESP32Controller
from src.hardware.sensor_reader import SensorReader


@pytest.fixture
def caller():
    return FunctionCaller(
        esp32=ESP32Controller(mock=True),
        sensor=SensorReader(mock=True),
    )


class TestParseArgs:
    def test_single_param(self):
        assert _parse_args("speed=50") == {"speed": "50"}

    def test_multiple_params(self):
        result = _parse_args("speed=50, name=fan")
        assert result["speed"] == "50"
        assert result["name"] == "fan"

    def test_empty(self):
        assert _parse_args("") == {}

    def test_quoted_value(self):
        result = _parse_args('message="hello world"')
        assert result["message"] == "hello world"


class TestExtractCalls:
    def test_no_calls(self, caller):
        assert caller.extract_calls("Hello, Sir!") == []

    def test_single_call_no_params(self, caller):
        calls = caller.extract_calls("Turning on light. CALL: turn_on_light()")
        assert len(calls) == 1
        assert calls[0]["tool"] == "turn_on_light"
        assert calls[0]["args"] == {}

    def test_call_with_params(self, caller):
        calls = caller.extract_calls("CALL: set_fan_speed(speed=70)")
        assert len(calls) == 1
        assert calls[0]["tool"] == "set_fan_speed"
        assert calls[0]["args"]["speed"] == "70"

    def test_multiple_calls(self, caller):
        text = "CALL: turn_on_light()\nCALL: set_fan_speed(speed=50)"
        calls = caller.extract_calls(text)
        assert len(calls) == 2

    def test_say_call(self, caller):
        calls = caller.extract_calls('CALL: say(message="Good morning")')
        assert len(calls) == 1
        assert calls[0]["args"]["message"] == "Good morning"


class TestExecute:
    def test_turn_on_light(self, caller):
        result = caller.execute("turn_on_light", {})
        assert result["success"] is True
        assert caller.esp32.light_state is True

    def test_turn_off_light(self, caller):
        result = caller.execute("turn_off_light", {})
        assert result["success"] is True
        assert caller.esp32.light_state is False

    def test_set_fan_speed(self, caller):
        result = caller.execute("set_fan_speed", {"speed": "75"})
        assert result["success"] is True
        assert caller.esp32.fan_speed == 75

    def test_set_fan_speed_clamps_max(self, caller):
        result = caller.execute("set_fan_speed", {"speed": "150"})
        assert result["success"] is True
        assert caller.esp32.fan_speed == 100

    def test_set_fan_speed_clamps_min(self, caller):
        result = caller.execute("set_fan_speed", {"speed": "-10"})
        assert result["success"] is True
        assert caller.esp32.fan_speed == 0

    def test_get_room_conditions(self, caller):
        result = caller.execute("get_room_conditions", {})
        assert result["success"] is True
        assert "temperature" in result["data"]
        assert "humidity" in result["data"]
        assert "time" in result["data"]
        assert "day" in result["data"]

    def test_get_time(self, caller):
        result = caller.execute("get_time", {})
        assert result["success"] is True
        assert "time" in result

    def test_get_day(self, caller):
        result = caller.execute("get_day", {})
        assert result["success"] is True
        assert "day" in result

    def test_predict_comfort(self, caller):
        result = caller.execute("predict_comfort", {})
        assert result["success"] is True
        assert "comfort" in result

    def test_say(self, caller):
        result = caller.execute("say", {"message": "Test message"})
        assert result["success"] is True
        assert result["spoken"] == "Test message"

    def test_unknown_tool(self, caller):
        result = caller.execute("nonexistent_tool", {})
        assert result["success"] is False
        assert "error" in result


class TestExecuteAll:
    def test_executes_all_calls(self, caller):
        text = "CALL: turn_on_light()\nCALL: set_fan_speed(speed=50)"
        results = caller.execute_all(text)
        assert len(results) == 2
        assert all(r["success"] for r in results)
