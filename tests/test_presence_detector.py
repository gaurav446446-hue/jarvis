"""Tests for PresenceDetector."""
import pytest
from datetime import datetime, timedelta

from src.intelligence.presence_detector import PresenceDetector
from src.utils.constants import STATE_HOME, STATE_AWAY


@pytest.fixture
def detector(config, memory):
    return PresenceDetector(config=config, memory=memory)


class TestInitialState:
    def test_default_state_is_home(self, detector):
        assert detector.state == STATE_HOME


class TestUpdate:
    def test_motion_keeps_home(self, detector):
        state = detector.update(motion_detected=True)
        assert state == STATE_HOME

    def test_no_motion_for_short_period_stays_home(self, detector):
        now = datetime.now()
        state = detector.update(motion_detected=False, now=now)
        assert state == STATE_HOME

    def test_no_motion_long_enough_triggers_away(self, detector):
        # Simulate last motion 3 hours ago
        past = datetime.now() - timedelta(hours=3)
        detector._last_motion_time = past
        state = detector.update(motion_detected=False)
        assert state == STATE_AWAY

    def test_motion_after_away_triggers_arrival(self, detector):
        # First set to AWAY
        past = datetime.now() - timedelta(hours=3)
        detector._last_motion_time = past
        detector.update(motion_detected=False)
        assert detector.state == STATE_AWAY

        # Now motion detected
        state = detector.update(motion_detected=True)
        assert state == STATE_HOME


class TestCallbacks:
    def test_arrival_callback_fires(self, detector):
        fired = []
        detector.add_arrival_callback(lambda: fired.append(True))

        # Go to AWAY first
        past = datetime.now() - timedelta(hours=3)
        detector._last_motion_time = past
        detector.update(motion_detected=False)

        # Then arrive
        detector.update(motion_detected=True)
        assert len(fired) == 1

    def test_departure_callback_fires(self, detector):
        fired = []
        detector.add_departure_callback(lambda: fired.append(True))

        past = datetime.now() - timedelta(hours=3)
        detector._last_motion_time = past
        detector.update(motion_detected=False)

        assert len(fired) == 1

    def test_force_arrival(self, detector):
        # Set away first
        detector._state = STATE_AWAY
        detector.force_arrival()
        assert detector.state == STATE_HOME

    def test_force_departure(self, detector):
        detector.force_departure()
        assert detector.state == STATE_AWAY


class TestMemoryIntegration:
    def test_state_persisted_on_arrival(self, detector, memory):
        detector._state = STATE_AWAY
        detector.force_arrival()
        assert memory.get_presence_state() == STATE_HOME

    def test_state_persisted_on_departure(self, detector, memory):
        detector.force_departure()
        assert memory.get_presence_state() == STATE_AWAY
