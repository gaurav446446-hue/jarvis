# Jarvis AI — Smart Room Assistant

> Phase 1 MVP: AI-powered smart room assistant with wake-up automation, natural language control, and presence detection.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Features

- 🌅 **Wake-Up Automation** — 5:40 AM (weekdays) / 7:00 AM (weekends)
- 💬 **Conversational AI** — Ollama (Mistral) with fallback rule engine
- 🏠 **Presence Detection** — motion-based arrival/departure
- 💡 **Light & Fan Control** — via function calling
- 📊 **Room Monitoring** — temperature & humidity
- 🧠 **Intent Classification** — CONTROL / QUERY / GREETING / CONTEXT / EXPLAIN
- 💾 **Memory System** — JSON persistence

## Docs

- [Quick Start](docs/QUICK_START.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP_GUIDE.md)
- [API Reference](docs/API_REFERENCE.md)
- [Phase 1 MVP](docs/PHASE_1_MVP.md)

## Tests

```bash
pytest tests/ -v        # 65 tests
```

## Roadmap

| Phase | Focus |
|-------|-------|
| **Phase 1** ✅ | MVP — CLI, automation, function calling |
| **Phase 2** 🔄 | Climate prediction (LSTM) |
| **Phase 3** 📊 | Continuous ML learning |
