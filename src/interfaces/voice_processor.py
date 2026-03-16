"""Voice processor (mocked for Phase 1)."""
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceProcessor:
    """
    Text-to-speech and speech-to-text stubs for Phase 1.

    Phase 2 will integrate pyttsx3 / whisper for real voice I/O.
    """

    def speak(self, message: str) -> bool:
        """Print message as Jarvis voice output (mock)."""
        logger.info("[VOICE] %s", message)
        print(f"\n🔊 Jarvis says: {message}\n")
        return True

    def listen(self) -> str:
        """Return empty string - real mic input not available in Phase 1."""
        logger.debug("Voice listen() called - not implemented in Phase 1")
        return ""
