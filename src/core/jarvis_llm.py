"""Main LLM orchestrator for Jarvis AI."""
import json
from typing import Optional

import requests

from src.core.intent_classifier import IntentClassifier
from src.core.prompt_builder import PromptBuilder
from src.core.function_caller import FunctionCaller
from src.utils.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Maximum number of conversation turns kept in context
_MAX_HISTORY = 20


class JarvisLLM:
    """
    Main LLM orchestrator.

    Handles:
    - Intent classification
    - Prompt construction
    - Ollama API calls
    - Tool/function call extraction and execution
    - Conversation history management
    """

    def __init__(self, config: Config, function_caller: FunctionCaller = None):
        self.config = config
        self.intent_classifier = IntentClassifier()
        self.prompt_builder = PromptBuilder(user_name=config.user_name)
        self.function_caller = function_caller or FunctionCaller()
        self._history: list[dict] = []
        self._presence_state: str = "HOME"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def chat(self, user_input: str) -> str:
        """Process user input and return Jarvis's response."""
        intent, confidence = self.intent_classifier.classify_with_confidence(user_input)
        logger.debug("Intent: %s (%.2f)", intent, confidence)

        messages = self.prompt_builder.build_messages(
            user_input=user_input,
            intent=intent,
            history=self._history[-_MAX_HISTORY:],
            presence_state=self._presence_state,
        )

        raw_response = self._call_llm(messages)

        tool_results = self.function_caller.execute_all(raw_response)

        clean_response = self._strip_tool_calls(raw_response)

        if tool_results:
            clean_response = self._append_tool_results(clean_response, tool_results)

        self._history.append({"role": "user", "content": user_input})
        self._history.append({"role": "assistant", "content": clean_response})

        return clean_response

    def set_presence(self, state: str):
        """Update the known presence state (HOME / AWAY / SLEEPING)."""
        self._presence_state = state

    def clear_history(self):
        """Reset conversation history."""
        self._history = []

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_llm(self, messages: list[dict]) -> str:
        """Send messages to Ollama and return the assistant text."""
        url = f"{self.config.llm_host}/api/chat"
        payload = {
            "model": self.config.llm_model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": self.config.get("llm", "max_tokens", default=512)},
        }

        try:
            resp = requests.post(url, json=payload, timeout=self.config.get("llm", "timeout", default=30))
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not available - using fallback response")
            return self._fallback_response(messages[-1]["content"])
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            return self._fallback_response(messages[-1]["content"])

    def _fallback_response(self, user_input: str) -> str:
        """
        Simple rule-based fallback when Ollama is unavailable.

        Ensures Jarvis still works without a running LLM.
        """
        lower = user_input.lower()
        if "turn on" in lower and "light" in lower:
            return "Of course, Sir. CALL: turn_on_light()"
        if "turn off" in lower and "light" in lower:
            return "Turning off the light, Sir. CALL: turn_off_light()"
        if "fan" in lower and any(d.isdigit() for d in lower):
            import re
            match = re.search(r"(\d+)", lower)
            speed = match.group(1) if match else "50"
            return f"Setting fan to {speed}%, Sir. CALL: set_fan_speed(speed={speed})"
        if "temperature" in lower or "conditions" in lower or "room" in lower:
            return "Let me check the room for you, Sir. CALL: get_room_conditions()"
        if "time" in lower:
            return "CALL: get_time()"
        if "day" in lower:
            return "CALL: get_day()"
        if any(w in lower for w in ["hello", "hi", "hey", "morning", "evening", "night"]):
            return f"Hello, Sir! How can I assist you today?"
        return "I'm here to help, Sir. Could you please clarify what you need?"

    @staticmethod
    def _strip_tool_calls(response: str) -> str:
        """Remove CALL: lines from the visible response."""
        import re
        return re.sub(r"\s*CALL:\s*\w+\([^)]*\)", "", response).strip()

    @staticmethod
    def _append_tool_results(response: str, results: list[dict]) -> str:
        """Append a summary of tool execution results to the response."""
        summaries = []
        for r in results:
            tool = r.get("tool", "")
            if r.get("success"):
                msg = r.get("message") or r.get("spoken") or ""
                data = r.get("data") or {}
                if data:
                    parts = [f"{k}: {v}" for k, v in data.items()]
                    msg = ", ".join(parts)
                if msg:
                    summaries.append(f"✓ {msg}")
            else:
                summaries.append(f"✗ {tool}: {r.get('error', 'failed')}")
        if summaries:
            return response + "\n" + "\n".join(summaries)
        return response
