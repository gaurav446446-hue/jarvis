"""Main LLM orchestrator for Jarvis AI."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from src.core.function_caller import FunctionCaller
from src.core.intent_classifier import IntentClassifier
from src.core.prompt_builder import (
    build_assistant_message,
    build_system_prompt,
    build_user_message,
)
from src.utils.constants import Intent
from src.utils.logger import get_logger

logger = get_logger("jarvis_llm")

try:
    import ollama as _ollama_lib
    _OLLAMA_AVAILABLE = True
except ImportError:
    _OLLAMA_AVAILABLE = False

_CALL_RE = re.compile(r"CALL:\s*(\w+\([^)]*\))", re.IGNORECASE)


class JarvisLLM:
    """Orchestrates intent classification, function calling, and LLM responses.

    When Ollama is not available the system falls back to template-based
    replies so the assistant is still useful without a local LLM.

    Args:
        appliance_controller: Optional :class:`ApplianceController` instance.
        sensor_reader: Optional :class:`SensorReader` instance.
        voice_processor: Optional :class:`VoiceProcessor` instance.
        model: Ollama model name (default: ``"mistral"``).
        max_history: Maximum conversation turns to retain.
    """

    def __init__(
        self,
        appliance_controller=None,
        sensor_reader=None,
        voice_processor=None,
        model: str = "mistral",
        max_history: int = 20,
    ) -> None:
        self._model = model
        self._max_history = max_history
        self._history: List[Dict[str, str]] = []

        self._classifier = IntentClassifier()
        self._caller = FunctionCaller(
            appliance_controller=appliance_controller,
            sensor_reader=sensor_reader,
            voice_processor=voice_processor,
        )
        self._appliance = appliance_controller
        self._sensor = sensor_reader

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_input: str) -> str:
        """Process *user_input* and return Jarvis's response.

        Args:
            user_input: Raw text from the user.

        Returns:
            Response string to present to the user.
        """
        user_input = user_input.strip()
        if not user_input:
            return "I didn't catch that, Sir. Could you please repeat?"

        intent, params = self._classifier.classify(user_input)
        logger.debug("Intent: %s, params: %s", intent, params)

        # Handle purely local intents without calling the LLM.
        quick = self._handle_locally(intent, params, user_input)
        if quick is not None:
            self._append_history(user_input, quick)
            return quick

        # Attempt LLM completion.
        response = self._llm_complete(user_input)

        # Execute any CALL: directives embedded in the LLM output.
        response = self._process_calls(response)

        self._append_history(user_input, response)
        return response

    def reset_history(self) -> None:
        """Clear conversation history."""
        self._history.clear()

    @property
    def history(self) -> List[Dict[str, str]]:
        return list(self._history)

    # ------------------------------------------------------------------
    # Local (non-LLM) intent handlers
    # ------------------------------------------------------------------

    def _handle_locally(
        self, intent: Intent, params: Dict[str, Any], raw: str
    ) -> Optional[str]:
        """Return a response string for simple intents, or ``None`` to fall through to LLM."""
        if intent == Intent.GREETING:
            return self._caller.execute("say", message=f"Hello, Sir! How can I help you?")["said"]

        if intent == Intent.CONTROL:
            return self._handle_control(params, raw)

        if intent == Intent.QUERY:
            return self._handle_query(raw)

        if intent == Intent.CONTEXT:
            return self._handle_context(params)

        if intent == Intent.COMFORT:
            return self._handle_comfort(params, raw)

        return None  # fallthrough to LLM

    def _handle_control(self, params: Dict[str, Any], raw: str) -> str:
        device = params.get("device", "")
        action = params.get("action", "")
        value = params.get("value")

        if device == "light":
            if action in ("turn_on", "on"):
                result = self._caller.execute("turn_on_light")
                return f"Light turned on, Sir."
            if action in ("turn_off", "off"):
                result = self._caller.execute("turn_off_light")
                return f"Light turned off, Sir."
        if device == "fan":
            if action == "set" and value is not None:
                self._caller.execute("set_fan_speed", speed=value)
                return f"Fan speed set to {value}%, Sir."
            if action in ("turn_on",):
                self._caller.execute("set_fan_speed", speed=50)
                return "Fan turned on at 50%, Sir."
            if action in ("turn_off",):
                self._caller.execute("set_fan_speed", speed=0)
                return "Fan turned off, Sir."

        # Try to parse a speed value from raw text when device is fan
        speed_match = re.search(r"(\d{1,3})\s*%", raw)
        if "fan" in raw.lower() and speed_match:
            speed = int(speed_match.group(1))
            self._caller.execute("set_fan_speed", speed=speed)
            return f"Fan speed set to {speed}%, Sir."

        # Turn on/off by keyword when device unclear
        if re.search(r"\bturn\s+on\b", raw, re.IGNORECASE):
            self._caller.execute("turn_on_light")
            return "Light turned on, Sir."
        if re.search(r"\bturn\s+off\b", raw, re.IGNORECASE):
            self._caller.execute("turn_off_light")
            return "Light turned off, Sir."

        return f"I'll take care of that, Sir."

    def _handle_query(self, raw: str) -> str:
        raw_lower = raw.lower()
        if any(w in raw_lower for w in ("time",)):
            result = self._caller.execute("get_time")
            return f"The current time is {result['time_full']}, Sir."
        if any(w in raw_lower for w in ("day", "date", "weekday")):
            result = self._caller.execute("get_day")
            return f"Today is {result['day']}, {result['date']}, Sir."
        if any(w in raw_lower for w in ("temperature", "temp", "humidity", "condition", "room")):
            result = self._caller.execute("get_room_conditions")
            temp = result.get("temperature", "N/A")
            hum = result.get("humidity", "N/A")
            return f"Room temperature is {temp}°C and humidity is {hum}%, Sir."
        if "status" in raw_lower:
            cond = self._caller.execute("get_room_conditions")
            comfort = self._caller.execute("predict_comfort")
            return (
                f"Room is {cond['temperature']}°C, {cond['humidity']}% humidity. "
                f"Comfort: {'✓' if comfort['comfortable'] else '✗'}. "
                + (comfort.get("suggestion") or "")
            )
        return "I can tell you the time, temperature, or room status, Sir."

    def _handle_context(self, params: Dict[str, Any]) -> str:
        event = params.get("event", "")
        if event == "arrival":
            self._caller.execute("turn_on_light")
            self._caller.execute("set_fan_speed", speed=50)
            return "Welcome home, Sir! Light on and fan set to 50%."
        if event == "departure":
            self._caller.execute("turn_off_light")
            self._caller.execute("set_fan_speed", speed=0)
            return "Goodbye, Sir! Lights off and fan off."
        return "Noted, Sir."

    def _handle_comfort(self, params: Dict[str, Any], raw: str) -> str:
        raw_lower = raw.lower()
        if any(w in raw_lower for w in ("hot", "warm", "stuffy")):
            self._caller.execute("set_fan_speed", speed=75)
            return "Increased fan to 75% to cool things down, Sir."
        if any(w in raw_lower for w in ("cold", "cool", "freezing")):
            self._caller.execute("set_fan_speed", speed=25)
            return "Reduced fan to 25% for more warmth, Sir."
        result = self._caller.execute("predict_comfort")
        sug = result.get("suggestion") or "Conditions are comfortable."
        return f"{sug}"

    # ------------------------------------------------------------------
    # LLM integration
    # ------------------------------------------------------------------

    def _llm_complete(self, user_input: str) -> str:
        if not _OLLAMA_AVAILABLE:
            return self._fallback_response(user_input)
        try:
            system_prompt = build_system_prompt(
                tools=self._caller.available_functions()
            )
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self._history[-self._max_history:])
            messages.append(build_user_message(user_input))
            response = _ollama_lib.chat(model=self._model, messages=messages)
            return response["message"]["content"].strip()
        except Exception as exc:
            logger.warning("Ollama error: %s – using fallback", exc)
            return self._fallback_response(user_input)

    def _fallback_response(self, user_input: str) -> str:
        """Return a generic helpful response when LLM is unavailable."""
        return (
            f"I understand, Sir. Unfortunately my language model is not available "
            f"right now. You can still control the room using direct commands like "
            f"'turn on light', 'set fan 50%', or 'room status'."
        )

    def _process_calls(self, response: str) -> str:
        """Find and execute CALL: directives in the LLM response."""
        lines = []
        for line in response.splitlines():
            m = _CALL_RE.search(line)
            if m:
                call_text = m.group(1)
                result = self._caller.execute_from_text(call_text)
                if result:
                    lines.append(f"[Executed: {call_text} → {result}]")
            else:
                lines.append(line)
        return "\n".join(lines).strip()

    def _append_history(self, user_input: str, response: str) -> None:
        self._history.append(build_user_message(user_input))
        self._history.append(build_assistant_message(response))
        if len(self._history) > self._max_history * 2:
            self._history = self._history[-(self._max_history * 2):]
