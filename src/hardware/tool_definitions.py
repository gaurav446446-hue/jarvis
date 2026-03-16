"""Tool definitions - available functions that Jarvis can call."""
from src.utils.constants import (
    TOOL_TURN_ON_LIGHT,
    TOOL_TURN_OFF_LIGHT,
    TOOL_SET_FAN_SPEED,
    TOOL_GET_ROOM_CONDITIONS,
    TOOL_GET_TIME,
    TOOL_GET_DAY,
    TOOL_PREDICT_COMFORT,
    TOOL_SAY,
)

JARVIS_TOOLS = {
    TOOL_TURN_ON_LIGHT: {
        "description": "Turn the tubelight ON",
        "parameters": [],
    },
    TOOL_TURN_OFF_LIGHT: {
        "description": "Turn the tubelight OFF",
        "parameters": [],
    },
    TOOL_SET_FAN_SPEED: {
        "description": "Set fan speed between 0 and 100 percent",
        "parameters": [
            {
                "name": "speed",
                "type": "int",
                "description": "Fan speed percentage (0-100)",
                "required": True,
            }
        ],
    },
    TOOL_GET_ROOM_CONDITIONS: {
        "description": "Get current room temperature, humidity, time, and day",
        "parameters": [],
    },
    TOOL_GET_TIME: {
        "description": "Get the current time",
        "parameters": [],
    },
    TOOL_GET_DAY: {
        "description": "Get the current day of the week",
        "parameters": [],
    },
    TOOL_PREDICT_COMFORT: {
        "description": "Predict the current comfort level based on temperature and humidity",
        "parameters": [],
    },
    TOOL_SAY: {
        "description": "Speak a message aloud via text-to-speech",
        "parameters": [
            {
                "name": "message",
                "type": "str",
                "description": "The message to speak",
                "required": True,
            }
        ],
    },
}


def get_tool_descriptions() -> str:
    """Return a formatted string of all available tools for LLM prompts."""
    lines = []
    for name, info in JARVIS_TOOLS.items():
        params = info.get("parameters", [])
        if params:
            param_str = ", ".join(p["name"] for p in params)
            lines.append(f"  {name}({param_str}) - {info['description']}")
        else:
            lines.append(f"  {name}() - {info['description']}")
    return "\n".join(lines)
