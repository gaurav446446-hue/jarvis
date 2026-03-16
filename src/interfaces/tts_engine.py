"""Text-to-speech engine wrapper for Jarvis AI."""
from __future__ import annotations

from src.utils.logger import get_logger

logger = get_logger("tts_engine")

try:
    import pyttsx3 as _pyttsx3
    _PYTTSX3_AVAILABLE = True
except ImportError:
    _PYTTSX3_AVAILABLE = False


class TTSEngine:
    """Text-to-speech engine using pyttsx3 (offline).

    Provides configurable voice rate, volume, and gender.  Falls back to
    console output when pyttsx3 is unavailable or fails to initialise.

    Args:
        rate: Speech rate in words per minute (default 150).
        volume: Volume level from 0.0 to 1.0 (default 0.9).
        voice: Voice gender – ``"male"`` or ``"female"`` (default ``"male"``).
    """

    def __init__(
        self,
        rate: int = 150,
        volume: float = 0.9,
        voice: str = "male",
    ) -> None:
        self._rate = rate
        self._volume = volume
        self._engine = None
        self._available = False

        if _PYTTSX3_AVAILABLE:
            try:
                self._engine = _pyttsx3.init()
                self._engine.setProperty("rate", rate)
                self._engine.setProperty("volume", volume)
                self._set_voice(voice)
                self._available = True
                logger.debug("TTSEngine initialised (rate=%d, volume=%.1f)", rate, volume)
            except Exception as exc:
                logger.warning("pyttsx3 init failed: %s – falling back to console", exc)
        else:
            logger.info("pyttsx3 not installed – TTS will use console output")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def speak(self, text: str) -> None:
        """Speak *text* through the system speakers.

        Falls back to ``print`` when TTS is unavailable.

        Args:
            text: The text to vocalise.
        """
        if self._available and self._engine:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
                logger.info("Jarvis said: %s", text)
                return
            except Exception as exc:
                logger.warning("TTS error: %s – falling back to console", exc)
        print(f"Jarvis: {text}")
        logger.info("Jarvis said (console): %s", text)

    def set_voice(self, gender: str) -> None:
        """Set voice gender.

        Args:
            gender: ``"male"`` or ``"female"``.
        """
        self._set_voice(gender)

    def set_rate(self, rate: int) -> None:
        """Set speech rate in words per minute.

        Args:
            rate: Words per minute (typical range 100–200).
        """
        if self._engine:
            self._engine.setProperty("rate", rate)
        self._rate = rate

    def set_volume(self, volume: float) -> None:
        """Set output volume.

        Args:
            volume: Level from 0.0 (silent) to 1.0 (maximum).
        """
        if self._engine:
            self._engine.setProperty("volume", volume)
        self._volume = volume

    @property
    def available(self) -> bool:
        """``True`` if the TTS engine is fully operational."""
        return self._available

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _set_voice(self, gender: str) -> None:
        if not self._engine:
            return
        try:
            voices = self._engine.getProperty("voices")
            if not voices:
                return
            if gender.lower() == "female" and len(voices) > 1:
                self._engine.setProperty("voice", voices[1].id)
            else:
                self._engine.setProperty("voice", voices[0].id)
        except Exception as exc:
            logger.warning("Could not set voice gender: %s", exc)
