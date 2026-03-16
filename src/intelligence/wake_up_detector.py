"""Wake-up detector - monitors time and motion to trigger morning automation."""
import threading
import time
from datetime import datetime, timedelta

from src.utils.constants import (
    WEEKDAYS,
    WEEKEND_DAYS,
    WEEKDAY_WAKE_TIME,
    WEEKEND_WAKE_TIME,
    WEEKDAY_GREETING,
    WEEKEND_GREETING,
    FAN_SPEED_DEFAULT,
    EVENT_WAKE_UP,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_time(time_str: str) -> tuple[int, int]:
    """Parse 'HH:MM' into (hour, minute) tuple."""
    h, m = time_str.split(":")
    return int(h), int(m)


class WakeUpDetector:
    """
    Monitor clock and (optionally) motion sensor to trigger wake-up automation.

    Wake-up times:
    - Weekdays (Mon-Fri): 05:40
    - Weekends (Sat-Sun): 07:00

    The automation sequence:
    1. Fade in light (2 seconds)
    2. Speak greeting
    3. Set fan to 50%
    4. Display room conditions
    """

    def __init__(self, config=None, memory=None, esp32=None, sensor=None):
        if config is not None:
            self._weekday_time = config.weekday_wake_time
            self._weekend_time = config.weekend_wake_time
            self._fan_speed = config.preferred_fan_speed
        else:
            self._weekday_time = WEEKDAY_WAKE_TIME
            self._weekend_time = WEEKEND_WAKE_TIME
            self._fan_speed = FAN_SPEED_DEFAULT

        self._memory = memory
        self._esp32 = esp32
        self._sensor = sensor

        self._triggered_today: bool = False
        self._last_trigger_date: datetime | None = None
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._callbacks: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_callback(self, fn):
        """Register a callback to run when wake-up triggers."""
        self._callbacks.append(fn)

    def start(self):
        """Start background monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("WakeUpDetector started (weekday=%s, weekend=%s)",
                    self._weekday_time, self._weekend_time)

    def stop(self):
        """Stop background monitoring thread."""
        self._running = False

    def get_wake_time_for_today(self) -> str:
        """Return the scheduled wake-up time string for today."""
        day = datetime.now().strftime("%A")
        return self._weekday_time if day in WEEKDAYS else self._weekend_time

    def is_wake_time(self, now: datetime = None) -> bool:
        """Return True if right now is within the wake-up window (±1 min)."""
        now = now or datetime.now()
        day = now.strftime("%A")
        wake_str = self._weekday_time if day in WEEKDAYS else self._weekend_time
        h, m = _parse_time(wake_str)
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        delta = abs((now - target).total_seconds())
        return delta <= 60

    def check_and_trigger(self, motion_detected: bool = False, now: datetime = None) -> bool:
        """
        Check whether wake-up automation should fire.

        Fires if:
        - It is the wake-up minute, OR motion was detected within the wake window
        - Not already triggered today

        Returns True if automation was triggered.
        """
        now = now or datetime.now()

        if self._triggered_today and self._last_trigger_date:
            if self._last_trigger_date.date() == now.date():
                return False

        if self.is_wake_time(now) or (motion_detected and self._is_within_wake_window(now)):
            self._run_wake_sequence(now)
            self._triggered_today = True
            self._last_trigger_date = now
            return True

        # Reset the flag at midnight
        if self._last_trigger_date and self._last_trigger_date.date() < now.date():
            self._triggered_today = False

        return False

    def get_greeting(self, now: datetime = None) -> str:
        """Return the appropriate morning greeting."""
        now = now or datetime.now()
        day = now.strftime("%A")
        return WEEKDAY_GREETING if day in WEEKDAYS else WEEKEND_GREETING

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _is_within_wake_window(self, now: datetime, window_minutes: int = 15) -> bool:
        """Return True if now is within `window_minutes` before the wake time."""
        day = now.strftime("%A")
        wake_str = self._weekday_time if day in WEEKDAYS else self._weekend_time
        h, m = _parse_time(wake_str)
        target = now.replace(hour=h, minute=m, second=0, microsecond=0)
        delta = (target - now).total_seconds()
        return 0 <= delta <= window_minutes * 60

    def _run_wake_sequence(self, now: datetime):
        """Execute the full wake-up automation sequence."""
        greeting = self.get_greeting(now)
        day = now.strftime("%A")
        time_str = now.strftime("%H:%M")

        logger.info("Wake-up sequence triggered at %s (%s)", time_str, day)

        if self._esp32:
            self._esp32.fade_in_light(duration_seconds=2)

        logger.info("Greeting: %s", greeting)

        if self._esp32:
            self._esp32.set_fan_speed(self._fan_speed)

        if self._memory:
            self._memory.log_event(EVENT_WAKE_UP, {
                "time": time_str,
                "day": day,
                "greeting": greeting,
                "fan_speed": self._fan_speed,
            })

        for cb in self._callbacks:
            try:
                cb(greeting=greeting, day=day, time_str=time_str)
            except Exception as e:
                logger.error("Wake-up callback error: %s", e)

    def _monitor_loop(self):
        """Background loop that checks every 30 seconds."""
        while self._running:
            try:
                motion = self._sensor.read_motion() if self._sensor else False
                self.check_and_trigger(motion_detected=motion)
            except Exception as e:
                logger.error("WakeUpDetector loop error: %s", e)
            time.sleep(30)
