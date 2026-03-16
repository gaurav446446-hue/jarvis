# API Reference

## Core Classes

### `JarvisLLM`
```python
from src.core.jarvis_llm import JarvisLLM

llm = JarvisLLM(appliance_controller, sensor_reader)
response = llm.chat("Turn on the light")
llm.reset_history()
```

### `IntentClassifier`
```python
from src.core.intent_classifier import IntentClassifier

clf = IntentClassifier()
intent, params = clf.classify("Turn on the light")
# → (Intent.CONTROL, {"device": "light", "action": "turn_on"})
```

### `FunctionCaller`
```python
from src.core.function_caller import FunctionCaller

fc = FunctionCaller(appliance_controller=ctrl, sensor_reader=sensor)
result = fc.execute("set_fan_speed", speed=75)
result = fc.execute_from_text("set_fan_speed(speed=50)")
```

### `ApplianceController`
```python
from src.intelligence.appliance_controller import ApplianceController

ctrl = ApplianceController()
ctrl.turn_on_light()
ctrl.turn_off_light()
ctrl.set_fan_speed(50)   # 0–100
ctrl.fade_in(duration=2)
state = ctrl.get_state()
```

### `MemoryManager`
```python
from src.intelligence.memory_manager import MemoryManager

mem = MemoryManager()
mem.log_event("light.on", {"brightness": 80})
mem.save_conversation_turn("user", "Turn on the light")
history = mem.get_conversation_history(limit=20)
```

### `WakeUpDetector`
```python
from src.intelligence.wake_up_detector import WakeUpDetector

det = WakeUpDetector(appliance_controller=ctrl)
det.is_wake_up_time()           # bool
det.wake_up_sequence()          # runs morning routine, returns greeting
```

### `PresenceDetector`
```python
from src.intelligence.presence_detector import PresenceDetector

det = PresenceDetector(appliance_controller=ctrl)
det.detect_motion(motion_detected=True)   # triggers arrival if was AWAY
det.mark_arrived()
det.mark_departed()
det.is_extended_absence()                 # bool
```

## Available Tools

| Tool | Parameters | Description |
|------|-----------|-------------|
| `turn_on_light` | – | Turn on room light |
| `turn_off_light` | – | Turn off room light |
| `set_fan_speed` | `speed: int` | Set fan speed 0–100% |
| `get_room_conditions` | – | Temperature, humidity, motion |
| `get_time` | – | Current time |
| `get_day` | – | Current day / date |
| `predict_comfort` | – | Comfort analysis + suggestion |
| `say` | `message: str` | Speak or print message |
