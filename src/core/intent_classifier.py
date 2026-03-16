"""Intent classifier using regex patterns."""
from __future__ import annotations

import re
from typing import Any, Dict, Optional, Tuple

from src.utils.constants import Intent

# ---------------------------------------------------------------------------
# Pattern tables
# ---------------------------------------------------------------------------

_GREETING_PATTERNS = [
    r"\bgood\s+(morning|afternoon|evening|night)\b",
    r"\bhello\b",
    r"\bhi\b",
    r"\bhey\s*(jarvis)?\b",
    r"\bwassup\b",
    r"\bgreetings\b",
]

_COMFORT_PATTERNS = [
    r"\btoo\s+(hot|warm|cold|cool|humid|dry)\b",
    r"\bit[''`]?s?\s+(hot|warm|cold|cool|stuffy|freezing)\b",
    r"\bfeeling\s+(hot|warm|cold|cool|uncomfortable)\b",
    r"\badjust\s+(the\s+)?(temperature|temp|fan|ac|air)\b",
    r"\b(increase|decrease|raise|lower)\s+(temperature|temp|fan|speed)\b",
    r"\bcomfort\b",
    r"\buncomfortable\b",
]

_CONTEXT_PATTERNS = [
    r"\bi[''`]?m\s+(leaving|going out|heading out|away)\b",
    r"\b(leaving|departing)\s+(now|home|the room)?\b",
    r"\bi[''`]?ll\s+be\s+back\b",
    r"\bsee\s+you\s+later\b",
    r"\bgoodbye\b",
    r"\bbye\b",
    r"\bi[''`]?m\s+(home|back|here|arrived)\b",
    r"\bjust\s+(arrived|got home|got back)\b",
]

_QUERY_PATTERNS = [
    r"\bwhat[''`]?s?\s+(the\s+)?(time|temperature|temp|humidity|fan speed|status|weather)\b",
    r"\bhow\s+(hot|cold|warm|cool|humid)\b",
    r"\btell\s+me\b",
    r"\bwhat\s+is\b",
    r"\bshow\s+me\b",
    r"\bcheck\s+(the\s+)?(room|temperature|temp|status|conditions)\b",
    r"\broom\s+conditions\b",
    r"\b(status|stats)\b",
    r"\bwhat\s+day\b",
    r"\bwhat\s+time\b",
]

_EXPLAIN_PATTERNS = [
    r"\bwhy\b",
    r"\bhow\s+does\b",
    r"\bexplain\b",
    r"\btell\s+me\s+(more|about)\b",
    r"\bwhat\s+can\s+you\b",
    r"\bhelp\b",
    r"\bwhat\s+do\s+you\s+do\b",
    r"\bcapabilities\b",
]

_CONTROL_PATTERNS = [
    r"\b(turn|switch)\s+(on|off)\s+(?:the\s+)?(.+)",
    r"\b(turn|switch)\s+(?:the\s+)?(.+?)\s+(on|off)\b",
    r"\b(set|change)\s+(?:the\s+)?(.+?)\s+(speed|brightness|level|to)\b",
    r"\b(dim|brighten)\s+(?:the\s+)?(lights?|lamp)\b",
    r"\b(start|stop|activate|deactivate)\s+(?:the\s+)?(.+)",
    r"\b(on|off)\b",
]

# Device keyword → canonical name mapping
_DEVICE_ALIASES: Dict[str, str] = {
    "light": "light",
    "lights": "light",
    "lamp": "light",
    "lamps": "light",
    "fan": "fan",
    "fans": "fan",
    "ac": "ac",
    "air conditioner": "ac",
    "air conditioning": "ac",
    "tv": "tv",
    "television": "tv",
    "heater": "heater",
}

_ACTION_ALIASES: Dict[str, str] = {
    "on": "turn_on",
    "turn on": "turn_on",
    "switch on": "turn_on",
    "start": "turn_on",
    "activate": "turn_on",
    "off": "turn_off",
    "turn off": "turn_off",
    "switch off": "turn_off",
    "stop": "turn_off",
    "deactivate": "turn_off",
    "dim": "dim",
    "brighten": "brighten",
    "set": "set",
    "change": "set",
}


def _compile(patterns: list[str]) -> re.Pattern:
    combined = "|".join(f"(?:{p})" for p in patterns)
    return re.compile(combined, re.IGNORECASE)


_RE_GREETING = _compile(_GREETING_PATTERNS)
_RE_COMFORT = _compile(_COMFORT_PATTERNS)
_RE_CONTEXT = _compile(_CONTEXT_PATTERNS)
_RE_QUERY = _compile(_QUERY_PATTERNS)
_RE_EXPLAIN = _compile(_EXPLAIN_PATTERNS)
_RE_CONTROL = _compile(_CONTROL_PATTERNS)


def _extract_device(text: str) -> Optional[str]:
    text_lower = text.lower()
    for alias, canonical in _DEVICE_ALIASES.items():
        if alias in text_lower:
            return canonical
    return None


def _extract_action(text: str) -> Optional[str]:
    text_lower = text.lower()
    # Longer phrases first to avoid partial matches
    for phrase in sorted(_ACTION_ALIASES, key=len, reverse=True):
        if phrase in text_lower:
            return _ACTION_ALIASES[phrase]
    return None


def _extract_fan_speed(text: str) -> Optional[int]:
    match = re.search(r"(\d{1,3})\s*%", text)
    if match:
        value = int(match.group(1))
        return max(0, min(100, value))
    for word, value in {"half": 50, "full": 100, "max": 100, "low": 25, "medium": 50, "high": 75}.items():
        if word in text.lower():
            return value
    return None


class IntentClassifier:
    """Classify natural language input into :class:`~src.utils.constants.Intent` values."""

    def classify(self, text: str) -> Tuple[Intent, Dict[str, Any]]:
        """Return ``(intent, params)`` for the given user utterance.

        Args:
            text: Raw user input string.

        Returns:
            A tuple of the detected :class:`Intent` and a dictionary of
            extracted parameters (may be empty).
        """
        text = text.strip()
        params: Dict[str, Any] = {}

        if _RE_GREETING.search(text):
            return Intent.GREETING, params

        if _RE_COMFORT.search(text):
            speed = _extract_fan_speed(text)
            if speed is not None:
                params["fan_speed"] = speed
            return Intent.COMFORT, params

        if _RE_CONTEXT.search(text):
            if re.search(r"\b(home|back|arrived|here)\b", text, re.IGNORECASE):
                params["event"] = "arrival"
            else:
                params["event"] = "departure"
            return Intent.CONTEXT, params

        if _RE_CONTROL.search(text):
            device = _extract_device(text)
            action = _extract_action(text)
            if device:
                params["device"] = device
            if action:
                params["action"] = action
            speed = _extract_fan_speed(text)
            if speed is not None:
                params["value"] = speed
            return Intent.CONTROL, params

        if _RE_QUERY.search(text):
            return Intent.QUERY, params

        if _RE_EXPLAIN.search(text):
            return Intent.EXPLAIN, params

        return Intent.UNKNOWN, params

    def get_intent_name(self, text: str) -> str:
        """Convenience wrapper returning the intent name string."""
        intent, _ = self.classify(text)
        return intent.value
