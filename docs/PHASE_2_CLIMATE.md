# Phase 2 – Climate Control

## Overview
Phase 2 integrates real ESP32 hardware and adds intelligent climate control.

## Planned Features
- ESP32 serial / HTTP communication
- DHT22 temperature & humidity sensor (real readings)
- PIR motion sensor (real presence detection)
- AC unit control via IR blaster
- Automatic temperature regulation within comfort range (23–25°C)
- Fan speed auto-adjustment based on temperature

## Hardware Requirements
- ESP32 development board
- DHT22 sensor
- PIR motion sensor
- IR LED (for AC control)
- Relay module (for light/fan)

## Implementation Plan
1. Complete `ESP32Controller` with serial communication
2. Replace `SensorReader` mock with real DHT22 reads
3. Add `ACController` for IR-based AC control
4. Implement PID-style temperature regulation loop
5. Update presence detection with real PIR sensor
