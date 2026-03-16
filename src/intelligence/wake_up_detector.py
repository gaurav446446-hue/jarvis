"""Wake-up detection and morning routine automation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from src.intelligence.appliance_controller import ApplianceController
from src.utils.constants import (
    DEFAULT_FAN_SPEED,
    FADE_IN_DURATION,
    WEEKDAYS,
    WEEKDAY_WAKE_TIME,
    WEEKEND_DAYS,
    WEEKEND_WAKE_TIME,
)
from src.utils.logger import get_logger

logger = get_logger("wake_up_detector")


class WakeUpDetector:
    """Detect wake-up time and execute the morning routine.

    Args:
        appliance_controller: Controller used to operate light and fan.
        voice_processor: Optional processor whose ``say()`` method is called.
        wake_time_weekday: Override weekday wake-up time (``"HH:MM"``).
        wake_time_weekend: Override weekend wake-up time (``"HH:MM"``).
    """

    def __init__(
        self,
        appliance_controller: Optional[ApplianceController] = None,
        voice_processor=None,
        wake_time_weekday: str = WEEKDAY_WAKE_TIME,
        wake_time_weekend: str = WEEKEND_WAKE_TIME,
    ) -> None:
        self._appliance = appliance_controller or ApplianceController()
        self._voice = voice_processor
        self._wake_time_weekday = wake_time_weekday
        self._wake_time_weekend = wake_time_weekend
        self._sequence_executed_today: Optional[str] = None  # stores "YYYY-MM-DD"

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def is_wake_up_time(self, now: Optional[datetime] = None) -> bool:
        """Return ``True`` if *now* matches the configured wake-up time.

        Args:
            now: Datetime to check; defaults to :func:`datetime.now`.

        Returns:
            Whether it is currently the wake-up minute.
        """
        now = now or datetime.now()
        current_hm = now.strftime("%H:%M")
        if now.weekday() in WEEKDAYS:
            return current_hm == self._wake_time_weekday
        return current_hm == self._wake_time_weekend

    def should_run_sequence(self, now: Optional[datetime] = None) -> bool:
        """Return ``True`` if the morning sequence has not yet run today."""
        now = now or datetime.now()
        today = now.strftime("%Y-%m-%d")
        return self.is_wake_up_time(now) and self._sequence_executed_today != today

    # ------------------------------------------------------------------
    # Morning routine
    # ------------------------------------------------------------------

    def wake_up_sequence(self, now: Optional[datetime] = None) -> str:
        """Execute the full wake-up routine.

        Steps:
        1. Fade in light over 2 seconds.
        2. Say the morning greeting.
        3. Set fan to 50 %.
        4. Show room conditions.

        Args:
            now: Override for the current time (used in tests).

        Returns:
            The greeting string that was announced.
        """
        now = now or datetime.now()
        today = now.strftime("%Y-%m-%d")

        greeting = self._get_greeting(now)

        # 1. Fade in light
        self._appliance.fade_in(duration=FADE_IN_DURATION)

        # 2. Announce greeting
        self._say(greeting)

        # 3. Set fan
        self._appliance.set_fan_speed(DEFAULT_FAN_SPEED)

        # 4. Log room conditions (simulated)
        logger.info("Wake-up sequence complete. Greeting: %s", greeting)
        self._sequence_executed_today = today

        return greeting

    def _get_greeting(self, now: datetime) -> str:
        if now.weekday() in WEEKDAYS:
            return "Good morning, Sir! Time to rise and shine!"
        return "Good morning, Sir! Happy weekend!"

    def _say(self, message: str) -> None:
        if self._voice and hasattr(self._voice, "say"):
            self._voice.say(message)
        else:
            print(f"Jarvis: {message}")
