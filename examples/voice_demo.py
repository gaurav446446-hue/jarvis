"""Demo script: showcase Jarvis voice capabilities.

Run with::

    python examples/voice_demo.py

This script demonstrates TTS and STT independently before launching a short
voice conversation.  When audio hardware is unavailable each section falls
back gracefully so the script always runs to completion.
"""
from __future__ import annotations

import sys
import os

# Ensure the repository root is on the path when run directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.interfaces.tts_engine import TTSEngine
from src.interfaces.stt_engine import STTEngine


def demo_tts() -> None:
    print("\n--- Text-to-Speech Demo ---")
    tts = TTSEngine(rate=150, volume=0.9, voice="male")

    if tts.available:
        print("TTS engine ready.  Speaking now…")
    else:
        print("TTS engine not available – output will be printed to console.")

    tts.speak("Hello Sir!  I am Jarvis, your smart room assistant.")
    tts.speak("I can control your lights, manage your fan speed, and answer your questions.")

    # Try female voice
    tts.set_voice("female")
    tts.speak("Switching to female voice.  How does this sound?")

    # Restore male voice
    tts.set_voice("male")
    tts.speak("Back to male voice.  Text-to-speech demo complete.")
    print("TTS demo finished.\n")


def demo_stt() -> None:
    print("\n--- Speech-to-Text Demo ---")
    stt = STTEngine(energy_threshold=4000)

    if not stt.available:
        print("STT engine not available (microphone or speech_recognition missing).")
        print("Skipping STT demo.\n")
        return

    print("Microphone ready.  Please speak after the prompt…")
    input("Press Enter when you are ready to speak (you have 10 seconds): ")
    print("[LISTENING] Speak now…")
    text = stt.listen(timeout=10)

    if text:
        print(f"[RECOGNISED] You said: {text}")
    else:
        print("[RESULT] Nothing was captured (timed out or unclear).")
    print("STT demo finished.\n")


def demo_voice_chat() -> None:
    print("\n--- Short Voice Chat Demo ---")
    print("Type 'skip' to skip this section.")
    choice = input("Start voice chat demo? (yes/skip): ").strip().lower()
    if choice in ("skip", "s", "n", "no"):
        print("Skipping voice chat demo.")
        return

    from src.interfaces.voice_chat import VoiceChat
    print("Starting voice chat.  Say 'goodbye' to end.\n")
    VoiceChat().start()


if __name__ == "__main__":
    print("=" * 55)
    print("  Jarvis AI – Voice Capabilities Demo")
    print("=" * 55)

    demo_tts()
    demo_stt()
    demo_voice_chat()

    print("\nDemo complete.  Run 'python main.py --voice' for the full experience!")
