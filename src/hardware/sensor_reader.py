"""Mock sensor reader for Phase 1."""
from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict


class SensorReader:
    """Simulate room sensors (motion, temperature, humidity).

    In Phase 1 all values are mocked.  Phase 2 will replace this with real
    ESP32 hardware reads.

    Args:
        temperature: Fixed simulated temperature (°C). Defaults to 24.0.
        humidity: Fixed simulated humidity (%). Defaults to 65.0.
        motion_probability: Probability (0–1) that motion is detected when
            :meth:`read_motion` is called without an explicit override.
    """

    def __init__(
        self,
        temperature: float = 24.0,
        humidity: float = 65.0,
        motion_probability: float = 0.3,
    ) -> None:
        self._temperature = temperature
        self._humidity = humidity
        self._motion_probability = motion_probability
        self._last_motion_time: datetime | None = None

    # ------------------------------------------------------------------
    # Individual sensors
    # ------------------------------------------------------------------

    def read_temperature(self) -> float:
        """Return the simulated room temperature in °C."""
        return self._temperature

    def read_humidity(self) -> float:
        """Return the simulated relative humidity (%)."""
        return self._humidity

    def read_motion(self) -> bool:
        """Return a random motion detection result.

        Returns:
            ``True`` if motion is simulated, ``False`` otherwise.
        """
        detected = random.random() < self._motion_probability
        if detected:
            self._last_motion_time = datetime.now()
        return detected

    # ------------------------------------------------------------------
    # Combined reading
    # ------------------------------------------------------------------

    def get_conditions(self) -> Dict[str, Any]:
        """Return a snapshot of all sensor readings.

        Returns:
            Dictionary with ``temperature``, ``humidity``, and ``motion`` keys.
        """
        return {
            "temperature": self._temperature,
            "humidity": self._humidity,
            "motion": self.read_motion(),
            "timestamp": datetime.now().isoformat(),
        }

    # ------------------------------------------------------------------
    # Configuration helpers (useful in tests)
    # ------------------------------------------------------------------

    def set_temperature(self, value: float) -> None:
        self._temperature = value

    def set_humidity(self, value: float) -> None:
        self._humidity = value

    def set_motion_probability(self, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError("motion_probability must be in [0, 1]")
        self._motion_probability = value
