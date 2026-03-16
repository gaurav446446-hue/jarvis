# API Reference

## Available Tools

All tools are callable via natural language or `CALL:` syntax.

### `turn_on_light()`
Turn the tubelight ON.

**Example:** "Turn on the light"  
**Response:** `✓ Light is now ON`

---

### `turn_off_light()`
Turn the tubelight OFF.

**Example:** "Turn off the light"  
**Response:** `✓ Light is now OFF`

---

### `set_fan_speed(speed: int)`
Set fan speed between 0 and 100%.

**Parameters:**
- `speed` (int, 0–100): Fan speed percentage

**Example:** "Set fan to 70%"  
**Response:** `✓ Fan speed set to 70%`

---

### `get_room_conditions()`
Get current temperature, humidity, time, and day.

**Example:** "What are the room conditions?"  
**Response:** `✓ temperature: 24.2, humidity: 63.0, time: 08:30, day: Monday`

---

### `get_time()`
Get the current time.

**Example:** "What time is it?"  
**Response:** `✓ time: 08:30`

---

### `get_day()`
Get the current day of the week.

**Example:** "What day is it?"  
**Response:** `✓ day: Monday`

---

### `predict_comfort()`
Predict comfort level based on current temperature.

**Example:** "How comfortable is it?"  
**Response:** `✓ comfort: Comfortable, temperature: 24.1`

---

### `say(message: str)`
Speak a message via text-to-speech (mock in Phase 1).

**Parameters:**
- `message` (str): Text to speak

**Example:** `CALL: say(message="Good morning")`

---

## Intent Types

| Intent | Trigger Words | Action |
|--------|--------------|--------|
| `CONTROL` | turn, set, switch, enable, disable | Execute control tool |
| `QUERY` | what, how, temperature, status, check | Execute query tool |
| `GREETING` | hello, hi, morning, evening, night | Respond warmly |
| `CONTEXT` | I'm home, leaving, sleeping, arrived | Update state + automate |
| `EXPLAIN` | why, explain, how does, what happened | Provide explanation |
| `UNKNOWN` | (anything else) | Generic helpful response |
