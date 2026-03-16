"""Function caller – executes Jarvis tool functions from parsed calls."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger("function_caller")


class FunctionCaller:
    """Parse and execute function calls produced by the LLM or intent classifier.

    Each registered function is a plain Python callable stored in
    ``self._registry``.  The caller supports a lightweight text-based call
    syntax:  ``function_name(param1=value1, param2=value2)``
    """

    def __init__(self, appliance_controller=None, sensor_reader=None, voice_processor=None) -> None:
        self._appliance = appliance_controller
        self._sensor = sensor_reader
        self._voice = voice_processor
        self._registry: Dict[str, Any] = {}
        self._register_builtins()

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------

    def register(self, name: str, fn: Any) -> None:
        """Register a callable under *name*."""
        self._registry[name] = fn

    def _register_builtins(self) -> None:
        self._registry.update(
            {
                "turn_on_light": self._turn_on_light,
                "turn_off_light": self._turn_off_light,
                "set_fan_speed": self._set_fan_speed,
                "get_room_conditions": self._get_room_conditions,
                "get_time": self._get_time,
                "get_day": self._get_day,
                "predict_comfort": self._predict_comfort,
                "say": self._say,
            }
        )

    # ------------------------------------------------------------------
    # Built-in implementations
    # ------------------------------------------------------------------

    def _turn_on_light(self, **_kwargs) -> Dict[str, Any]:
        if self._appliance:
            self._appliance.turn_on_light()
        return {"status": "ok", "device": "light", "state": "on"}

    def _turn_off_light(self, **_kwargs) -> Dict[str, Any]:
        if self._appliance:
            self._appliance.turn_off_light()
        return {"status": "ok", "device": "light", "state": "off"}

    def _set_fan_speed(self, speed: int = 50, **_kwargs) -> Dict[str, Any]:
        try:
            speed = int(speed)
        except (TypeError, ValueError):
            return {"status": "error", "message": "speed must be an integer 0-100"}
        if not 0 <= speed <= 100:
            return {"status": "error", "message": "speed must be between 0 and 100"}
        if self._appliance:
            self._appliance.set_fan_speed(speed)
        return {"status": "ok", "device": "fan", "speed": speed}

    def _get_room_conditions(self, **_kwargs) -> Dict[str, Any]:
        if self._sensor:
            return self._sensor.get_conditions()
        return {"temperature": 24.0, "humidity": 65.0, "motion": False}

    def _get_time(self, **_kwargs) -> Dict[str, Any]:
        now = datetime.now()
        return {"time": now.strftime("%H:%M"), "time_full": now.strftime("%I:%M %p")}

    def _get_day(self, **_kwargs) -> Dict[str, Any]:
        now = datetime.now()
        return {"day": now.strftime("%A"), "date": now.strftime("%Y-%m-%d"), "weekday": now.weekday() < 5}

    def _predict_comfort(self, **_kwargs) -> Dict[str, Any]:
        conditions = self._get_room_conditions()
        temp = conditions.get("temperature", 24.0)
        humidity = conditions.get("humidity", 65.0)
        comfortable = 23 <= temp <= 25 and humidity <= 75
        suggestion = None
        if temp > 25:
            suggestion = "Consider increasing fan speed or lowering AC."
        elif temp < 23:
            suggestion = "Room is a bit cool – consider reducing fan speed."
        return {"comfortable": comfortable, "temperature": temp, "humidity": humidity, "suggestion": suggestion}

    def _say(self, message: str = "", **_kwargs) -> Dict[str, Any]:
        if self._voice:
            self._voice.say(message)
        else:
            print(f"Jarvis: {message}")
        return {"status": "ok", "said": message}

    # ------------------------------------------------------------------
    # Call parsing
    # ------------------------------------------------------------------

    def parse_call(self, text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Parse ``function_name(key=value, ...)`` from *text*.

        Returns ``(function_name, kwargs)`` or ``None`` if no call found.
        """
        pattern = r"(\w+)\(([^)]*)\)"
        match = re.search(pattern, text)
        if not match:
            return None
        fn_name = match.group(1)
        raw_args = match.group(2).strip()
        kwargs: Dict[str, Any] = {}
        if raw_args:
            for part in raw_args.split(","):
                part = part.strip()
                if "=" in part:
                    key, _, val = part.partition("=")
                    kwargs[key.strip()] = _coerce(val.strip())
                elif part:
                    # Positional string argument → stored as 'message'
                    kwargs["message"] = part.strip("'\"")
        return fn_name, kwargs

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, fn_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered function by name.

        Args:
            fn_name: Registered tool name.
            **kwargs: Parameters forwarded to the function.

        Returns:
            Result dictionary.
        """
        fn = self._registry.get(fn_name)
        if fn is None:
            logger.warning("Unknown function: %s", fn_name)
            return {"status": "error", "message": f"Unknown function: {fn_name}"}
        try:
            result = fn(**kwargs)
            logger.debug("Called %s(%s) → %s", fn_name, kwargs, result)
            return result
        except Exception as exc:
            logger.error("Error in %s: %s", fn_name, exc)
            return {"status": "error", "message": str(exc)}

    def execute_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a function call embedded in *text* and execute it."""
        parsed = self.parse_call(text)
        if parsed is None:
            return None
        fn_name, kwargs = parsed
        return self.execute(fn_name, **kwargs)

    def available_functions(self) -> list[str]:
        """Return a sorted list of registered function names."""
        return sorted(self._registry.keys())


def _coerce(value: str) -> Any:
    """Attempt to coerce a string value to int, float, bool, or leave as str."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value.strip("'\"")
