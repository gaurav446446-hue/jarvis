# Architecture

## System Overview

```
User Input (CLI)
      │
      ▼
  CLIChat ──────────────────────────────────┐
      │                                     │
      ▼                                     │
  JarvisLLM                          PresenceDetector
  ├── IntentClassifier                WakeUpDetector
  ├── PromptBuilder
  ├── Ollama API call (or fallback)
  └── FunctionCaller
          ├── ESP32Controller (mock)
          └── SensorReader (mock)
```

## Component Breakdown

### `src/core/`

| File | Role |
|------|------|
| `jarvis_llm.py` | Orchestrates intent → prompt → LLM → tool execution → response |
| `intent_classifier.py` | Regex-based classification (CONTROL/QUERY/GREETING/CONTEXT/EXPLAIN) |
| `prompt_builder.py` | Constructs system + history + user messages for Ollama |
| `function_caller.py` | Parses `CALL: tool(args)` from LLM output, executes tools |

### `src/intelligence/`

| File | Role |
|------|------|
| `wake_up_detector.py` | Monitors time/motion, triggers morning automation |
| `presence_detector.py` | Tracks HOME/AWAY state via motion events |
| `appliance_controller.py` | High-level light/fan control with logging |
| `memory_manager.py` | JSON persistence: profile, events, conversations |

### `src/hardware/`

| File | Role |
|------|------|
| `tool_definitions.py` | Declares available tools and parameters |
| `sensor_reader.py` | Mock temperature/humidity/motion sensor |
| `esp32_controller.py` | Stub serial/MQTT commands to ESP32 |

### `src/interfaces/`

| File | Role |
|------|------|
| `cli_chat.py` | Interactive terminal chat loop |
| `voice_processor.py` | TTS/STT stub (Phase 2) |

## Data Flow

```
1. User types "set fan to 70%"
2. IntentClassifier → CONTROL
3. PromptBuilder builds messages with system context + history
4. JarvisLLM calls Ollama (or fallback)
5. LLM returns "Setting fan to 70%, Sir. CALL: set_fan_speed(speed=70)"
6. FunctionCaller.execute_all() extracts and runs set_fan_speed(70)
7. ESP32Controller.set_fan_speed(70) → logged
8. Response cleaned and returned to user
9. Memory logs conversation turn
```

## Storage Schema

### `models/user_profile.json`
```json
{
  "user": "Gaurav",
  "wake_times": { "weekday": "05:40", "weekend": "07:00" },
  "preferences": { "preferred_fan_speed": 50, "comfort_temp_min": 23 },
  "presence_state": "HOME"
}
```

### `data/events_log.jsonl`
Each line:
```json
{"timestamp": "2024-01-01T05:40:00", "event": "wake_up", "data": {"fan_speed": 50}}
```

### `data/conversation_history.jsonl`
Each line:
```json
{"timestamp": "2024-01-01T08:00:00", "role": "user", "content": "turn on the light"}
```
