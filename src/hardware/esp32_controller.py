"""ESP32 controller stub (Phase 1 - commands are logged, not sent)."""
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ESP32Controller:
    """
    Stub for ESP32 serial/MQTT communication.

    Phase 1: All commands are simulated and logged.
    Phase 2: Real UART/MQTT integration will be added.
    """

    def __init__(self, port: str = "/dev/ttyUSB0", baud_rate: int = 115200, mock: bool = True):
        self.port = port
        self.baud_rate = baud_rate
        self.mock = mock
        self._light_state: bool = False
        self._fan_speed: int = 0
        self._connected: bool = False

        if not mock:
            self._connect()

    def _connect(self):
        """Establish serial connection to ESP32."""
        try:
            import serial  # type: ignore

            self._serial = serial.Serial(self.port, self.baud_rate, timeout=2)
            self._connected = True
            logger.info("Connected to ESP32 on %s", self.port)
        except Exception as e:
            logger.error("Failed to connect to ESP32: %s", e)

    def send_command(self, command: str, value: int = 0) -> bool:
        """Send a command to ESP32."""
        if self.mock:
            logger.debug("ESP32 [MOCK] command=%s value=%d", command, value)
            return True

        if not self._connected:
            logger.error("ESP32 not connected")
            return False

        try:
            payload = f"{command}:{value}\n"
            self._serial.write(payload.encode())
            return True
        except Exception as e:
            logger.error("ESP32 send error: %s", e)
            return False

    def set_light(self, state: bool) -> bool:
        """Turn tubelight on or off."""
        self._light_state = state
        cmd = "LIGHT_ON" if state else "LIGHT_OFF"
        logger.info("Light -> %s", "ON" if state else "OFF")
        return self.send_command(cmd, 1 if state else 0)

    def set_fan_speed(self, speed: int) -> bool:
        """Set fan speed (0-100)."""
        speed = max(0, min(100, speed))
        self._fan_speed = speed
        logger.info("Fan speed -> %d%%", speed)
        return self.send_command("FAN_SPEED", speed)

    def fade_in_light(self, duration_seconds: float = 2.0) -> bool:
        """Gradually increase light brightness over `duration_seconds`."""
        import time

        steps = 10
        delay = duration_seconds / steps
        logger.info("Fading in light over %.1f seconds", duration_seconds)
        for i in range(1, steps + 1):
            brightness = int((i / steps) * 100)
            self.send_command("LIGHT_DIM", brightness)
            time.sleep(delay)
        self._light_state = True
        return True

    @property
    def light_state(self) -> bool:
        return self._light_state

    @property
    def fan_speed(self) -> int:
        return self._fan_speed
