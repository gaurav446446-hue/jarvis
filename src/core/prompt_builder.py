"""Prompt builder - constructs LLM prompts for Jarvis."""
from datetime import datetime

from src.hardware.tool_definitions import get_tool_descriptions
from src.utils.constants import (
    INTENT_CONTROL,
    INTENT_QUERY,
    INTENT_GREETING,
    INTENT_CONTEXT,
    INTENT_EXPLAIN,
)

_SYSTEM_PROMPT = """You are Jarvis, an AI-powered smart room assistant for {user_name}.
You control room appliances (lights, fan) and answer questions about the room.

Current date/time: {datetime}
User presence: {presence_state}

Available tools (call them by name in your response when needed):
{tool_descriptions}

When you need to call a tool, include it in your response like:
  CALL: tool_name(param=value)

For tools without parameters:
  CALL: turn_on_light()

Rules:
- Always be polite and address the user as "Sir".
- Keep responses concise and helpful.
- Call tools when the user asks you to control something or get information.
- After calling tools, describe what you did.
- Remember context from the conversation history.
"""

_INTENT_HINTS = {
    INTENT_CONTROL: "The user wants to control a device. Call the appropriate tool.",
    INTENT_QUERY: "The user is asking a question. Call the relevant query tool and answer.",
    INTENT_GREETING: "The user is greeting you. Respond warmly.",
    INTENT_CONTEXT: "The user is sharing their context/status. Respond appropriately and call relevant tools.",
    INTENT_EXPLAIN: "The user wants an explanation. Provide a clear and helpful answer.",
}


class PromptBuilder:
    """Build structured prompts for the LLM."""

    def __init__(self, user_name: str = "Gaurav"):
        self.user_name = user_name

    def build_system_prompt(self, presence_state: str = "HOME") -> str:
        """Build the system prompt with current context."""
        now = datetime.now().strftime("%A, %B %d %Y %H:%M")
        return _SYSTEM_PROMPT.format(
            user_name=self.user_name,
            datetime=now,
            presence_state=presence_state,
            tool_descriptions=get_tool_descriptions(),
        )

    def build_user_message(self, user_input: str, intent: str) -> str:
        """Enrich the user message with intent hint."""
        hint = _INTENT_HINTS.get(intent, "")
        if hint:
            return f"[Intent: {intent}] {user_input}"
        return user_input

    def build_messages(
        self,
        user_input: str,
        intent: str,
        history: list[dict],
        presence_state: str = "HOME",
    ) -> list[dict]:
        """
        Build the full messages list for the chat completion API.

        Returns a list of role/content dicts ready for Ollama.
        """
        messages = [{"role": "system", "content": self.build_system_prompt(presence_state)}]
        messages.extend(history)
        messages.append({"role": "user", "content": self.build_user_message(user_input, intent)})
        return messages
