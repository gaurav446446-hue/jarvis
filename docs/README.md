# Jarvis AI - Smart Room Assistant

> **Phase 1 MVP** — AI-powered smart room assistant that learns user behavior and automates room controls.

## Overview

Jarvis is a local AI assistant that runs entirely on your machine (no cloud required). It controls your room appliances (lights, fan) through natural language and learns your routines over time.

### Features (Phase 1)

| Feature | Description |
|---------|-------------|
| 🌅 Wake-Up Automation | 5:40 AM weekdays / 7:00 AM weekends |
| 💬 Conversational AI | Natural language via Ollama (Mistral) |
| 🏠 Presence Detection | Motion-based arrival/departure automation |
| 💡 Light Control | On/off with 2-second fade-in |
| 🌀 Fan Control | 0–100% speed via AC dimmer |
| 📊 Room Monitoring | Temperature & humidity readout |
| 🧠 Intent Classification | CONTROL / QUERY / GREETING / CONTEXT / EXPLAIN |
| 💾 Memory System | JSON-based persistent storage |

---

## Quick Start

```bash
git clone https://github.com/gaurav446446-hue/jarvis.git
cd jarvis
pip install -r requirements.txt
python main.py
```

### Example Chat

```
You: turn on the light
Jarvis: ✓ Light is now ON

You: set fan to 70%
Jarvis: ✓ Fan speed set to 70%

You: what's the temperature?
Jarvis: ✓ temperature: 24.2, humidity: 63.5, time: 08:30, day: Monday

You: I'm leaving
Jarvis: Goodbye, Sir! Turning everything off.
```

---

## Project Structure

```
jarvis/
├── src/
│   ├── core/              # LLM, intent classifier, function caller, prompt builder
│   ├── intelligence/      # Wake-up, presence, appliance controller, memory
│   ├── hardware/          # Tool definitions, sensor reader (mock), ESP32 stub
│   ├── interfaces/        # CLI chat, voice processor (stub)
│   └── utils/             # Config, logger, constants
├── tests/                 # pytest test suite (65 tests)
├── models/                # user_profile.json, behavior_patterns.json
├── data/                  # events_log.jsonl, conversation_history.jsonl
├── docs/                  # Documentation
├── examples/              # Usage examples
├── main.py                # Entry point
├── config.yaml            # Configuration
└── requirements.txt
```

---

## Configuration

Edit `config.yaml` to adjust settings:

```yaml
user_profile:
  wake_times:
    weekday: "05:40"   # Monday–Friday
    weekend: "07:00"   # Saturday–Sunday
  preferred_fan_speed: 50
  comfort_temp_min: 23
  comfort_temp_max: 25

llm:
  model: "mistral"            # or phi, llama2, etc.
  host: "http://localhost:11434"
```

---

## LLM Setup (Ollama)

```bash
# Install Ollama: https://ollama.ai
ollama pull mistral   # ~4 GB — recommended
# or
ollama pull phi       # ~2 GB — faster on low RAM
```

Jarvis works without Ollama too — it falls back to a built-in rule engine.

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term-missing
```

---

## Roadmap

| Phase | Focus | Timeline |
|-------|-------|----------|
| **Phase 1** ✅ | MVP — CLI, automation, function calling | Week 1 |
| **Phase 2** 🔄 | Climate prediction (LSTM), energy optimization | Week 2 |
| **Phase 3** 📊 | Continuous ML learning, anomaly detection | Week 3 |

---

## License

MIT License — see [LICENSE](../LICENSE)
