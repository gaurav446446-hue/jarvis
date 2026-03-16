"""Jarvis AI Smart Room Assistant – entry point."""
from __future__ import annotations

import sys

from src.utils.config import get_config
from src.utils.logger import setup_logger


def main() -> None:
    cfg = get_config()
    setup_logger(
        level=cfg.logging.level,
        log_file=cfg.logging.file,
        console=cfg.logging.console,
    )

    from src.interfaces.cli_chat import CLIChat
    cli = CLIChat()
    cli.start()


if __name__ == "__main__":
    main()
