"""Tests for JarvisLLM."""
import pytest
from unittest.mock import patch, MagicMock

from src.core.jarvis_llm import JarvisLLM
from src.core.function_caller import FunctionCaller
from src.hardware.esp32_controller import ESP32Controller
from src.hardware.sensor_reader import SensorReader


@pytest.fixture
def llm(config):
    fc = FunctionCaller(esp32=ESP32Controller(mock=True), sensor=SensorReader(mock=True))
    return JarvisLLM(config=config, function_caller=fc)


class TestFallbackResponse:
    """Test the fallback responses when Ollama is unavailable."""

    def test_turn_on_light_fallback(self, llm):
        resp = llm._fallback_response("turn on the light")
        assert "turn_on_light" in resp

    def test_turn_off_light_fallback(self, llm):
        resp = llm._fallback_response("turn off the light")
        assert "turn_off_light" in resp

    def test_fan_speed_fallback(self, llm):
        resp = llm._fallback_response("set fan to 70%")
        assert "set_fan_speed" in resp

    def test_temperature_fallback(self, llm):
        resp = llm._fallback_response("what is the temperature")
        assert "get_room_conditions" in resp

    def test_time_fallback(self, llm):
        resp = llm._fallback_response("what time is it")
        assert "get_time" in resp

    def test_day_fallback(self, llm):
        resp = llm._fallback_response("what day is it")
        assert "get_day" in resp

    def test_greeting_fallback(self, llm):
        resp = llm._fallback_response("good morning")
        assert "Sir" in resp


class TestStripToolCalls:
    def test_removes_call_from_response(self):
        text = "Turning on the light. CALL: turn_on_light()"
        result = JarvisLLM._strip_tool_calls(text)
        assert "CALL:" not in result
        assert "Turning on the light" in result

    def test_no_calls_unchanged(self):
        text = "Hello, how can I help?"
        assert JarvisLLM._strip_tool_calls(text) == text


class TestChat:
    def test_chat_uses_fallback_when_ollama_unavailable(self, llm):
        """Chat should work even without Ollama by using fallback."""
        with patch("requests.post", side_effect=ConnectionError):
            response = llm.chat("turn on the light")
        assert response is not None
        assert len(response) > 0

    def test_history_grows_after_chat(self, llm):
        with patch("requests.post", side_effect=ConnectionError):
            llm.chat("hello")
        assert len(llm.history) == 2  # user + assistant

    def test_clear_history(self, llm):
        with patch("requests.post", side_effect=ConnectionError):
            llm.chat("hello")
        llm.clear_history()
        assert len(llm.history) == 0

    def test_set_presence(self, llm):
        llm.set_presence("AWAY")
        assert llm._presence_state == "AWAY"


class TestIntentClassification:
    def test_control_intent(self, llm):
        intent, _ = llm.intent_classifier.classify_with_confidence("turn on the light")
        assert intent == "CONTROL"

    def test_query_intent(self, llm):
        intent, _ = llm.intent_classifier.classify_with_confidence("what is the temperature")
        assert intent == "QUERY"

    def test_greeting_intent(self, llm):
        intent, _ = llm.intent_classifier.classify_with_confidence("good morning")
        assert intent == "GREETING"

    def test_context_intent(self, llm):
        intent, _ = llm.intent_classifier.classify_with_confidence("I'm leaving")
        assert intent == "CONTEXT"
