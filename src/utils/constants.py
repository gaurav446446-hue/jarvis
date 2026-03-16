"""Constants for Jarvis AI."""

# Intent types
INTENT_CONTROL = "CONTROL"
INTENT_QUERY = "QUERY"
INTENT_GREETING = "GREETING"
INTENT_CONTEXT = "CONTEXT"
INTENT_EXPLAIN = "EXPLAIN"
INTENT_UNKNOWN = "UNKNOWN"

VALID_INTENTS = {
    INTENT_CONTROL,
    INTENT_QUERY,
    INTENT_GREETING,
    INTENT_CONTEXT,
    INTENT_EXPLAIN,
    INTENT_UNKNOWN,
}

# Presence states
STATE_HOME = "HOME"
STATE_AWAY = "AWAY"
STATE_SLEEPING = "SLEEPING"

# Days of week
WEEKDAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
WEEKEND_DAYS = {"Saturday", "Sunday"}

# Wake-up times
WEEKDAY_WAKE_TIME = "05:40"
WEEKEND_WAKE_TIME = "07:00"

# Fan speed bounds
FAN_SPEED_MIN = 0
FAN_SPEED_MAX = 100
FAN_SPEED_DEFAULT = 50

# Comfort temperature range (Celsius)
COMFORT_TEMP_MIN = 23
COMFORT_TEMP_MAX = 25

# Presence detection
AWAY_TIMEOUT_MINUTES = 120

# Tool names
TOOL_TURN_ON_LIGHT = "turn_on_light"
TOOL_TURN_OFF_LIGHT = "turn_off_light"
TOOL_SET_FAN_SPEED = "set_fan_speed"
TOOL_GET_ROOM_CONDITIONS = "get_room_conditions"
TOOL_GET_TIME = "get_time"
TOOL_GET_DAY = "get_day"
TOOL_PREDICT_COMFORT = "predict_comfort"
TOOL_SAY = "say"

# Greeting messages
WEEKDAY_GREETING = "Good morning, Sir! Time to rise and shine!"
WEEKEND_GREETING = "Good morning, Sir! Happy weekend!"
ARRIVAL_GREETING = "Welcome home, Sir! Setting up your room."
DEPARTURE_MESSAGE = "Goodbye, Sir! Have a great day."

# Event types for logging
EVENT_WAKE_UP = "wake_up"
EVENT_ARRIVAL = "arrival"
EVENT_DEPARTURE = "departure"
EVENT_LIGHT_ON = "light_on"
EVENT_LIGHT_OFF = "light_off"
EVENT_FAN_SPEED = "fan_speed"
EVENT_CHAT = "chat"
EVENT_AUTOMATION = "automation"
