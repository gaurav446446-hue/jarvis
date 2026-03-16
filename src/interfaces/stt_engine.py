"""Speech-to-text engine wrapper for Jarvis AI."""
from __future__ import annotations

from typing import Optional

from src.utils.logger import get_logger

logger = get_logger("stt_engine")

try:
    import speech_recognition as _sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False


class STTEngine:
    """Speech-to-text engine using the ``speech_recognition`` library.

    Uses the Google Web Speech API for transcription and ``pyaudio`` for
    microphone access.  Degrades gracefully when either dependency is missing.

    Args:
        energy_threshold: Minimum audio energy to consider for recording
            (default 4000; lower values are more sensitive).
        microphone_index: Specific microphone device index.  ``None`` means
            auto-detect the default microphone.
    """

    def __init__(
        self,
        energy_threshold: int = 4000,
        microphone_index: Optional[int] = None,
    ) -> None:
        self._mic_index = microphone_index
        self._available = False
        self._recognizer = None

        if not _SR_AVAILABLE:
            logger.info("speech_recognition not installed – STT unavailable")
            return

        try:
            self._recognizer = _sr.Recognizer()
            self._recognizer.energy_threshold = energy_threshold
            # Probe for pyaudio (required by sr.Microphone)
            import pyaudio as _pyaudio  # noqa: F401
            self._available = True
            logger.debug(
                "STTEngine initialised (energy_threshold=%d, mic_index=%s)",
                energy_threshold,
                microphone_index,
            )
        except ImportError:
            logger.warning("pyaudio not installed – STT unavailable")
        except Exception as exc:
            logger.warning("STT init failed: %s – STT unavailable", exc)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def listen(self, timeout: int = 10) -> str:
        """Listen to the microphone and return transcribed text.

        Adjusts for ambient noise before capturing, then sends the recorded
        audio to the Google Web Speech API.

        Args:
            timeout: Maximum seconds to wait for speech to begin.

        Returns:
            Transcribed text, or an empty string when nothing was captured
            or an error occurred.
        """
        if not self._available or not _SR_AVAILABLE:
            logger.debug("STT unavailable – returning empty string")
            return ""

        try:
            mic_kwargs: dict = {}
            if self._mic_index is not None:
                mic_kwargs["device_index"] = self._mic_index

            with _sr.Microphone(**mic_kwargs) as source:
                logger.info("Adjusting for ambient noise…")
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Listening for speech (timeout=%ds)…", timeout)
                audio = self._recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=timeout,
                )

            text: str = self._recognizer.recognize_google(audio)
            logger.info("Recognised: %s", text)
            return text

        except _sr.WaitTimeoutError:
            logger.debug("Listen timed out – no speech detected")
            return ""
        except _sr.UnknownValueError:
            logger.debug("Google STT could not understand audio")
            return ""
        except _sr.RequestError as exc:
            logger.warning("Google STT API error: %s", exc)
            return ""
        except Exception as exc:
            logger.warning("STT unexpected error: %s", exc)
            return ""

    @property
    def available(self) -> bool:
        """``True`` if the STT engine is fully operational."""
        return self._available
