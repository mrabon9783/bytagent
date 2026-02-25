# ByteOps Agent (Windows-first, local-first)

ByteOps Agent is a local monitoring service that polls security/news sources and highlights signal using local policy rules.

## What is implemented

- Startup config loading from `config/watchlist.yaml` and `config/policy.yaml`.
- Background polling loop driven by `poll_seconds`.
- Source pollers:
  - RSS feeds
  - GitHub releases
  - YouTube channel feeds
- SQLite-backed dedupe fingerprints and event history (`data/agent.db`).
- Policy matching (severity + include/exclude keywords).
- Desktop notifications (`winotify` optional, `plyer` fallback).
- Optional TTS summaries via `pyttsx3` with cooldown.
- Local dashboard pages:
  - `GET /dashboard/events`
  - `GET /dashboard/matches`
- Startup diagnostics and structured logging.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m byteops_agent
```

Then open:
- `http://127.0.0.1:8844/`
- `http://127.0.0.1:8844/dashboard/events`
- `http://127.0.0.1:8844/dashboard/matches`

## Optional GitHub API token

```bash
export GITHUB_TOKEN=ghp_xxx
```

## Tests and checks

```bash
pytest -q
ruff check .
mypy byteops_agent
```

## CI

GitHub Actions workflow runs lint/type/tests on push + pull requests.
