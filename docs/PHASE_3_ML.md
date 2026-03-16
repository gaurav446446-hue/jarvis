# Phase 3 – Machine Learning

## Overview
Phase 3 adds ML-based behaviour prediction and personalised automation.

## Planned Features
- Learn wake-up patterns from sensor history
- Predict optimal fan speed based on temperature + time of day
- Anomaly detection for unusual presence patterns
- Personalised comfort model (scikit-learn)
- Automated schedule learning

## Models
| Model | Purpose | Algorithm |
|-------|---------|-----------|
| ComfortPredictor | Fan speed from temperature | Linear Regression |
| WakeTimeClassifier | Predict wake-up time | Decision Tree |
| PresencePredictor | Predict arrival time | Time-series model |

## Data Requirements
- Minimum 30 days of sensor data
- Logged in `data/events_log.jsonl`

## Implementation Plan
1. Collect 30 days of baseline data (Phase 1/2)
2. Build training pipeline with pandas + scikit-learn
3. Expose predictions via `predict_comfort()` tool
4. Add online learning for continuous improvement
