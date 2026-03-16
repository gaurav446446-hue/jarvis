# Phase 1 MVP

## Goals

- Working CLI chat with Jarvis
- Wake-up automation (5:40 AM weekday / 7:00 AM weekend)
- Motion-based presence detection
- Tool/function calling system
- Intent classification
- Memory & event logging
- Full test coverage

## Wake-Up Sequence

```
5:35 AM — Jarvis monitors motion + time

5:40 AM (Weekday):
  1. Light fades in (2 seconds)
  2. "Good morning, Sir! Time to rise and shine!"
  3. Fan → 50%
  4. Display: Monday, 5:40 AM, 24°C, 65% humidity

7:00 AM (Weekend):
  1. Light fades in (2 seconds)
  2. "Good morning, Sir! Happy weekend!"
  3. Fan → 50%
  4. Display: Saturday, 7:00 AM, 23°C, 60% humidity
```

## Intent Types

| Intent | Example | Action |
|--------|---------|--------|
| CONTROL | "Turn on light" | Execute tool |
| QUERY | "What's the temp?" | Query tool + answer |
| GREETING | "Good morning" | Respond warmly |
| CONTEXT | "I'm leaving" | Away mode |
| EXPLAIN | "Why did you..." | Explain reasoning |

## Available Tools

```python
turn_on_light()
turn_off_light()
set_fan_speed(speed=0..100)
get_room_conditions()
get_time()
get_day()
predict_comfort()
say(message="...")
```

## Success Criteria

- [x] Wake-up automation (5:40/7:00)
- [x] CLI chat functional
- [x] Intent classification working
- [x] Function calling executes commands
- [x] 65 tests passing
- [x] Documentation complete
- [x] Ready for Phase 2
