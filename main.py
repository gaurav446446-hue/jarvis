"""Jarvis AI Smart Room Assistant – entry point."""
from __future__ import annotations

import argparse
import sys

from src.utils.config import get_config
from src.utils.logger import setup_logger


def _choose_mode() -> str:
    """Prompt the user to choose between voice and text mode.

    Returns:
        ``"voice"`` or ``"text"``.
    """
    print("\nHow would you like to chat with Jarvis?")
    print("  1. Voice  – speak via microphone, hear via speakers")
    print("  2. Text   – type commands, read responses")
    while True:
        choice = input("Enter 1 or 2 (default: 2): ").strip()
        if choice in ("", "2", "text"):
            return "text"
        if choice in ("1", "voice"):
            return "voice"
        print("Please enter 1 or 2.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Jarvis AI Smart Room Assistant")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--voice",
        action="store_true",
        help="Start in voice chat mode (microphone + speakers)",
    )
    group.add_argument(
        "--text",
        action="store_true",
        help="Start in text (CLI) chat mode",
    )
    args = parser.parse_args()

    cfg = get_config()
    setup_logger(
        level=cfg.logging.level,
        log_file=cfg.logging.file,
        console=cfg.logging.console,
    )

    if args.voice:
        mode = "voice"
    elif args.text:
        mode = "text"
    else:
        mode = _choose_mode()

    if mode == "voice":
        from src.interfaces.voice_chat import VoiceChat
        VoiceChat().start()
    else:
        from src.interfaces.cli_chat import CLIChat
        CLIChat().start()


if __name__ == "__main__":
    main()
