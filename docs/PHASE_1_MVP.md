# Phase 1 MVP

## Goal
Deliver a working CLI-based smart room assistant that controls light and fan,
understands natural language, and automates morning/arrival routines – all
running **fully offline** on a Raspberry Pi or laptop.

## Features

### ✅ Natural Language Control
- Intent classification with regex patterns
- Intents: CONTROL, QUERY, GREETING, CONTEXT, EXPLAIN, COMFORT
- Ollama LLM integration (optional, graceful fallback)

### ✅ Appliance Control
- Light: turn_on, turn_off, fade_in
- Fan: set_speed 0–100%
- State tracking in memory

### ✅ Wake-Up Automation
- Weekday: 05:40 AM → fade-in light, greeting, fan 50%
- Weekend: 07:00 AM → same routine with weekend greeting

### ✅ Presence Detection
- Arrival → lights on, fan 50%, "Welcome home, Sir!"
- 2-hour absence → all off

### ✅ Local Storage
- JSONL event log
- Conversation history
- User profile JSON

### ✅ CLI Interface
- Rich-formatted terminal UI
- Commands: /status, /history, /clear, /quit, /help

## Out of Scope (Phase 2+)
- Real ESP32 hardware
- Climate control / AC
- ML-based behaviour prediction
- Voice recognition
