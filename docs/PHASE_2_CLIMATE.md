# Phase 2 — Climate Prediction

> **Coming in Week 2**

## Goals

- Predict room temperature trends (LSTM model)
- Optimize comfort automatically
- Energy-saving mode
- Advanced automation rules
- Historical pattern analysis from Phase 1 data

## Planned Features

- `ClimatePredictor` — LSTM-based temperature forecasting
- Comfort score calculation (temp + humidity)
- Proactive fan adjustment before discomfort occurs
- Daily energy usage tracking
- Real DHT sensor integration

## Data Requirements

Phase 1 logs all events to `data/events_log.jsonl`. Phase 2 will train on this data.

## Model Architecture

```
Inputs: [temperature, humidity, time_of_day, day_of_week, fan_speed]
       → LSTM(64 units) → Dense(32) → Dense(1)
Output: predicted_temperature_30_min_ahead
```
