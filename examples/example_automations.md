# Example Automations

## Wake-Up Automation (Weekday)
Triggered at **05:40 AM** Monday–Friday:
1. Fade-in light over 2 seconds
2. "Good morning, Sir! Time to rise and shine!"
3. Set fan to 50%

## Wake-Up Automation (Weekend)
Triggered at **07:00 AM** Saturday–Sunday:
1. Fade-in light over 2 seconds
2. "Good morning, Sir! Happy weekend!"
3. Set fan to 50%

## Arrival Automation
Triggered when presence detected after absence:
1. Turn on light
2. Set fan to 50%
3. "Welcome home, Sir!"

## Extended Absence Automation
Triggered after 2 hours without presence:
1. Turn off all lights
2. Turn off fan (speed = 0%)
3. Set presence state to AWAY

## Comfort Automation (Too Hot)
Triggered by "It's too hot" or temperature > 26°C:
1. Set fan speed to 75%

## Comfort Automation (Too Cold)
Triggered by "Too cold" or temperature < 22°C:
1. Set fan speed to 25%
