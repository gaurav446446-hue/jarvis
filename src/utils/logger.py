"""Structured logging for Jarvis AI."""
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class JSONLHandler(logging.Handler):
    """Writes log records as newline-delimited JSON to a file."""

    def __init__(self, filepath: str) -> None:
        super().__init__()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(path, "a", encoding="utf-8")  # noqa: WPS515

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self.format(record),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if hasattr(record, "context"):
            entry["context"] = record.context
        try:
            self._file.write(json.dumps(entry) + "\n")
            self._file.flush()
        except Exception:  # pragma: no cover
            self.handleError(record)

    def close(self) -> None:
        try:
            self._file.close()
        finally:
            super().close()


def setup_logger(
    name: str = "jarvis",
    level: str = "INFO",
    log_file: Optional[str] = "data/events_log.jsonl",
    console: bool = True,
) -> logging.Logger:
    """Configure and return the Jarvis root logger.

    Args:
        name: Logger name.
        level: Logging level string (DEBUG / INFO / WARNING / ERROR).
        log_file: Path for JSONL file output; ``None`` disables file logging.
        console: Whether to attach a console (stderr) handler.

    Returns:
        Configured :class:`logging.Logger` instance.
    """
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Avoid adding duplicate handlers when called multiple times.
    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        try:
            jsonl_handler = JSONLHandler(log_file)
            jsonl_handler.setLevel(numeric_level)
            logger.addHandler(jsonl_handler)
        except OSError as exc:  # pragma: no cover
            logger.warning("Could not open log file %s: %s", log_file, exc)

    return logger


def get_logger(name: str = "jarvis") -> logging.Logger:
    """Return (or create) a child logger under the *jarvis* namespace."""
    return logging.getLogger(f"jarvis.{name}" if not name.startswith("jarvis") else name)


def log_event(
    logger: logging.Logger,
    event_type: str,
    data: Optional[Any] = None,
    level: str = "INFO",
) -> None:
    """Emit a structured event log record with optional payload.

    Args:
        logger: Logger instance to use.
        event_type: Short event identifier, e.g. ``"light.on"``.
        data: Arbitrary JSON-serialisable context.
        level: Log level string.
    """
    record_level = getattr(logging, level.upper(), logging.INFO)
    extra = {"context": {"event_type": event_type, "data": data or {}}}
    logger.log(record_level, event_type, extra=extra)
