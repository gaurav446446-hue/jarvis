# Jarvis AI Smart Room Assistant

Jarvis is a local, offline-first AI smart room assistant built with Python.
It controls lights, fans, and room appliances through natural language while learning your habits.

## Features (Phase 1 MVP)
- 🗣️ Natural language control via CLI
- 💡 Light control (on/off/fade-in)
- 🌀 Fan speed control (0–100%)
- 🧠 Intent classification (no internet required)
- 📋 Event and conversation logging
- ⏰ Wake-up routine automation
- 🏠 Presence detection automations

## Quick Start
```bash
pip install -r requirements.txt
python main.py
```

## Project Structure
```
src/        – Core source code
tests/      – Pytest test suite
models/     – User profile and behaviour patterns
data/       – Logs and conversation history
docs/       – Documentation
examples/   – Example conversations and automations
```

## Documentation
- [Quick Start](QUICK_START.md)
- [Architecture](ARCHITECTURE.md)
- [Setup Guide](SETUP_GUIDE.md)
- [API Reference](API_REFERENCE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
