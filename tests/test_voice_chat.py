"""Unit tests for voice chat components.

All audio hardware interactions (pyttsx3 engine, pyaudio microphone) are
mocked so the tests run on any machine without real audio devices.
"""
from __future__ import annotations

import sys
import importlib
from types import ModuleType
from unittest.mock import MagicMock, patch, call

import pytest

from src.interfaces.voice_chat import VoiceChat
from src.intelligence.appliance_controller import ApplianceController
from src.hardware.sensor_reader import SensorReader
from src.core.jarvis_llm import JarvisLLM


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_pyttsx3() -> tuple[ModuleType, MagicMock]:
    """Return a mock pyttsx3 module and the engine instance it produces."""
    mock_engine = MagicMock()
    voices = [MagicMock(id="voice-male"), MagicMock(id="voice-female")]
    mock_engine.getProperty.return_value = voices

    mock_pyttsx3 = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
    return mock_pyttsx3, mock_engine


def _load_tts_engine_with_mock_pyttsx3() -> tuple:
    """Import TTSEngine with a mocked pyttsx3 in sys.modules."""
    mock_pyttsx3, mock_engine = _make_mock_pyttsx3()

    # Inject the mock before importing so the try/except in the module sees it
    sys.modules.setdefault("pyttsx3", mock_pyttsx3)
    # Force a fresh import so the flag is set correctly
    if "src.interfaces.tts_engine" in sys.modules:
        del sys.modules["src.interfaces.tts_engine"]

    sys.modules["pyttsx3"] = mock_pyttsx3
    import src.interfaces.tts_engine as tts_mod
    importlib.reload(tts_mod)

    return tts_mod, mock_pyttsx3, mock_engine


def _make_mock_sr_module() -> ModuleType:
    """Return a mock speech_recognition module with realistic exception types."""
    mock_sr = MagicMock()
    mock_sr.WaitTimeoutError = type("WaitTimeoutError", (Exception,), {})
    mock_sr.UnknownValueError = type("UnknownValueError", (Exception,), {})
    mock_sr.RequestError = type("RequestError", (Exception,), {})
    return mock_sr


def _load_stt_engine_with_mock_sr(recognized: str = "") -> tuple:
    """Import STTEngine with mocked speech_recognition and pyaudio."""
    mock_sr = _make_mock_sr_module()
    mock_recognizer = MagicMock()
    mock_recognizer.recognize_google.return_value = recognized
    mock_recognizer.listen.return_value = MagicMock()
    mock_sr.Recognizer.return_value = mock_recognizer

    mock_mic = MagicMock()
    mock_mic.__enter__ = MagicMock(return_value=MagicMock())
    mock_mic.__exit__ = MagicMock(return_value=False)
    mock_sr.Microphone.return_value = mock_mic

    mock_pyaudio = MagicMock()

    sys.modules["speech_recognition"] = mock_sr
    sys.modules["pyaudio"] = mock_pyaudio

    if "src.interfaces.stt_engine" in sys.modules:
        del sys.modules["src.interfaces.stt_engine"]

    import src.interfaces.stt_engine as stt_mod
    importlib.reload(stt_mod)

    return stt_mod, mock_sr, mock_recognizer


# ---------------------------------------------------------------------------
# TTSEngine tests
# ---------------------------------------------------------------------------

