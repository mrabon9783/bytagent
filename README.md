# ByteOps Agent (Windows MVP)

Local background AI agent:
- RSS
- GitHub
- YouTube
- Voice alerts
- Local dashboard (http://127.0.0.1:8844)

## Setup (PowerShell)

```powershell
cd byteops_agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

pip install winotify  # optional better notifications

setx GITHUB_TOKEN "ghp_yourtoken"  # optional

python -m byteops_agent
```
