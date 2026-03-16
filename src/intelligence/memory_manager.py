"""Memory manager - stores user preferences, events, and conversation history."""
import json
import os
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.constants import (
    WEEKDAY_WAKE_TIME,
    WEEKEND_WAKE_TIME,
    FAN_SPEED_DEFAULT,
    COMFORT_TEMP_MIN,
    COMFORT_TEMP_MAX,
    STATE_HOME,
)

logger = get_logger(__name__)

_DEFAULT_PROFILE = {
    "user": "Gaurav",
    "wake_times": {
        "weekday": WEEKDAY_WAKE_TIME,
        "weekend": WEEKEND_WAKE_TIME,
    },
    "preferences": {
        "comfort_temp_min": COMFORT_TEMP_MIN,
        "comfort_temp_max": COMFORT_TEMP_MAX,
        "preferred_fan_speed": FAN_SPEED_DEFAULT,
    },
    "presence_state": STATE_HOME,
    "created_at": datetime.now().isoformat(),
}


class MemoryManager:
    """Persist user profile, preferences, events, and conversation history."""

    def __init__(self, config=None):
        if config is not None:
            self._profile_path = config.user_profile_path
            self._events_log = config.events_log_path
            self._conversation_log = config.conversation_log_path
        else:
            self._profile_path = "models/user_profile.json"
            self._events_log = "data/events_log.jsonl"
            self._conversation_log = "data/conversation_history.jsonl"

        Path(self._profile_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self._events_log).parent.mkdir(parents=True, exist_ok=True)
        Path(self._conversation_log).parent.mkdir(parents=True, exist_ok=True)

        self._profile: dict = self._load_profile()

    # ------------------------------------------------------------------
    # User profile
    # ------------------------------------------------------------------

    def _load_profile(self) -> dict:
        if os.path.exists(self._profile_path):
            try:
                with open(self._profile_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning("Could not load profile: %s - using defaults", e)
        return dict(_DEFAULT_PROFILE)

    def save_profile(self):
        """Persist the current user profile to disk."""
        with open(self._profile_path, "w") as f:
            json.dump(self._profile, f, indent=2)
        logger.debug("Profile saved to %s", self._profile_path)

    @property
    def profile(self) -> dict:
        return self._profile

    def get_preference(self, key: str, default=None):
        return self._profile.get("preferences", {}).get(key, default)

    def set_preference(self, key: str, value):
        self._profile.setdefault("preferences", {})[key] = value
        self.save_profile()

    def get_presence_state(self) -> str:
        return self._profile.get("presence_state", STATE_HOME)

    def set_presence_state(self, state: str):
        self._profile["presence_state"] = state
        self.save_profile()

    # ------------------------------------------------------------------
    # Event logging
    # ------------------------------------------------------------------

    def log_event(self, event_type: str, data: dict = None):
        """Append an event record to events_log.jsonl."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data or {},
        }
        with open(self._events_log, "a") as f:
            f.write(json.dumps(record) + "\n")

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------

    def log_conversation(self, role: str, content: str):
        """Append a chat message to conversation_history.jsonl."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
        }
        with open(self._conversation_log, "a") as f:
            f.write(json.dumps(record) + "\n")

    def load_recent_conversations(self, n: int = 50) -> list[dict]:
        """Return the last n conversation records."""
        if not os.path.exists(self._conversation_log):
            return []
        records = []
        try:
            with open(self._conversation_log) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        except (IOError, json.JSONDecodeError):
            return []
        return records[-n:]
