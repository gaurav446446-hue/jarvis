"""Appliance controller for lights and fan."""
from __future__ import annotations

import time
from typing import Any, Dict

from src.utils.constants import (
    DEFAULT_BRIGHTNESS,
    DEFAULT_FAN_SPEED,
    DeviceState,
    FADE_IN_DURATION,
    FAN_SPEED_MAX,
    FAN_SPEED_MIN,
)
from src.utils.logger import get_logger

logger = get_logger("appliance_controller")


class ApplianceController:
    """Control lights and fan; maintain their in-memory state.

    All hardware operations are simulated in Phase 1.

    Attributes:
        light_state: Current light :class:`~src.utils.constants.DeviceState`.
        light_brightness: Current brightness (0–100).
        fan_speed: Current fan speed percentage (0–100).
    """

    def __init__(self) -> None:
        self.light_state: DeviceState = DeviceState.OFF
        self.light_brightness: int = DEFAULT_BRIGHTNESS
        self.fan_speed: int = 0

    # ------------------------------------------------------------------
    # Light control
    # ------------------------------------------------------------------

    def turn_on_light(self, brightness: int = DEFAULT_BRIGHTNESS) -> Dict[str, Any]:
        """Turn on the room light.

        Args:
            brightness: Target brightness (0–100). Defaults to 80.

        Returns:
            State dictionary.
        """
        brightness = max(0, min(100, brightness))
        self.light_state = DeviceState.ON
        self.light_brightness = brightness
        logger.info("Light turned ON (brightness=%d)", brightness)
        return self.get_state()

    def turn_off_light(self) -> Dict[str, Any]:
        """Turn off the room light."""
        self.light_state = DeviceState.OFF
        logger.info("Light turned OFF")
        return self.get_state()

    def fade_in(self, duration: float = FADE_IN_DURATION, target_brightness: int = DEFAULT_BRIGHTNESS) -> Dict[str, Any]:
        """Simulate a gradual fade-in over *duration* seconds.

        Args:
            duration: Fade duration in seconds.
            target_brightness: Final brightness level.

        Returns:
            State dictionary after fade completes.
        """
        steps = max(1, int(duration * 10))
        step_brightness = target_brightness / steps
        self.light_state = DeviceState.ON
        for i in range(1, steps + 1):
            self.light_brightness = int(step_brightness * i)
            time.sleep(duration / steps)
        self.light_brightness = target_brightness
        logger.info("Fade-in complete (brightness=%d)", self.light_brightness)
        return self.get_state()

    # ------------------------------------------------------------------
    # Fan control
    # ------------------------------------------------------------------

    def set_fan_speed(self, speed: int) -> Dict[str, Any]:
        """Set the fan speed.

        Args:
            speed: Fan speed percentage (0–100).

        Returns:
            State dictionary.

        Raises:
            ValueError: If *speed* is outside [0, 100].
        """
        if not FAN_SPEED_MIN <= speed <= FAN_SPEED_MAX:
            raise ValueError(f"Fan speed must be between {FAN_SPEED_MIN} and {FAN_SPEED_MAX}, got {speed}")
        self.fan_speed = speed
        logger.info("Fan speed set to %d%%", speed)
        return self.get_state()

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def get_state(self) -> Dict[str, Any]:
        """Return the current appliance state as a dictionary."""
        return {
            "light": self.light_state.value,
            "light_brightness": self.light_brightness,
            "fan_speed": self.fan_speed,
        }

    def turn_off_all(self) -> Dict[str, Any]:
        """Turn off all appliances (used for extended absence)."""
        self.turn_off_light()
        self.set_fan_speed(0)
        logger.info("All appliances turned off")
        return self.get_state()