class TestTTSEngine:
    """Tests for TTSEngine behaviour, isolated from real audio hardware."""

    def test_available_when_pyttsx3_present(self) -> None:
        tts_mod, mock_pyttsx3, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        assert tts.available is True

    def test_unavailable_when_pyttsx3_missing(self) -> None:
        # Remove any injected mock so the module falls through to ImportError path
        sys.modules.pop("pyttsx3", None)
        if "src.interfaces.tts_engine" in sys.modules:
            del sys.modules["src.interfaces.tts_engine"]
        import src.interfaces.tts_engine as tts_mod
        importlib.reload(tts_mod)

        with patch.object(tts_mod, "_PYTTSX3_AVAILABLE", False):
            tts = tts_mod.TTSEngine()
        assert tts.available is False

    def test_speak_calls_engine(self) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        tts.speak("Hello Sir")
        mock_engine.say.assert_called_once_with("Hello Sir")
        mock_engine.runAndWait.assert_called_once()

    def test_speak_falls_back_to_print_when_unavailable(self, capsys) -> None:
        sys.modules.pop("pyttsx3", None)
        if "src.interfaces.tts_engine" in sys.modules:
            del sys.modules["src.interfaces.tts_engine"]
        import src.interfaces.tts_engine as tts_mod
        importlib.reload(tts_mod)

        with patch.object(tts_mod, "_PYTTSX3_AVAILABLE", False):
            tts = tts_mod.TTSEngine()
        tts.speak("Fallback message")
        captured = capsys.readouterr()
        assert "Fallback message" in captured.out

    def test_speak_falls_back_on_engine_error(self, capsys) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        mock_engine.say.side_effect = RuntimeError("audio error")
        tts = tts_mod.TTSEngine()
        tts.speak("Error test")
        captured = capsys.readouterr()
        assert "Error test" in captured.out

    def test_set_rate(self) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        tts.set_rate(180)
        mock_engine.setProperty.assert_any_call("rate", 180)

    def test_set_volume(self) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        tts.set_volume(0.5)
        mock_engine.setProperty.assert_any_call("volume", 0.5)

    def test_set_voice_male(self) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        voices = [MagicMock(id="voice-male"), MagicMock(id="voice-female")]
        mock_engine.getProperty.return_value = voices
        tts.set_voice("male")
        mock_engine.setProperty.assert_any_call("voice", "voice-male")

    def test_set_voice_female(self) -> None:
        tts_mod, _, mock_engine = _load_tts_engine_with_mock_pyttsx3()
        tts = tts_mod.TTSEngine()
        voices = [MagicMock(id="voice-male"), MagicMock(id="voice-female")]
        mock_engine.getProperty.return_value = voices
        tts.set_voice("female")
        mock_engine.setProperty.assert_any_call("voice", "voice-female")


# ---------------------------------------------------------------------------
# STTEngine tests
# ---------------------------------------------------------------------------

class TestSTTEngine:
    """Tests for STTEngine, isolated from real microphone hardware."""

    def test_available_when_sr_and_pyaudio_present(self) -> None:
        stt_mod, mock_sr, _ = _load_stt_engine_with_mock_sr()
        stt = stt_mod.STTEngine()
        assert stt.available is True

    def test_unavailable_when_sr_missing(self) -> None:
        sys.modules.pop("speech_recognition", None)
        if "src.interfaces.stt_engine" in sys.modules:
            del sys.modules["src.interfaces.stt_engine"]
        import src.interfaces.stt_engine as stt_mod
        importlib.reload(stt_mod)

        with patch.object(stt_mod, "_SR_AVAILABLE", False):
            stt = stt_mod.STTEngine()
        assert stt.available is False

    def test_listen_returns_empty_when_unavailable(self) -> None:
        sys.modules.pop("speech_recognition", None)
        if "src.interfaces.stt_engine" in sys.modules:
            del sys.modules["src.interfaces.stt_engine"]
        import src.interfaces.stt_engine as stt_mod
        importlib.reload(stt_mod)

        with patch.object(stt_mod, "_SR_AVAILABLE", False):
            stt = stt_mod.STTEngine()
        assert stt.listen() == ""

    def test_listen_returns_recognised_text(self) -> None:
        stt_mod, mock_sr, mock_recognizer = _load_stt_engine_with_mock_sr("turn on the light")
        stt = stt_mod.STTEngine()
        result = stt.listen(timeout=5)
        assert result == "turn on the light"

    def test_listen_returns_empty_on_timeout(self) -> None:
        stt_mod, mock_sr, mock_recognizer = _load_stt_engine_with_mock_sr()
        mock_recognizer.listen.side_effect = mock_sr.WaitTimeoutError()
        stt = stt_mod.STTEngine()
        result = stt.listen(timeout=1)
        assert result == ""

    def test_listen_returns_empty_on_unknown_value(self) -> None:
        stt_mod, mock_sr, mock_recognizer = _load_stt_engine_with_mock_sr()
        mock_recognizer.listen.return_value = MagicMock()
        mock_recognizer.recognize_google.side_effect = mock_sr.UnknownValueError()
        stt = stt_mod.STTEngine()
        result = stt.listen()
        assert result == ""

    def test_listen_returns_empty_on_request_error(self) -> None:
        stt_mod, mock_sr, mock_recognizer = _load_stt_engine_with_mock_sr()
        mock_recognizer.listen.return_value = MagicMock()
        mock_recognizer.recognize_google.side_effect = mock_sr.RequestError("network")
        stt = stt_mod.STTEngine()
        result = stt.listen()
        assert result == ""


