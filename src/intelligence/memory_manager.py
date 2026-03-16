"""JSON-based local storage and event logging."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.utils.logger import get_logger

logger = get_logger("memory_manager")

_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class MemoryManager:
    """Persist user profile, conversation history, and events to JSON files.

    All file I/O is protected by a :class:`threading.Lock` for thread safety.

    Args:
        data_dir: Directory to store all data files.
    """

    def __init__(self, data_dir: Optional[str] = None) -> None:
        self._dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

        self._events_file = self._dir / "events_log.jsonl"
        self._history_file = self._dir / "conversation_history.jsonl"
        self._profile_file = self._dir / "user_profile.json"
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # User profile
    # ------------------------------------------------------------------

    def save_profile(self, profile: Dict[str, Any]) -> None:
        """Persist *profile* to ``user_profile.json``."""
        with self._lock:
            with open(self._profile_file, "w", encoding="utf-8") as fh:
                json.dump(profile, fh, indent=2)
        logger.debug("Profile saved")

    def load_profile(self) -> Optional[Dict[str, Any]]:
        """Load and return the stored user profile, or ``None`` if absent."""
        with self._lock:
            if not self._profile_file.exists():
                return None
            with open(self._profile_file, "r", encoding="utf-8") as fh:
                return json.load(fh)

    # ------------------------------------------------------------------
    # Event logging
    # ------------------------------------------------------------------

    def log_event(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """Append a structured event record to ``events_log.jsonl``.

        Args:
            event_type: Short event identifier, e.g. ``"light.on"``.
            data: Arbitrary JSON-serialisable payload.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "data": data or {},
        }
        with self._lock:
            with open(self._events_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        logger.debug("Event logged: %s", event_type)

    def get_events(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Read recent events from the log.

        Args:
            limit: Maximum number of events to return (most recent first).
            event_type: Optional filter on ``event_type`` field.

        Returns:
            List of event dictionaries.
        """
        with self._lock:
            if not self._events_file.exists():
                return []
            lines = self._events_file.read_text(encoding="utf-8").splitlines()

        events: List[Dict[str, Any]] = []
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                if event_type and record.get("event_type") != event_type:
                    continue
                events.append(record)
                if len(events) >= limit:
                    break
            except json.JSONDecodeError:
                continue
        return events

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------

    def save_conversation_turn(self, role: str, content: str) -> None:
        """Append one conversation turn to ``conversation_history.jsonl``.

        Args:
            role: ``"user"`` or ``"assistant"``.
            content: Message text.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        with self._lock:
            with open(self._history_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")

    def get_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Return the last *limit* conversation turns (oldest first)."""
        with self._lock:
            if not self._history_file.exists():
                return []
            lines = self._history_file.read_text(encoding="utf-8").splitlines()

        turns: List[Dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                turns.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return turns[-limit:]

    def clear_history(self) -> None:
        """Erase the conversation history file."""
        with self._lock:
            if self._history_file.exists():
                self._history_file.unlink()
        logger.debug("Conversation history cleared")
