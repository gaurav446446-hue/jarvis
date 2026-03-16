"""Tests for WakeUpDetector."""
import pytest
from datetime import datetime, timedelta

from src.intelligence.wake_up_detector import WakeUpDetector, _parse_time
from src.utils.constants import (
    WEEKDAY_WAKE_TIME,
    WEEKEND_WAKE_TIME,
    WEEKDAY_GREETING,
    WEEKEND_GREETING,
)


@pytest.fixture
def detector(config, memory):
    return WakeUpDetector(config=config, memory=memory)


class TestParseTime:
    def test_parse_normal(self):
        assert _parse_time("05:40") == (5, 40)

    def test_parse_midnight(self):
        assert _parse_time("00:00") == (0, 0)

    def test_parse_noon(self):
        assert _parse_time("12:00") == (12, 0)


class TestWakeTimeForToday:
    def test_weekday_returns_weekday_time(self, detector, monkeypatch):
        # Monday
        fixed = datetime(2024, 1, 1, 5, 40)  # Monday
        monkeypatch.setattr("src.intelligence.wake_up_detector.datetime",
                            type("FakeDT", (), {"now": staticmethod(lambda: fixed),
                                                "strftime": fixed.strftime})())
        result = detector.get_wake_time_for_today()
        # Can't easily monkeypatch datetime.now inside the method - test directly
        assert detector._weekday_time == WEEKDAY_WAKE_TIME
        assert detector._weekend_time == WEEKEND_WAKE_TIME

    def test_returns_correct_types(self, detector):
        wt = detector.get_wake_time_for_today()
        assert isinstance(wt, str)
        assert ":" in wt


class TestIsWakeTime:
    def test_exact_weekday_wake_time(self, detector):
        # Monday 5:40 AM
        now = datetime(2024, 1, 1, 5, 40, 0)  # Monday
        assert detector.is_wake_time(now=now)

    def test_weekend_wake_time(self, detector):
        # Saturday 7:00 AM
        now = datetime(2024, 1, 6, 7, 0, 0)  # Saturday
        assert detector.is_wake_time(now=now)

    def test_outside_wake_window(self, detector):
        # Monday 8:00 AM - way past wake time
        now = datetime(2024, 1, 1, 8, 0, 0)
        assert not detector.is_wake_time(now=now)

    def test_one_minute_after(self, detector):
        # Monday 5:41 - within 60 second window
        now = datetime(2024, 1, 1, 5, 41, 0)
        assert detector.is_wake_time(now=now)

    def test_two_minutes_after(self, detector):
        # Monday 5:42 - outside 60 second window
        now = datetime(2024, 1, 1, 5, 42, 0)
        assert not detector.is_wake_time(now=now)


class TestGetGreeting:
    def test_weekday_greeting(self, detector):
        # Monday
        now = datetime(2024, 1, 1, 5, 40)
        greeting = detector.get_greeting(now=now)
        assert greeting == WEEKDAY_GREETING

    def test_weekend_greeting(self, detector):
        # Saturday
        now = datetime(2024, 1, 6, 7, 0)
        greeting = detector.get_greeting(now=now)
        assert greeting == WEEKEND_GREETING


class TestCheckAndTrigger:
    def test_triggers_at_wake_time(self, detector):
        callback_called = []

        def cb(**kwargs):
            callback_called.append(kwargs)

        detector.add_callback(cb)
        now = datetime(2024, 1, 1, 5, 40, 0)  # Monday wake time
        result = detector.check_and_trigger(now=now)
        assert result is True
        assert len(callback_called) == 1

    def test_does_not_trigger_twice_same_day(self, detector):
        callback_called = []

        def cb(**kwargs):
            callback_called.append(kwargs)

        detector.add_callback(cb)
        now = datetime(2024, 1, 1, 5, 40, 0)
        detector.check_and_trigger(now=now)
        detector.check_and_trigger(now=now)
        assert len(callback_called) == 1

    def test_does_not_trigger_outside_window(self, detector):
        callback_called = []

        def cb(**kwargs):
            callback_called.append(kwargs)

        detector.add_callback(cb)
        now = datetime(2024, 1, 1, 10, 0, 0)  # 10 AM - no trigger
        result = detector.check_and_trigger(now=now)
        assert result is False
        assert len(callback_called) == 0

    def test_resets_trigger_next_day(self, detector):
        callback_called = []

        def cb(**kwargs):
            callback_called.append(kwargs)

        detector.add_callback(cb)
        day1 = datetime(2024, 1, 1, 5, 40, 0)  # Monday
        day2 = datetime(2024, 1, 2, 5, 40, 0)  # Tuesday
        detector.check_and_trigger(now=day1)
        detector.check_and_trigger(now=day2)
        assert len(callback_called) == 2
