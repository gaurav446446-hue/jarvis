"""Mock voice input/output for Phase 1."""
from __future__ import annotations

from src.utils.logger import get_logger

logger = get_logger("voice_processor")

try:
    import pyttsx3 as _pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False


class VoiceProcessor:
    """Provide text-to-speech output and mock voice input.

    In Phase 1, TTS uses ``pyttsx3`` if available, otherwise falls back to
    console output.  Voice input (STT) is not implemented in Phase 1.

    Args:
        use_tts: Force TTS on (``True``) or off (``False``). ``None`` means
            auto-detect based on library availability.
    """

    def __init__(self, use_tts: bool | None = None) -> None:
        if use_tts is None:
            self._use_tts = _PYTTSX3_AVAILABLE
        else:
            self._use_tts = use_tts and _PYTTSX3_AVAILABLE

        self._engine = None
        if self._use_tts:
            try:
                self._engine = _pyttsx3.init()
            except Exception as exc:
                logger.warning("pyttsx3 init failed: %s – falling back to console", exc)
                self._use_tts = False

    def say(self, message: str) -> None:
        """Speak *message* via TTS or print it to the console.

        Args:
            message: Text to vocalise.
        """
        if self._use_tts and self._engine:
            try:
                self._engine.say(message)
                self._engine.runAndWait()
                return
            except Exception as exc:
                logger.warning("TTS error: %s", exc)
        print(f"Jarvis: {message}")
        logger.info("Jarvis said: %s", message)

    def listen(self) -> str:
        """Mock voice input – always returns an empty string in Phase 1."""
        logger.debug("Voice input not available in Phase 1")
        return ""

    @property
    def tts_available(self) -> bool:
        return self._use_tts
