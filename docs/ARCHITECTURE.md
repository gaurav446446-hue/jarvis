# Architecture

## Overview

```
main.py
  └── CLIChat (src/interfaces/cli_chat.py)
        └── JarvisLLM (src/core/jarvis_llm.py)
              ├── IntentClassifier (src/core/intent_classifier.py)
              ├── FunctionCaller (src/core/function_caller.py)
              │     ├── ApplianceController (src/intelligence/appliance_controller.py)
              │     └── SensorReader (src/hardware/sensor_reader.py)
              └── PromptBuilder (src/core/prompt_builder.py)
```

## Layers

### Interfaces (`src/interfaces/`)
Entry points for user interaction: CLI chat and voice processor.

### Core (`src/core/`)
LLM orchestration, intent classification, function calling, and prompt construction.

### Intelligence (`src/intelligence/`)
Higher-level automations: wake-up detection, presence detection, appliance control, and memory.

### Hardware (`src/hardware/`)
Hardware abstraction: sensor reading, ESP32 control stubs, and tool definitions.

### Utils (`src/utils/`)
Cross-cutting concerns: logging, configuration, and constants.

## Data Flow

```
User Input → IntentClassifier → JarvisLLM → FunctionCaller → ApplianceController
                                          ↘ LLM (Ollama) → Response
```

## Storage

All data is stored locally as JSON / JSONL files under `data/`:
- `events_log.jsonl` – structured event log
- `conversation_history.jsonl` – chat history
