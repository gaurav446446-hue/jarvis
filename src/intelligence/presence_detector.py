"""Presence detector - tracks whether the user is home based on motion sensor."""
import threading
import time
from datetime import datetime, timedelta

from src.utils.constants import (
    STATE_HOME,
    STATE_AWAY,
    FAN_SPEED_DEFAULT,
    EVENT_ARRIVAL,
    EVENT_DEPARTURE,
    ARRIVAL_GREETING,
    DEPARTURE_MESSAGE,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PresenceDetector:
    """
    Track user presence using motion sensor data.

    Transitions:
    - AWAY → HOME: motion detected after absence
    - HOME → AWAY: no motion for `away_timeout_minutes`
    """

    def __init__(self, config=None, memory=None, esp32=None, sensor=None):
        self._memory = memory
        self._esp32 = esp32
        self._sensor = sensor

        if config is not None:
            self._away_timeout = timedelta(
                minutes=config.away_timeout_minutes
            )
            self._fan_speed = config.preferred_fan_speed
        else:
            self._away_timeout = timedelta(minutes=120)
            self._fan_speed = FAN_SPEED_DEFAULT

        # Load last known state from memory, default to HOME
        if memory is not None:
            initial = memory.get_presence_state()
        else:
            initial = STATE_HOME

        self._state: str = initial
        self._last_motion_time: datetime = datetime.now()
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._arrival_callbacks: list = []
        self._departure_callbacks: list = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state

    def add_arrival_callback(self, fn):
        self._arrival_callbacks.append(fn)

    def add_departure_callback(self, fn):
        self._departure_callbacks.append(fn)

    def update(self, motion_detected: bool, now: datetime = None) -> str:
        """
        Update presence state based on motion reading.

        Returns the current state after the update.
        """
        now = now or datetime.now()

        if motion_detected:
            self._last_motion_time = now
            if self._state == STATE_AWAY:
                self._transition_to_home(now)
        else:
            elapsed = now - self._last_motion_time
            if self._state == STATE_HOME and elapsed >= self._away_timeout:
                self._transition_to_away(now)

        return self._state

    def start(self):
        """Start background presence monitoring loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("PresenceDetector started (away_timeout=%s)", self._away_timeout)

    def stop(self):
        self._running = False

    def force_arrival(self):
        """Manually trigger an arrival event (for testing)."""
        self._transition_to_home(datetime.now())

    def force_departure(self):
        """Manually trigger a departure event (for testing)."""
        self._transition_to_away(datetime.now())

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _transition_to_home(self, now: datetime):
        logger.info("Presence: AWAY → HOME")
        self._state = STATE_HOME
        self._last_motion_time = now

        if self._memory:
            self._memory.set_presence_state(STATE_HOME)
            self._memory.log_event(EVENT_ARRIVAL, {"time": now.strftime("%H:%M")})

        if self._esp32:
            self._esp32.set_light(True)
            self._esp32.set_fan_speed(self._fan_speed)
            logger.info("Arrival automation: light ON, fan %d%%", self._fan_speed)

        for cb in self._arrival_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error("Arrival callback error: %s", e)

    def _transition_to_away(self, now: datetime):
        logger.info("Presence: HOME → AWAY (no motion for %s)", self._away_timeout)
        self._state = STATE_AWAY

        if self._memory:
            self._memory.set_presence_state(STATE_AWAY)
            self._memory.log_event(EVENT_DEPARTURE, {"time": now.strftime("%H:%M")})

        if self._esp32:
            self._esp32.set_light(False)
            self._esp32.set_fan_speed(0)
            logger.info("Away mode: light OFF, fan OFF")

        for cb in self._departure_callbacks:
            try:
                cb()
            except Exception as e:
                logger.error("Departure callback error: %s", e)

    def _monitor_loop(self):
        """Background loop checking presence every 30 seconds."""
        while self._running:
            try:
                motion = self._sensor.read_motion() if self._sensor else False
                self.update(motion_detected=motion)
            except Exception as e:
                logger.error("PresenceDetector loop error: %s", e)
            time.sleep(30)
