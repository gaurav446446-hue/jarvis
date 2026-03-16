"""Mock motion event generator for testing and demos."""
from __future__ import annotations

import random
import time
from datetime import datetime


def generate_motion_events(count: int = 10, interval: float = 0.5) -> list[dict]:
    """Generate a list of mock motion sensor events.

    Args:
        count: Number of events to generate.
        interval: Seconds between events (used when ``stream=True``).

    Returns:
        List of event dicts with ``timestamp`` and ``motion`` keys.
    """
    events = []
    for i in range(count):
        motion = random.random() < 0.4
        events.append(
            {
                "timestamp": datetime.now().isoformat(),
                "motion": motion,
                "sequence": i,
            }
        )
    return events


def stream_motion_events(count: int = 20, interval: float = 1.0) -> None:
    """Print mock motion events to stdout at *interval* second intervals.

    Args:
        count: Total events to emit.
        interval: Delay between events in seconds.
    """
    print(f"Streaming {count} mock motion events (interval={interval}s)…")
    for event in generate_motion_events(count):
        status = "MOTION" if event["motion"] else "quiet"
        print(f"[{event['timestamp']}] {status}")
        time.sleep(interval)
    print("Done.")


if __name__ == "__main__":
    stream_motion_events(count=10, interval=0.3)
