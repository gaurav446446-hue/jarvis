"""System prompt builder for Jarvis LLM."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.utils.config import get_config

_SYSTEM_TEMPLATE = """\
You are Jarvis, an AI-powered smart room assistant.
You address the user as "{user_name}".
Current date/time: {datetime}

## Personality
- Polite, concise, and helpful
- Proactive about comfort and automation
- Refer to the user as "{user_name}" (formal but friendly)

## User Preferences
- Wake-up (weekday): {wake_weekday}
- Wake-up (weekend): {wake_weekend}
- Comfort temperature: {temp_min}°C – {temp_max}°C
- Preferred fan speed: {fan_speed}%

## Available Tools
{tools_section}

## Instructions
- When the user requests a device action, call the appropriate tool.
- Keep responses brief unless asked for detail.
- If a tool call is needed, output it on its own line as: CALL: tool_name(param=value)
- After executing a tool, confirm the action in natural language.
"""


def build_system_prompt(
    tools: Optional[List[str]] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> str:
    """Build the LLM system prompt.

    Args:
        tools: List of available tool names to include in the prompt.
        extra_context: Additional key/value pairs merged into the template.

    Returns:
        Formatted system prompt string.
    """
    cfg = get_config()
    now = datetime.now()

    if tools:
        tools_lines = "\n".join(f"  - {t}" for t in sorted(tools))
    else:
        tools_lines = "  (none registered)"

    values: Dict[str, Any] = {
        "user_name": cfg.user.name,
        "datetime": now.strftime("%A, %Y-%m-%d %H:%M"),
        "wake_weekday": cfg.user.wake_time_weekday,
        "wake_weekend": cfg.user.wake_time_weekend,
        "temp_min": cfg.user.comfort.temperature_min,
        "temp_max": cfg.user.comfort.temperature_max,
        "fan_speed": cfg.user.comfort.preferred_fan_speed,
        "tools_section": tools_lines,
    }
    if extra_context:
        values.update(extra_context)

    return _SYSTEM_TEMPLATE.format(**values)


def build_user_message(text: str) -> Dict[str, str]:
    """Wrap a user utterance in the Ollama message format."""
    return {"role": "user", "content": text}


def build_assistant_message(text: str) -> Dict[str, str]:
    """Wrap an assistant reply in the Ollama message format."""
    return {"role": "assistant", "content": text}
