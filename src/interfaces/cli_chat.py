"""Interactive CLI chat interface for Jarvis AI."""
from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

from src.core.jarvis_llm import JarvisLLM
from src.hardware.sensor_reader import SensorReader
from src.intelligence.appliance_controller import ApplianceController
from src.intelligence.memory_manager import MemoryManager
from src.interfaces.voice_processor import VoiceProcessor
from src.utils.config import get_config
from src.utils.logger import get_logger, setup_logger

logger = get_logger("cli_chat")

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False


class CLIChat:
    """Rich-formatted interactive CLI for Jarvis.

    Commands:
        /quit   – exit the session
        /status – show room conditions
        /history – print conversation history
        /clear  – clear conversation history
        /help   – show available commands
    """

    def __init__(
        self,
        jarvis: Optional[JarvisLLM] = None,
        memory: Optional[MemoryManager] = None,
    ) -> None:
        cfg = get_config()
        self._cfg = cfg
        self._memory = memory or MemoryManager()

        appliance = ApplianceController()
        sensor = SensorReader()
        voice = VoiceProcessor(use_tts=False)

        self._jarvis = jarvis or JarvisLLM(
            appliance_controller=appliance,
            sensor_reader=sensor,
            voice_processor=voice,
            model=cfg.llm.model,
        )

        if _RICH_AVAILABLE:
            self._console = Console()
        else:
            self._console = None

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the interactive CLI session (blocking loop)."""
        self._print_welcome()
        while True:
            try:
                user_input = self._prompt()
            except (KeyboardInterrupt, EOFError):
                self._print("\n[dim]Session ended. Goodbye, Sir![/dim]" if _RICH_AVAILABLE else "\nGoodbye, Sir!")
                break

            if not user_input.strip():
                continue

            if user_input.startswith("/"):
                should_exit = self._handle_command(user_input)
                if should_exit:
                    break
                continue

            response = self._jarvis.chat(user_input)
            self._memory.save_conversation_turn("user", user_input)
            self._memory.save_conversation_turn("assistant", response)
            self._print_response(response)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def _handle_command(self, cmd: str) -> bool:
        """Handle /commands.  Returns True if the session should exit."""
        cmd = cmd.strip().lower()
        if cmd in ("/quit", "/exit", "/q"):
            self._print("Goodbye, Sir! Have a great day." if not _RICH_AVAILABLE
                        else "[bold green]Goodbye, Sir! Have a great day.[/bold green]")
            return True
        if cmd == "/status":
            self._show_status()
        elif cmd == "/history":
            self._show_history()
        elif cmd in ("/clear", "/reset"):
            self._jarvis.reset_history()
            self._memory.clear_history()
            self._print("Conversation history cleared.")
        elif cmd == "/help":
            self._show_help()
        else:
            self._print(f"Unknown command: {cmd}. Type /help for a list of commands.")
        return False

    def _show_status(self) -> None:
        from src.core.function_caller import FunctionCaller
        from src.hardware.sensor_reader import SensorReader
        sensor = SensorReader()
        conditions = sensor.get_conditions()
        now = datetime.now()
        lines = [
            f"Time: {now.strftime('%H:%M:%S')}",
            f"Date: {now.strftime('%A, %Y-%m-%d')}",
            f"Temperature: {conditions['temperature']}°C",
            f"Humidity: {conditions['humidity']}%",
        ]
        if _RICH_AVAILABLE and self._console:
            self._console.print(Panel("\n".join(lines), title="Room Status", border_style="cyan"))
        else:
            print("\n--- Room Status ---")
            for line in lines:
                print(f"  {line}")
            print("-------------------")

    def _show_history(self) -> None:
        turns = self._memory.get_conversation_history(limit=10)
        if not turns:
            self._print("No conversation history.")
            return
        if _RICH_AVAILABLE and self._console:
            self._console.print("\n[bold]Recent conversation:[/bold]")
            for turn in turns:
                role = turn.get("role", "?")
                content = turn.get("content", "")
                colour = "cyan" if role == "user" else "green"
                self._console.print(f"[{colour}]{role.capitalize()}:[/{colour}] {content}")
        else:
            print("\n--- Recent conversation ---")
            for turn in turns:
                role = turn.get("role", "?")
                print(f"{role.capitalize()}: {turn.get('content', '')}")
            print("---------------------------")

    def _show_help(self) -> None:
        commands = [
            ("/quit      ", "Exit the session"),
            ("/status    ", "Show room conditions"),
            ("/history   ", "Show recent conversation"),
            ("/clear     ", "Clear conversation history"),
            ("/help      ", "Show this help message"),
        ]
        if _RICH_AVAILABLE and self._console:
            lines = "\n".join(f"  [cyan]{c}[/cyan] {d}" for c, d in commands)
            self._console.print(Panel(lines, title="Commands", border_style="yellow"))
        else:
            print("\n--- Commands ---")
            for c, d in commands:
                print(f"  {c} {d}")
            print("----------------")

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _print_welcome(self) -> None:
        name = self._cfg.user.name
        if _RICH_AVAILABLE and self._console:
            self._console.print(
                Panel(
                    f"[bold green]Welcome, {name}![/bold green]\n"
                    "[dim]Jarvis AI Smart Room Assistant — Phase 1 MVP[/dim]\n"
                    "Type your message or [cyan]/help[/cyan] for commands.",
                    title="🤖 Jarvis",
                    border_style="green",
                )
            )
        else:
            print("=" * 50)
            print(f"  Welcome, {name}! Jarvis AI Smart Room Assistant")
            print("  Type /help for commands or /quit to exit.")
            print("=" * 50)

    def _prompt(self) -> str:
        if _RICH_AVAILABLE and self._console:
            return self._console.input("[bold cyan]You:[/bold cyan] ")
        return input("You: ")

    def _print_response(self, response: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(f"[bold green]Jarvis:[/bold green] {response}")
        else:
            print(f"Jarvis: {response}")

    def _print(self, message: str) -> None:
        if _RICH_AVAILABLE and self._console:
            self._console.print(message)
        else:
            print(message)
