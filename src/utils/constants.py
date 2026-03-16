"""Constants and enumerations for Jarvis AI."""
from enum import Enum, auto


class Intent(Enum):
    """User intent types."""
    CONTROL = "control"
    QUERY = "query"
    GREETING = "greeting"
    CONTEXT = "context"
    EXPLAIN = "explain"
    COMFORT = "comfort"
    UNKNOWN = "unknown"


class DeviceState(Enum):
    """Device on/off states."""
    ON = "on"
    OFF = "off"


class PresenceState(Enum):
    """Room presence states."""
    HOME = "home"
    AWAY = "away"


class FanSpeed(Enum):
    """Common fan speed presets."""
    OFF = 0
    LOW = 25
    MEDIUM = 50
    HIGH = 75
    MAX = 100


# Wake-up times
WEEKDAY_WAKE_TIME = "05:40"
WEEKEND_WAKE_TIME = "07:00"
WEEKDAYS = [0, 1, 2, 3, 4]   # Monday=0 … Friday=4
WEEKEND_DAYS = [5, 6]          # Saturday=5, Sunday=6

# Fan speed limits
FAN_SPEED_MIN = 0
FAN_SPEED_MAX = 100
DEFAULT_FAN_SPEED = 50

# Temperature comfort range (°C)
TEMP_MIN = 23
TEMP_MAX = 25
TEMP_HIGH_THRESHOLD = 26
TEMP_LOW_THRESHOLD = 22

# Humidity comfort range (%)
HUMIDITY_MIN = 40
HUMIDITY_MAX = 75

# Absence threshold before auto-off (seconds)
EXTENDED_ABSENCE_SECONDS = 7200  # 2 hours

# Light brightness
DEFAULT_BRIGHTNESS = 80
FADE_IN_DURATION = 2  # seconds

# User identity
USER_NAME = "Sir"
