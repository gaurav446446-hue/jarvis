# Automation Examples

## Wake-Up Automation

**Weekday (5:40 AM, Monday–Friday):**
```
Trigger: Time = 05:40 OR motion detected within 15min window
Actions:
  1. fade_in_light(duration=2s)
  2. say("Good morning, Sir! Time to rise and shine!")
  3. set_fan_speed(50)
  4. display room conditions
```

**Weekend (7:00 AM, Saturday–Sunday):**
```
Trigger: Time = 07:00 OR motion detected within 15min window
Actions:
  1. fade_in_light(duration=2s)
  2. say("Good morning, Sir! Happy weekend!")
  3. set_fan_speed(50)
  4. display room conditions
```

## Presence Detection

**Arrival (AWAY → HOME):**
```
Trigger: Motion detected after 2+ hours absence
Actions:
  1. turn_on_light()
  2. set_fan_speed(50)
  3. say("Welcome home, Sir!")
  4. log_event(arrival)
```

**Departure (HOME → AWAY):**
```
Trigger: No motion for 2+ hours
Actions:
  1. turn_off_light()
  2. set_fan_speed(0)
  3. log_event(departure)
```

## Comfort Mode

```
Trigger: Temperature > 25°C
Actions:
  1. increase fan_speed by 20%
  2. log_event(comfort_adjustment)

Trigger: Temperature < 23°C
Actions:
  1. decrease fan_speed by 20%
  2. log_event(comfort_adjustment)
```
