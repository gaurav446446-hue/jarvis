# Troubleshooting

## Ollama not installed
Jarvis works without Ollama. Responses will use rule-based fallback.
To install: `curl -fsSL https://ollama.ai/install.sh | sh && ollama pull mistral`

## ImportError: No module named 'yaml'
```bash
pip install pyyaml
```

## ImportError: No module named 'rich'
```bash
pip install rich
```

## Tests failing
```bash
pip install pytest pyyaml rich numpy
pytest tests/ -v --tb=short
```

## Config file not found
Jarvis falls back to built-in defaults. Create `config.yaml` from the template
in the repository root.

## Fan speed ValueError
Fan speed must be between 0 and 100. Check your command:
```
Set fan to 50%   ✓
Set fan to 150%  ✗
```

## Log file not created
Ensure the `data/` directory exists:
```bash
mkdir -p data
```

## Conversation history not saving
Check that `data/` is writable:
```bash
ls -la data/
```
