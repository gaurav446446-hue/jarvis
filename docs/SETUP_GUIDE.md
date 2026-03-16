# Setup Guide

## System Requirements
- Python 3.10 or higher
- 512 MB RAM minimum
- Linux / macOS / Windows (WSL recommended)

## Python Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
| Package | Purpose |
|---------|---------|
| `pyyaml` | Configuration loading |
| `rich` | Terminal UI |
| `ollama` | Local LLM (optional) |
| `scikit-learn` | ML utilities (Phase 3) |
| `numpy` | Numerical computing |
| `pandas` | Data analysis |
| `pytest` | Testing |

## Optional: Ollama LLM

For richer natural language responses install Ollama:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull mistral
```

Jarvis works without Ollama using rule-based fallback responses.

## Configuration

Edit `config.yaml` to personalise:

```yaml
user:
  name: "Sir"
  wake_times:
    weekday: "05:40"
    weekend: "07:00"
```

## Running Tests

```bash
pytest tests/ -v
```
