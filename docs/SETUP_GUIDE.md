# Setup Guide

## Requirements

- Python 3.9 or higher
- pip
- (Optional) Ollama for LLM support

## Installation

```bash
# 1. Clone repository
git clone https://github.com/gaurav446446-hue/jarvis.git
cd jarvis

# 2. (Optional) Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Configuration

Copy and edit `config.yaml` as needed:

```yaml
user_profile:
  wake_times:
    weekday: "05:40"
    weekend: "07:00"
  preferred_fan_speed: 50

llm:
  model: "mistral"
  host: "http://localhost:11434"
```

## Ollama Setup (Optional)

```bash
# Install Ollama: https://ollama.ai/download
ollama pull mistral    # Full quality — ~4 GB
ollama pull phi        # Lighter — ~2 GB
ollama serve           # Start the server
```

## Running

```bash
python main.py
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

## Troubleshooting

**Q: Jarvis doesn't respond**  
A: Ollama may not be running. Jarvis will fall back to a built-in rule engine automatically.

**Q: Import errors**  
A: Run `pip install -r requirements.txt` again.

**Q: `data/` or `models/` directories missing**  
A: They're created automatically on first run.
