"""Voice chat interface for Jarvis AI.

Replaces the CLI chat with a full voice conversation:
  - Microphone input  → STTEngine → JarvisLLM
  - JarvisLLM output  → TTSEngine → laptop speakers

Falls back to keyboard input when a microphone is not available.
"""
from __future__ import annotations

from typing import Optional

from src.core.jarvis_llm import JarvisLLM
from src.hardware.sensor_reader import SensorReader
from src.intelligence.appliance_controller import ApplianceController
from src.intelligence.memory_manager import MemoryManager
from src.interfaces.tts_engine import TTSEngine
from src.interfaces.stt_engine import STTEngine
from src.interfaces.voice_processor import VoiceProcessor
from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger("voice_chat")

try:
    from rich.console import Console
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

# Words that trigger a graceful exit
_EXIT_WORDS = frozenset({"bye", "goodbye", "exit", "quit", "stop", "see you"})


class VoiceChat:
    """Voice-driven conversational interface for Jarvis.

    The user speaks into the laptop microphone and Jarvis responds through
    the laptop speakers.  When the microphone is unavailable the interface
    falls back to keyboard input, so it is always usable.

    Visual feedback is displayed for each stage of the interaction::

        [Listening...]    – waiting for microphone input
        [Processing...]   – sending input to the LLM
        [Speaking...]     – TTS output in progress

    Args:
        jarvis: Optional pre-built :class:`~src.core.jarvis_llm.JarvisLLM`
            instance (mainly useful for testing).
        memory: Optional pre-built :class:`~src.intelligence.memory_manager.MemoryManager`
            instance (mainly useful for testing).
    """

    def __init__(
        self,
        jarvis: Optional[JarvisLLM] = None,
        memory: Optional[MemoryManager] = None,
    ) -> None:
        cfg = get_config()
        self._cfg = cfg
        self._memory = memory or MemoryManager()

        # Read voice config (falls back to defaults when absent)
        voice_cfg = cfg.get("voice") or {}
        speaker_cfg = voice_cfg.get("speaker") or {}
        mic_cfg = voice_cfg.get("microphone") or {}

        self._tts = TTSEngine(
            rate=speaker_cfg.get("rate", 150),
            volume=speaker_cfg.get("volume", 0.9),
            voice=speaker_cfg.get("voice", "male"),
        )
        self._stt = STTEngine(
            energy_threshold=mic_cfg.get("energy_threshold", 4000),
            microphone_index=mic_cfg.get("index"),
        )
        self._listen_timeout: int = mic_cfg.get("timeout", 10)

        voice_proc = VoiceProcessor(use_tts=False)
        appliance = ApplianceController()
        sensor = SensorReader()

        self._jarvis = jarvis or JarvisLLM(
            appliance_controller=appliance,
            sensor_reader=sensor,
            voice_processor=voice_proc,
            model=cfg.llm.model,
        )

        if _RICH_AVAILABLE:
            self._console = Console()
        else:
            self._console = None  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the voice conversation loop (blocking).

        Greets the user, then cycles between listening for input and
        speaking the response until an exit word is detected or the user
        interrupts with Ctrl+C.
        """
        self._print_welcome()

        greeting = f"Hello {self._cfg.user.name}! I'm Jarvis. How can I help you?"
        self._tts.speak(greeting)
        self._print_jarvis(greeting)

        while True:
            try:
                user_input = self._listen()
            except (KeyboardInterrupt, EOFError):
                farewell = f"Goodbye, {self._cfg.user.name}!"
                self._tts.speak(farewell)
                self._print(
                    "[dim]Session ended.[/dim]" if _RICH_AVAILABLE else "Session ended."
                )
                break

            if not user_input.strip():
                # Timed out with no speech detected – wait for next attempt
                continue

            self._print_user(user_input)

            # Exit on farewell keywords
            lower = user_input.lower()
            if any(word in lower for word in _EXIT_WORDS):
                farewell = f"Goodbye, {self._cfg.user.name}! Have a great day!"
                self._print_status("Speaking...")
                self._tts.speak(farewell)
                self._print_jarvis(farewell)
                break

            # Process command
            self._print_status("Processing...")
            response = self._jarvis.chat(user_input)
            self._memory.save_conversation_turn("user", user_input)
            self._memory.save_conversation_turn("assistant", response)

            # Speak response
            self._print_status("Speaking...")
            self._print_jarvis(response)
            self._tts.speak(response)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _listen(self) -> str:
        """Capture a voice utterance or fall back to keyboard input.

        Returns:
            Transcribed text from the microphone, or text typed by the user.
        """
        if self._stt.available:
            self._print_status("Listening...")
            return self._stt.listen(timeout=self._listen_timeout)

        # Keyboard fallback
        if _RICH_AVAILABLE and self._console:
            return self._console.input("[bold cyan]You (type):[/bold cyan] ")
        return input("You (type): ")

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _print_welcome(self) -> None:
        name = self._cfg.user.name
        tts_status = (
            "✅ TTS ready (laptop speakers)"
            if self._tts.available
            else "⚠️  TTS unavailable – using console output"
        )
        stt_status = (
            "✅ Microphone ready"
            if self._stt.available
            else "⚠️  Microphone unavailable – using keyboard input"
        )

        if _RICH_AVAILABLE and self._console:
            from rich.panel import Panel

            self._console.print(
                Panel(
                    f"[bold green]Welcome, {name}![/bold green]\n"
                    "[dim]Jarvis AI – Voice Chat Mode[/dim]\n"
                    f"{tts_status}\n"
                    f"{stt_status}\n"
                    "Say [cyan]'goodbye'[/cyan] or [cyan]'exit'[/cyan] to end.",
                    title="🎙️ Jarvis Voice",
                    border_style="green",
                )
            )
        else:
            print("=" * 55)
            print(f"  Welcome, {name}! Jarvis AI – Voice Chat Mode")
            print(f"  {tts_status}")
            print(f"  {stt_status}")
            print("  Say 'goodbye' or 'exit' to end.")
            print("=" * 55)

    def _print_status(self, status: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(f"[dim][{status}][/dim]")
        else:
            print(f"[{status}]")

    def _print_user(self, text: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(f"[bold cyan][YOU][/bold cyan] {text}")
        else:
            print(f"[YOU] {text}")

    def _print_jarvis(self, text: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(f"[bold green][RESPONSE][/bold green] Jarvis: {text}")
        else:
            print(f"[RESPONSE] Jarvis: {text}")

    def _print(self, message: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(message)
        else:
            print(message)