# ---------------------------------------------------------------------------
# VoiceChat tests
# ---------------------------------------------------------------------------

class TestVoiceChat:
    """Integration tests for VoiceChat with mocked audio engines."""

    def _make_voice_chat(self) -> tuple[VoiceChat, MagicMock, MagicMock, JarvisLLM]:
        from src.interfaces.tts_engine import TTSEngine
        from src.interfaces.stt_engine import STTEngine

        mock_tts = MagicMock(spec=TTSEngine)
        mock_tts.available = True
        mock_stt = MagicMock(spec=STTEngine)
        mock_stt.available = False  # Use keyboard fallback in tests

        appliance = ApplianceController()
        sensor = SensorReader(temperature=24.0, humidity=65.0, motion_probability=0.0)
        jarvis = JarvisLLM(appliance_controller=appliance, sensor_reader=sensor)

        vc = VoiceChat(jarvis=jarvis)
        vc._tts = mock_tts
        vc._stt = mock_stt
        return vc, mock_tts, mock_stt, jarvis

    def test_tts_speaks_greeting_on_start(self) -> None:
        vc, mock_tts, mock_stt, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", side_effect=["Turn on the light", EOFError]):
            try:
                vc.start()
            except SystemExit:
                pass

        calls = [str(c) for c in mock_tts.speak.call_args_list]
        assert any("Hello" in c or "Jarvis" in c for c in calls)

    def test_exit_on_goodbye(self) -> None:
        vc, mock_tts, _, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", return_value="goodbye"):
            vc.start()

        farewell_calls = [
            c for c in mock_tts.speak.call_args_list
            if "Goodbye" in str(c) or "goodbye" in str(c).lower()
        ]
        assert farewell_calls

    def test_exit_on_quit(self) -> None:
        vc, mock_tts, _, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", return_value="quit"):
            vc.start()

        assert mock_tts.speak.call_count >= 2

    def test_empty_input_is_ignored(self) -> None:
        vc, mock_tts, _, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", side_effect=["", "bye"]):
            vc.start()

        assert mock_tts.speak.call_count >= 2

    def test_response_is_spoken(self) -> None:
        vc, mock_tts, _, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", side_effect=["Turn on the light", "bye"]):
            vc.start()

        # greeting + command response + farewell = at least 3 speak calls
        assert mock_tts.speak.call_count >= 3

    def test_keyboard_fallback_when_stt_unavailable(self) -> None:
        vc, mock_tts, mock_stt, _ = self._make_voice_chat()
        mock_stt.available = False

        with patch("builtins.input", side_effect=["What time is it?", "bye"]):
            vc.start()

        assert mock_tts.speak.call_count >= 2

    def test_ctrl_c_exits_gracefully(self) -> None:
        vc, mock_tts, _, _ = self._make_voice_chat()

        with patch.object(vc, "_listen", side_effect=KeyboardInterrupt):
            vc.start()  # Must not raise

        farewell_calls = [c for c in mock_tts.speak.call_args_list if "Goodbye" in str(c)]
        assert farewell_calls


# ---------------------------------------------------------------------------
# main.py integration: --voice and --text flags
# ---------------------------------------------------------------------------

class TestMainVoiceFlag:
    """Ensure main.py correctly routes --voice to VoiceChat and --text to CLIChat."""

    def test_voice_flag_starts_voice_chat(self) -> None:
        import main as main_module
        with patch("sys.argv", ["main.py", "--voice"]), \
             patch("src.interfaces.voice_chat.VoiceChat") as mock_vc_class:
            mock_vc = MagicMock()
            mock_vc_class.return_value = mock_vc
            main_module.main()
            mock_vc.start.assert_called_once()

    def test_text_flag_starts_cli_chat(self) -> None:
        import main as main_module
        with patch("sys.argv", ["main.py", "--text"]), \
             patch("src.interfaces.cli_chat.CLIChat") as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli_class.return_value = mock_cli
            main_module.main()
            mock_cli.start.assert_called_once()
