"""Tool definitions for Jarvis hardware abstraction layer."""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional


def _noop(**kwargs) -> Dict[str, Any]:
    """Placeholder callable for tools that require external injection."""
    return {"status": "not_configured"}


JARVIS_TOOLS: Dict[str, Dict[str, Any]] = {
    "turn_on_light": {
        "description": "Turn on the room light.",
        "callable": _noop,
        "parameters": [],
    },
    "turn_off_light": {
        "description": "Turn off the room light.",
        "callable": _noop,
        "parameters": [],
    },
    "set_fan_speed": {
        "description": "Set the fan speed (0–100%).",
        "callable": _noop,
        "parameters": [
            {"name": "speed", "type": "int", "description": "Fan speed percentage (0–100)", "required": True},
        ],
    },
    "get_room_conditions": {
        "description": "Return current temperature, humidity, and motion status.",
        "callable": _noop,
        "parameters": [],
    },
    "get_time": {
        "description": "Return the current local time.",
        "callable": _noop,
        "parameters": [],
    },
    "get_day": {
        "description": "Return the current day of the week and date.",
        "callable": _noop,
        "parameters": [],
    },
    "predict_comfort": {
        "description": "Analyse current room conditions and predict comfort level.",
        "callable": _noop,
        "parameters": [],
    },
    "say": {
        "description": "Speak a message via TTS or print to console.",
        "callable": _noop,
        "parameters": [
            {"name": "message", "type": "str", "description": "Text to speak", "required": True},
        ],
    },
}


def get_tool(name: str) -> Optional[Dict[str, Any]]:
    """Return the tool definition for *name*, or ``None`` if unknown."""
    return JARVIS_TOOLS.get(name)


def register_tool(
    name: str,
    description: str,
    callable_: Callable,
    parameters: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Register or update a tool in :data:`JARVIS_TOOLS`.

    Args:
        name: Unique tool name.
        description: Human-readable description used in the LLM prompt.
        callable_: Python callable that implements the tool.
        parameters: List of parameter definition dicts.
    """
    JARVIS_TOOLS[name] = {
        "description": description,
        "callable": callable_,
        "parameters": parameters or [],
    }


def tool_names() -> List[str]:
    """Return a sorted list of registered tool names."""
    return sorted(JARVIS_TOOLS.keys())


def tools_summary() -> str:
    """Return a human-readable summary of all tools (used in LLM prompts)."""
    lines = []
    for name, info in sorted(JARVIS_TOOLS.items()):
        params = info.get("parameters", [])
        param_str = ", ".join(p["name"] for p in params) if params else ""
        lines.append(f"  {name}({param_str}) – {info['description']}")
    return "\n".join(lines)
