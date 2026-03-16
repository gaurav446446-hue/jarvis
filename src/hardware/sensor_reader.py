"""Motion sensor reader (mocked for Phase 1)."""
import random
import time
from datetime import datetime

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SensorReader:
    """
    Mock motion sensor for Phase 1.

    In Phase 2, this will interface with real GPIO/ESP32 hardware.
    """

    def __init__(self, pin: int = 14, mock: bool = True):
        self.pin = pin
        self.mock = mock
        self._last_motion_time: datetime | None = None
        self._motion_detected: bool = False

    def read_motion(self) -> bool:
        """Return True if motion is currently detected."""
        if self.mock:
            # Simulate occasional motion (20% chance per read)
            detected = random.random() < 0.2
            if detected:
                self._last_motion_time = datetime.now()
                self._motion_detected = True
            else:
                self._motion_detected = False
            return detected

        # Real sensor read would go here (GPIO / ESP32 serial)
        raise NotImplementedError("Real sensor not implemented in Phase 1")

    def simulate_motion(self) -> bool:
        """Force a motion detection event (for testing / automation triggers)."""
        self._last_motion_time = datetime.now()
        self._motion_detected = True
        logger.debug("Motion simulated at %s", self._last_motion_time.strftime("%H:%M:%S"))
        return True

    @property
    def last_motion_time(self) -> datetime | None:
        return self._last_motion_time

    def read_dht_sensor(self) -> dict:
        """Return mocked temperature and humidity readings."""
        if self.mock:
            temperature = round(random.uniform(22.0, 27.0), 1)
            humidity = round(random.uniform(50.0, 75.0), 1)
            return {"temperature": temperature, "humidity": humidity}
        raise NotImplementedError("Real DHT sensor not implemented in Phase 1")
