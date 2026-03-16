"""Function caller - parse LLM output and execute tool calls."""
import re
from datetime import datetime

from src.hardware.tool_definitions import JARVIS_TOOLS
from src.hardware.esp32_controller import ESP32Controller
from src.hardware.sensor_reader import SensorReader
from src.utils.constants import (
    TOOL_TURN_ON_LIGHT,
    TOOL_TURN_OFF_LIGHT,
    TOOL_SET_FAN_SPEED,
    TOOL_GET_ROOM_CONDITIONS,
    TOOL_GET_TIME,
    TOOL_GET_DAY,
    TOOL_PREDICT_COMFORT,
    TOOL_SAY,
    COMFORT_TEMP_MIN,
    COMFORT_TEMP_MAX,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Regex to find CALL: tool_name(args) in LLM output
_CALL_PATTERN = re.compile(r"CALL:\s*(\w+)\(([^)]*)\)")


def _parse_args(raw: str) -> dict:
    """Parse 'key=value, key2=value2' into a dict."""
    args = {}
    for part in raw.split(","):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            args[k.strip()] = v.strip().strip("\"'")
    return args


class FunctionCaller:
    """Parse LLM responses for tool calls and execute them."""

    def __init__(self, esp32: ESP32Controller = None, sensor: SensorReader = None):
        self.esp32 = esp32 or ESP32Controller(mock=True)
        self.sensor = sensor or SensorReader(mock=True)

    def extract_calls(self, llm_response: str) -> list[dict]:
        """Extract all CALL: ... directives from LLM text."""
        calls = []
        for match in _CALL_PATTERN.finditer(llm_response):
            tool_name = match.group(1)
            raw_args = match.group(2)
            args = _parse_args(raw_args)
            calls.append({"tool": tool_name, "args": args})
        return calls

    def execute(self, tool_name: str, args: dict) -> dict:
        """Execute a single tool call and return a result dict."""
        if tool_name not in JARVIS_TOOLS:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        logger.info("Executing tool: %s(%s)", tool_name, args)

        try:
            if tool_name == TOOL_TURN_ON_LIGHT:
                self.esp32.set_light(True)
                return {"success": True, "message": "Light is now ON"}

            if tool_name == TOOL_TURN_OFF_LIGHT:
                self.esp32.set_light(False)
                return {"success": True, "message": "Light is now OFF"}

            if tool_name == TOOL_SET_FAN_SPEED:
                speed = int(args.get("speed", 50))
                speed = max(0, min(100, speed))
                self.esp32.set_fan_speed(speed)
                return {"success": True, "message": f"Fan speed set to {speed}%"}

            if tool_name == TOOL_GET_ROOM_CONDITIONS:
                data = self.sensor.read_dht_sensor()
                now = datetime.now()
                data["time"] = now.strftime("%H:%M")
                data["day"] = now.strftime("%A")
                return {"success": True, "data": data}

            if tool_name == TOOL_GET_TIME:
                return {"success": True, "time": datetime.now().strftime("%H:%M")}

            if tool_name == TOOL_GET_DAY:
                return {"success": True, "day": datetime.now().strftime("%A")}

            if tool_name == TOOL_PREDICT_COMFORT:
                data = self.sensor.read_dht_sensor()
                temp = data["temperature"]
                if COMFORT_TEMP_MIN <= temp <= COMFORT_TEMP_MAX:
                    level = "Comfortable"
                elif temp < COMFORT_TEMP_MIN:
                    level = "Cool - consider reducing fan speed"
                else:
                    level = "Warm - consider increasing fan speed"
                return {"success": True, "comfort": level, "temperature": temp}

            if tool_name == TOOL_SAY:
                message = args.get("message", "")
                logger.info("SAY: %s", message)
                return {"success": True, "spoken": message}

        except Exception as e:
            logger.error("Tool execution error (%s): %s", tool_name, e)
            return {"success": False, "error": str(e)}

        return {"success": False, "error": f"Tool {tool_name} not handled"}

    def execute_all(self, llm_response: str) -> list[dict]:
        """Extract and execute all tool calls found in LLM response."""
        calls = self.extract_calls(llm_response)
        results = []
        for call in calls:
            result = self.execute(call["tool"], call["args"])
            result["tool"] = call["tool"]
            results.append(result)
        return results
