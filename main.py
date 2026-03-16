"""
Jarvis AI - Smart Room Assistant
Phase 1 MVP entry point
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import get_logger
from src.utils.config import Config
from src.intelligence.wake_up_detector import WakeUpDetector
from src.intelligence.presence_detector import PresenceDetector
from src.intelligence.memory_manager import MemoryManager
from src.interfaces.cli_chat import CLIChat

logger = get_logger(__name__)


def main():
    """Main entry point for Jarvis AI."""
    try:
        config = Config()

        logger.info("Initializing Jarvis AI - Phase 1 MVP")

        memory = MemoryManager(config)
        wake_detector = WakeUpDetector(config, memory)
        presence_detector = PresenceDetector(config, memory)

        cli = CLIChat(config, memory, wake_detector, presence_detector)

        cli.run()

    except KeyboardInterrupt:
        print("\n\nGoodbye, Sir! Jarvis is shutting down.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
