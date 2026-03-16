"""Tests for PresenceDetector."""
from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from src.intelligence.presence_detector import PresenceDetector
from src.intelligence.appliance_controller import ApplianceController
from src.utils.constants import DeviceState, PresenceState


class TestArrival:
    def test_away_to_home_on_motion(self, presence_detector, appliance):
        assert presence_detector.state == PresenceState.AWAY
        result = presence_detector.detect_motion(motion_detected=True)
        assert result == "arrival"
        assert presence_detector.state == PresenceState.HOME

    def test_arrival_turns_on_light(self, appliance, voice):
        det = PresenceDetector(appliance_controller=appliance, voice_processor=voice)
        det.detect_motion(motion_detected=True)
        assert appliance.light_state == DeviceState.ON

    def test_arrival_sets_fan_50(self, appliance, voice):
        det = PresenceDetector(appliance_controller=appliance, voice_processor=voice)
        det.detect_motion(motion_detected=True)
        assert appliance.fan_speed == 50

    def test_arrival_says_welcome(self, appliance, voice):
        det = PresenceDetector(appliance_controller=appliance, voice_processor=voice)
        det.detect_motion(motion_detected=True)
        voice.say.assert_called_once_with("Welcome home, Sir!")

    def test_mark_arrived(self, presence_detector):
        result = presence_detector.mark_arrived()
        assert presence_detector.state == PresenceState.HOME
        assert result == "arrival"

    def test_motion_while_home_returns_none(self, presence_detector):
        presence_detector.detect_motion(motion_detected=True)  # arrive
        result = presence_detector.detect_motion(motion_detected=True)  # still home
        assert result is None


class TestAbsenceDetection:
    def test_no_absence_within_threshold(self, appliance, voice):
        det = PresenceDetector(
            appliance_controller=appliance,
            voice_processor=voice,
            absence_threshold_seconds=7200,
        )
        det.detect_motion(True)  # arrive
        now = datetime.now()
        # Only 1 hour away – no trigger
        det.detect_motion(False, timestamp=now)
        det.detect_motion(False, timestamp=now + timedelta(hours=1))
        assert det.state == PresenceState.HOME

    def test_extended_absence_turns_off_appliances(self, appliance, voice):
        det = PresenceDetector(
            appliance_controller=appliance,
            voice_processor=voice,
            absence_threshold_seconds=10,
        )
        det.detect_motion(True)  # arrive
        now = datetime.now()
        det.detect_motion(False, timestamp=now)  # start absence timer
        result = det.detect_motion(False, timestamp=now + timedelta(seconds=15))
        assert result == "extended_absence"
        assert det.state == PresenceState.AWAY
        assert appliance.light_state == DeviceState.OFF
        assert appliance.fan_speed == 0

    def test_is_extended_absence_false_when_home(self, presence_detector):
        presence_detector.detect_motion(True)
        assert presence_detector.is_extended_absence() is False

    def test_is_extended_absence_true_after_threshold(self, appliance, voice):
        det = PresenceDetector(appliance_controller=appliance, voice_processor=voice,
                               absence_threshold_seconds=5)
        det.detect_motion(True)
        now = datetime.now()
        det.detect_motion(False, timestamp=now)
        assert det.is_extended_absence(now=now + timedelta(seconds=10)) is True


class TestDeparture:
    def test_mark_departed(self, presence_detector):
        presence_detector.mark_arrived()
        msg = presence_detector.mark_departed()
        assert presence_detector.state == PresenceState.AWAY
        assert "Goodbye" in msg or "Departure" in msg

    def test_state_transitions(self, presence_detector):
        assert presence_detector.state == PresenceState.AWAY
        presence_detector.mark_arrived()
        assert presence_detector.state == PresenceState.HOME
        presence_detector.mark_departed()
        assert presence_detector.state == PresenceState.AWAY
