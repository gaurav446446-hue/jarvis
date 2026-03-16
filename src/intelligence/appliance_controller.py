"""Appliance controller - high-level smart control logic."""
from datetime import datetime

from src.hardware.esp32_controller import ESP32Controller
from src.hardware.sensor_reader import SensorReader
from src.utils.constants import (
    FAN_SPEED_DEFAULT,
    COMFORT_TEMP_MIN,
    COMFORT_TEMP_MAX,
    EVENT_LIGHT_ON,
    EVENT_LIGHT_OFF,
    EVENT_FAN_SPEED,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplianceController:
    """High-level appliance control with logging and memory integration."""

    def __init__(self, esp32: ESP32Controller = None, sensor: SensorReader = None, memory=None):
        self.esp32 = esp32 or ESP32Controller(mock=True)
        self.sensor = sensor or SensorReader(mock=True)
        self.memory = memory

    def turn_on_light(self) -> str:
        self.esp32.set_light(True)
        if self.memory:
            self.memory.log_event(EVENT_LIGHT_ON, {"time": datetime.now().isoformat()})
        return "Light is now ON"

    def turn_off_light(self) -> str:
        self.esp32.set_light(False)
        if self.memory:
            self.memory.log_event(EVENT_LIGHT_OFF, {"time": datetime.now().isoformat()})
        return "Light is now OFF"

    def set_fan_speed(self, speed: int) -> str:
        speed = max(0, min(100, speed))
        self.esp32.set_fan_speed(speed)
        if self.memory:
            self.memory.log_event(EVENT_FAN_SPEED, {"speed": speed, "time": datetime.now().isoformat()})
        return f"Fan speed set to {speed}%"

    def get_room_conditions(self) -> dict:
        data = self.sensor.read_dht_sensor()
        now = datetime.now()
        data["time"] = now.strftime("%H:%M")
        data["day"] = now.strftime("%A")
        return data

    def arrival_mode(self) -> str:
        """Set up room for user arrival."""
        self.turn_on_light()
        self.set_fan_speed(FAN_SPEED_DEFAULT)
        return f"Welcome home! Light ON, fan set to {FAN_SPEED_DEFAULT}%."

    def away_mode(self) -> str:
        """Turn everything off when user leaves."""
        self.turn_off_light()
        self.set_fan_speed(0)
        return "Away mode activated. Light OFF, fan OFF."

    def comfort_mode(self) -> str:
        """Adjust fan based on current temperature."""
        data = self.sensor.read_dht_sensor()
        temp = data["temperature"]
        if temp > COMFORT_TEMP_MAX:
            speed = min(100, FAN_SPEED_DEFAULT + 20)
        elif temp < COMFORT_TEMP_MIN:
            speed = max(0, FAN_SPEED_DEFAULT - 20)
        else:
            speed = FAN_SPEED_DEFAULT
        self.set_fan_speed(speed)
        return f"Comfort mode: {temp}°C → fan at {speed}%"
