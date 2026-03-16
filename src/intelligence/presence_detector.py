"""Presence detection and absence automation."""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Optional

from src.intelligence.appliance_controller import ApplianceController
from src.utils.constants import (
    DEFAULT_FAN_SPEED,
    EXTENDED_ABSENCE_SECONDS,
    PresenceState,
)
from src.utils.logger import get_logger

logger = get_logger("presence_detector")


class PresenceDetector:
    """Track user presence and trigger automations on state changes.

    Args:
        appliance_controller: Controller for light/fan.
        voice_processor: Optional processor whose ``say()`` is called.
        absence_threshold_seconds: Seconds of absence before auto-off.
    """

    def __init__(
        self,
        appliance_controller: Optional[ApplianceController] = None,
        voice_processor=None,
        absence_threshold_seconds: int = EXTENDED_ABSENCE_SECONDS,
    ) -> None:
        self._appliance = appliance_controller or ApplianceController()
        self._voice = voice_processor
        self._absence_threshold = absence_threshold_seconds

        self._state: PresenceState = PresenceState.AWAY
        self._last_seen: Optional[datetime] = None
        self._away_since: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def state(self) -> PresenceState:
        return self._state

    @property
    def last_seen(self) -> Optional[datetime]:
        return self._last_seen

    @property
    def away_since(self) -> Optional[datetime]:
        return self._away_since

    # ------------------------------------------------------------------
    # Core detection
    # ------------------------------------------------------------------

    def detect_motion(self, motion_detected: bool, timestamp: Optional[datetime] = None) -> Optional[str]:
        """Process a motion sensor reading and trigger automations.

        Args:
            motion_detected: Whether motion was detected.
            timestamp: Event time (defaults to now).

        Returns:
            Description of any triggered automation, or ``None``.
        """
        now = timestamp or datetime.now()

        if motion_detected:
            return self._handle_presence(now)
        else:
            return self._check_absence(now)

    def mark_arrived(self, timestamp: Optional[datetime] = None) -> str:
        """Explicitly mark the user as arrived (AWAY → HOME).

        Returns:
            Automation description string.
        """
        now = timestamp or datetime.now()
        return self._handle_presence(now)

    def mark_departed(self, timestamp: Optional[datetime] = None) -> str:
        """Explicitly mark the user as departed (HOME → AWAY).

        Returns:
            Automation description string.
        """
        now = timestamp or datetime.now()
        self._away_since = now
        previous = self._state
        self._state = PresenceState.AWAY
        logger.info("Presence → AWAY")
        if previous == PresenceState.HOME:
            return "Departure recorded. Goodbye, Sir!"
        return "Already away."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _handle_presence(self, now: datetime) -> Optional[str]:
        previous = self._state
        self._state = PresenceState.HOME
        self._last_seen = now
        self._away_since = None

        if previous == PresenceState.AWAY:
            # Arrival automation
            self._appliance.turn_on_light()
            self._appliance.set_fan_speed(DEFAULT_FAN_SPEED)
            self._say("Welcome home, Sir!")
            logger.info("Arrival detected – lights ON, fan 50%%")
            return "arrival"
        return None

    def _check_absence(self, now: datetime) -> Optional[str]:
        if self._state != PresenceState.HOME:
            return None  # Already away

        if self._away_since is None:
            self._away_since = now
            return None

        elapsed = (now - self._away_since).total_seconds()
        if elapsed >= self._absence_threshold:
            self._state = PresenceState.AWAY
            self._appliance.turn_off_all()
            logger.info("Extended absence (%ds) – all appliances off", elapsed)
            return "extended_absence"
        return None

    def is_extended_absence(self, now: Optional[datetime] = None) -> bool:
        """Return ``True`` if absence timer has exceeded the threshold.

        The check is based purely on the ``_away_since`` timer so it correctly
        reports an impending absence even while state is still HOME (i.e. before
        the first ``detect_motion(False)`` call flips the state to AWAY).
        """
        if self._away_since is None:
            return False
        now = now or datetime.now()
        return (now - self._away_since).total_seconds() >= self._absence_threshold

    def _say(self, message: str) -> None:
        if self._voice and hasattr(self._voice, "say"):
            self._voice.say(message)
        else:
            print(f"Jarvis: {message}")
