# Quick Start Guide

Get Jarvis running in under 5 minutes.

## Prerequisites

- Python 3.9+
- pip

## Step 1 — Clone & Install

```bash
git clone https://github.com/gaurav446446-hue/jarvis.git
cd jarvis
pip install -r requirements.txt
```

## Step 2 — Run Jarvis

```bash
python main.py
```

## Step 3 — Chat

```
You: Hello Jarvis
Jarvis: Hello, Sir! How can I assist you today?

You: Turn on the light
Jarvis: ✓ Light is now ON

You: What's the temperature?
Jarvis: ✓ temperature: 24.1, humidity: 63.0, time: 08:15, day: Monday

You: Set fan to 60%
Jarvis: ✓ Fan speed set to 60%

You: /status
  Day:         Monday
  Time:        08:15
  Temperature: 24.1°C
  Humidity:    63.0%
  Presence:    HOME
  Light:       ON
  Fan:         60%
```

## Slash Commands

| Command | Action |
|---------|--------|
| `/help` | Show help |
| `/status` | Room conditions |
| `/history` | Recent chat |
| `/clear` | Clear history |
| `/arrive` | Simulate arrival |
| `/leave` | Simulate departure |
| `/quit` | Exit |

## Optional: Enable Ollama LLM

```bash
# Install Ollama from https://ollama.ai
ollama pull mistral
```

Jarvis works without Ollama using a built-in rule engine. With Ollama, responses become much richer and more natural.
