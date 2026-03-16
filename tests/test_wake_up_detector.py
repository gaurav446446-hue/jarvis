"""Tests for WakeUpDetector."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.intelligence.wake_up_detector import WakeUpDetector
from src.intelligence.appliance_controller import ApplianceController
from src.utils.constants import DeviceState


def _dt(hour: int, minute: int, weekday: int = 0) -> datetime:
    """Build a datetime with the given time and weekday (0=Monday)."""
    # Find a date that has the desired weekday
    base = datetime(2025, 3, 17)  # Monday
    delta_days = (weekday - base.weekday()) % 7
    from datetime import timedelta
    target = base + timedelta(days=delta_days)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


# ---------------------------------------------------------------------------
# is_wake_up_time
# ---------------------------------------------------------------------------

class TestIsWakeUpTime:
    def test_weekday_at_wake_time(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        # Monday 05:40
        assert det.is_wake_up_time(_dt(5, 40, weekday=0)) is True

    def test_weekday_friday_at_wake_time(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        # Friday 05:40
        assert det.is_wake_up_time(_dt(5, 40, weekday=4)) is True

    def test_weekend_saturday_at_wake_time(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        # Saturday 07:00
        assert det.is_wake_up_time(_dt(7, 0, weekday=5)) is True

    def test_weekend_sunday_at_wake_time(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        # Sunday 07:00
        assert det.is_wake_up_time(_dt(7, 0, weekday=6)) is True

    def test_weekday_wrong_time_returns_false(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        assert det.is_wake_up_time(_dt(6, 0, weekday=1)) is False

    def test_weekend_wrong_time_returns_false(self):
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        assert det.is_wake_up_time(_dt(8, 0, weekday=5)) is False

    def test_weekday_weekend_time_is_false(self):
        """Weekday at 07:00 (weekend time) should not trigger."""
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        assert det.is_wake_up_time(_dt(7, 0, weekday=2)) is False

    def test_weekend_weekday_time_is_false(self):
        """Weekend at 05:40 (weekday time) should not trigger."""
        det = WakeUpDetector(wake_time_weekday="05:40", wake_time_weekend="07:00")
        assert det.is_wake_up_time(_dt(5, 40, weekday=6)) is False


# ---------------------------------------------------------------------------
# wake_up_sequence
# ---------------------------------------------------------------------------

class TestWakeUpSequence:
    def test_weekday_greeting(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice,
                             wake_time_weekday="05:40", wake_time_weekend="07:00")
        now = _dt(5, 40, weekday=0)
        greeting = det.wake_up_sequence(now=now)
        assert "rise and shine" in greeting.lower()

    def test_weekend_greeting(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice,
                             wake_time_weekday="05:40", wake_time_weekend="07:00")
        now = _dt(7, 0, weekday=5)
        greeting = det.wake_up_sequence(now=now)
        assert "weekend" in greeting.lower()

    def test_light_turned_on(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice)
        det.wake_up_sequence(now=_dt(5, 40, weekday=0))
        assert appliance.light_state == DeviceState.ON

    def test_fan_set_to_50(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice)
        det.wake_up_sequence(now=_dt(5, 40, weekday=0))
        assert appliance.fan_speed == 50

    def test_voice_say_called(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice)
        det.wake_up_sequence(now=_dt(5, 40, weekday=0))
        voice.say.assert_called_once()

    def test_sequence_marks_today(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice)
        now = _dt(5, 40, weekday=0)
        det.wake_up_sequence(now=now)
        assert det._sequence_executed_today == now.strftime("%Y-%m-%d")

    def test_should_run_sequence_false_after_execution(self, appliance, voice):
        det = WakeUpDetector(appliance_controller=appliance, voice_processor=voice,
                             wake_time_weekday="05:40", wake_time_weekend="07:00")
        now = _dt(5, 40, weekday=0)
        det.wake_up_sequence(now=now)
        assert det.should_run_sequence(now=now) is False
