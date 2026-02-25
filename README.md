# ByteOps Agent (Windows-first, local-first MVP)

ByteOps Agent is currently a **minimal FastAPI service** that starts a local HTTP endpoint at `http://127.0.0.1:8844`.

Current runtime behavior:
- Starts a local web server (`uvicorn`) on localhost only.
- Exposes a single health-style route (`GET /`).
- Returns JSON confirming the service is running.

> Note: RSS/GitHub/YouTube polling, dedupe, notifications, TTS, and dashboard UI are **not implemented yet** in code.

## Repository layout

- `byteops_agent/app.py` — FastAPI app and server startup coroutine.
- `byteops_agent/__main__.py` — entry point for `python -m byteops_agent`.
- `config/watchlist.yaml` — source/watch targets for future polling features.
- `config/policy.yaml` — local policy defaults for future filtering/notifications.

## Windows Setup (PowerShell)

```powershell
# from repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# optional: GitHub API token for future GitHub polling
setx GITHUB_TOKEN "ghp_yourtoken"

# run the service
python -m byteops_agent
```

If you get script execution errors in PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Quick verification

```powershell
# in another terminal
Invoke-RestMethod http://127.0.0.1:8844/
```

Expected response:

```json
{
  "status": "ByteOps Agent running",
  "dashboard": "coming online"
}
```

## Configuration status

### `config/watchlist.yaml`
- Valid YAML structure.
- Contains starter feeds/repos/channels.
- Not yet consumed by runtime code.

### `config/policy.yaml`
- Added as a baseline policy file for upcoming polling and alert logic.
- Local-first defaults with Windows-friendly notifier/TTS preferences.
- Not yet consumed by runtime code.

## Windows compatibility notes

- **PowerShell setup:** supported by commands above.
- **Notifications:** `plyer` is present in dependencies, but no notification code paths exist yet.
- **TTS:** `pyttsx3` is present in dependencies; Windows SAPI support is expected once integrated.
- **Current app behavior is cross-platform** because it is only FastAPI + Uvicorn today.

## Known gaps (MVP state)

1. No scheduler/poller loop.
2. No feed/repo/channel fetch clients wired to runtime.
3. No dedupe state store usage despite `aiosqlite` dependency.
4. No policy evaluation engine.
5. No notification/TTS pipeline.
6. No rendered dashboard pages (JSON root only).

## Suggested near-term roadmap

### Phase 1: Functional polling MVP
- Load `watchlist.yaml` and `policy.yaml` at startup.
- Add periodic polling loop (`poll_seconds`).
- Implement RSS polling first (smallest surface area).
- Persist dedupe fingerprints in SQLite.

### Phase 2: Alerts and signal quality
- Add policy matching (keywords/severity/source rules).
- Add Windows notifications (`plyer` fallback; `winotify` optional path).
- Add optional TTS summaries (`pyttsx3`) with cooldown/rate limits.

### Phase 3: Sources + dashboard
- Add GitHub releases polling.
- Add YouTube channel polling.
- Build local dashboard pages for recent events and policy matches.

### Phase 4: Reliability + contributor UX
- Add basic tests for config loading and policy matching.
- Add lint/type checks in CI.
- Add structured logging and clearer startup diagnostics.

## Contributor next steps

- Keep features local-first (no cloud-only dependencies).
- Prioritize Windows compatibility for notifications and TTS paths.
- Ship in thin vertical slices: config load -> poll -> dedupe -> notify -> dashboard.
- Add tests alongside each feature increment.
