"""Tests for IntentClassifier."""
from __future__ import annotations

import pytest

from src.core.intent_classifier import IntentClassifier
from src.utils.constants import Intent


@pytest.fixture()
def clf() -> IntentClassifier:
    return IntentClassifier()


class TestGreeting:
    def test_good_morning(self, clf):
        intent, _ = clf.classify("Good morning")
        assert intent == Intent.GREETING

    def test_hello(self, clf):
        intent, _ = clf.classify("Hello!")
        assert intent == Intent.GREETING

    def test_hi(self, clf):
        intent, _ = clf.classify("Hi")
        assert intent == Intent.GREETING

    def test_hey_jarvis(self, clf):
        intent, _ = clf.classify("Hey Jarvis")
        assert intent == Intent.GREETING


class TestControl:
    def test_turn_on_light(self, clf):
        intent, params = clf.classify("Turn on the light")
        assert intent == Intent.CONTROL
        assert params.get("device") == "light"
        assert params.get("action") == "turn_on"

    def test_turn_off_light(self, clf):
        intent, params = clf.classify("Turn off the light")
        assert intent == Intent.CONTROL
        assert params.get("device") == "light"
        assert params.get("action") == "turn_off"

    def test_set_fan_speed(self, clf):
        intent, params = clf.classify("Set fan speed to 75%")
        assert intent == Intent.CONTROL
        assert params.get("device") == "fan"
        assert params.get("value") == 75

    def test_turn_on_fan(self, clf):
        intent, params = clf.classify("Turn on the fan")
        assert intent == Intent.CONTROL
        assert params.get("device") == "fan"


class TestQuery:
    def test_what_time(self, clf):
        intent, _ = clf.classify("What's the time?")
        assert intent == Intent.QUERY

    def test_temperature_query(self, clf):
        intent, _ = clf.classify("What's the temperature?")
        assert intent == Intent.QUERY

    def test_room_conditions(self, clf):
        intent, _ = clf.classify("Check room conditions")
        assert intent == Intent.QUERY

    def test_status(self, clf):
        intent, _ = clf.classify("Show me the status")
        assert intent == Intent.QUERY


class TestContext:
    def test_leaving(self, clf):
        intent, params = clf.classify("I'm leaving")
        assert intent == Intent.CONTEXT
        assert params.get("event") == "departure"

    def test_im_home(self, clf):
        intent, params = clf.classify("I'm home")
        assert intent == Intent.CONTEXT
        assert params.get("event") == "arrival"

    def test_goodbye(self, clf):
        intent, params = clf.classify("Goodbye")
        assert intent == Intent.CONTEXT

    def test_just_arrived(self, clf):
        intent, params = clf.classify("Just arrived home")
        assert intent == Intent.CONTEXT
        assert params.get("event") == "arrival"


class TestComfort:
    def test_too_hot(self, clf):
        intent, _ = clf.classify("It's too hot")
        assert intent == Intent.COMFORT

    def test_too_cold(self, clf):
        intent, _ = clf.classify("Too cold in here")
        assert intent == Intent.COMFORT

    def test_adjust_fan(self, clf):
        intent, _ = clf.classify("Adjust the fan")
        assert intent == Intent.COMFORT


class TestExplain:
    def test_why(self, clf):
        intent, _ = clf.classify("Why did you do that?")
        assert intent == Intent.EXPLAIN

    def test_help(self, clf):
        intent, _ = clf.classify("help")
        assert intent == Intent.EXPLAIN

    def test_what_can_you_do(self, clf):
        intent, _ = clf.classify("What can you do?")
        assert intent == Intent.EXPLAIN


class TestGetIntentName:
    def test_returns_string(self, clf):
        name = clf.get_intent_name("Good morning")
        assert isinstance(name, str)
        assert name == Intent.GREETING.value
