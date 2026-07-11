# Dust Investment Agent 2.0

## Richtige GitHub-Struktur

```text
app.py
requirements.txt
README.md
.gitignore
dust_agent/
  __init__.py
  ai.py
  config.py
  fmp.py
  metrics.py
  pdf_report.py
  scoring.py
.streamlit/
  secrets.example.toml
```

## Streamlit Secrets

```toml
OPENAI_API_KEY = "sk-..."
FMP_API_KEY = "..."
OPENAI_MODEL = "gpt-5-mini"
```

## Streamlit Deploy

- Repository: `michaeldust-debug/dust-investment-agent_`
- Branch: `main`
- Main file path: `app.py`

Für Friedrich Vorwerk funktionieren `A255F1`, `DE000A255F11`, `VH2` und `VH2.DE`.
