"""CLI chat interface for Jarvis AI."""
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    _RICH_AVAILABLE = True
except ImportError:
    _RICH_AVAILABLE = False

from src.core.jarvis_llm import JarvisLLM
from src.core.function_caller import FunctionCaller
from src.hardware.esp32_controller import ESP32Controller
from src.hardware.sensor_reader import SensorReader
from src.intelligence.wake_up_detector import WakeUpDetector
from src.intelligence.presence_detector import PresenceDetector
from src.intelligence.memory_manager import MemoryManager
from src.utils.logger import get_logger

logger = get_logger(__name__)

_BANNER = """
 ╔══════════════════════════════════════════╗
 ║       🤖 Jarvis AI - Smart Room          ║
 ║          Phase 1 MVP  v1.0.0             ║
 ╚══════════════════════════════════════════╝
"""

_HELP_TEXT = """
Available commands:
  /help          Show this help message
  /status        Show room conditions and system status
  /history       Show recent conversation history
  /clear         Clear conversation history
  /arrive        Simulate user arrival
  /leave         Simulate user departure
  /quit  /exit   Exit Jarvis

Type any message to chat with Jarvis naturally.
"""


class CLIChat:
    """Interactive CLI interface for chatting with Jarvis."""

    def __init__(
        self,
        config=None,
        memory: MemoryManager = None,
        wake_detector: WakeUpDetector = None,
        presence_detector: PresenceDetector = None,
    ):
        self.config = config
        self.memory = memory or MemoryManager(config)
        self.esp32 = ESP32Controller(mock=True)
        self.sensor = SensorReader(mock=True)
        self.function_caller = FunctionCaller(esp32=self.esp32, sensor=self.sensor)
        self.llm = JarvisLLM(config=config, function_caller=self.function_caller)
        self.wake_detector = wake_detector
        self.presence_detector = presence_detector

        if _RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None

    def _print(self, text: str):
        if self.console:
            self.console.print(text)
        else:
            print(text)

    def _print_banner(self):
        self._print(_BANNER)
        user = self.config.user_name if self.config else "Gaurav"
        now = datetime.now().strftime("%A, %B %d %Y %H:%M")
        self._print(f"  Welcome, {user}! Today is {now}\n")
        self._print("  Type /help for available commands.\n")

    def _handle_command(self, cmd: str) -> bool:
        """Handle slash commands. Returns True if command was handled."""
        cmd = cmd.strip().lower()

        if cmd in ("/quit", "/exit"):
            self._print("\n👋 Goodbye, Sir! Jarvis is shutting down.\n")
            return False  # Signal to exit loop

        if cmd == "/help":
            self._print(_HELP_TEXT)
            return True

        if cmd == "/clear":
            self.llm.clear_history()
            self._print("  Conversation history cleared.\n")
            return True

        if cmd == "/status":
            self._show_status()
            return True

        if cmd == "/history":
            self._show_history()
            return True

        if cmd == "/arrive":
            if self.presence_detector:
                self.presence_detector.force_arrival()
            self._print("  ✅ Simulated arrival - Welcome home, Sir!\n")
            return True

        if cmd == "/leave":
            if self.presence_detector:
                self.presence_detector.force_departure()
            self._print("  🚪 Simulated departure - Goodbye, Sir!\n")
            return True

        self._print(f"  Unknown command: {cmd}. Type /help for help.\n")
        return True

    def _show_status(self):
        data = self.sensor.read_dht_sensor()
        now = datetime.now()
        presence = self.presence_detector.state if self.presence_detector else "HOME"
        lines = [
            f"  Day:         {now.strftime('%A')}",
            f"  Time:        {now.strftime('%H:%M')}",
            f"  Temperature: {data['temperature']}°C",
            f"  Humidity:    {data['humidity']}%",
            f"  Presence:    {presence}",
            f"  Light:       {'ON' if self.esp32.light_state else 'OFF'}",
            f"  Fan:         {self.esp32.fan_speed}%",
        ]
        self._print("\n" + "\n".join(lines) + "\n")

    def _show_history(self):
        history = self.llm.history[-10:]
        if not history:
            self._print("  No conversation history yet.\n")
            return
        for msg in history:
            role = "You" if msg["role"] == "user" else "Jarvis"
            self._print(f"  [{role}] {msg['content']}\n")

    def run(self):
        """Start the interactive CLI chat loop."""
        self._print_banner()

        if self.wake_detector:
            self.wake_detector.start()
        if self.presence_detector:
            self.presence_detector.start()

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                self._print("\n\n👋 Goodbye, Sir!\n")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                should_continue = self._handle_command(user_input)
                if not should_continue:
                    break
                continue

            response = self.llm.chat(user_input)
            self._print(f"\nJarvis: {response}\n")

            if self.memory:
                self.memory.log_conversation("user", user_input)
                self.memory.log_conversation("assistant", response)
