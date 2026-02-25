from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .alerts import AlertManager
from .config import AgentConfig, load_agent_config
from .policy import match_policy
from .pollers import poll_github_releases, poll_rss, poll_youtube
from .storage import Storage

LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent
WATCHLIST_PATH = ROOT / "config" / "watchlist.yaml"
POLICY_PATH = ROOT / "config" / "policy.yaml"
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "agent.db"


def _load_runtime() -> tuple[AgentConfig, Storage, AlertManager]:
    config = load_agent_config(WATCHLIST_PATH, POLICY_PATH)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    storage = Storage(DB_PATH)
    alerts = AlertManager(config.policy.notifications)
    return config, storage, alerts


async def polling_loop(app: FastAPI) -> None:
    config: AgentConfig = app.state.agent_config
    storage: Storage = app.state.storage
    alerts: AlertManager = app.state.alerts
    token = os.getenv("GITHUB_TOKEN")

    while True:
        try:
            events = []
            if config.policy.routing.rss.enabled:
                events.extend(poll_rss(config.watchlist.rss))
            if config.policy.routing.github.enabled:
                events.extend(await poll_github_releases(config.watchlist.github, token))
            if config.policy.routing.youtube.enabled:
                events.extend(poll_youtube(config.watchlist.youtube))

            new_count = 0
            for event in events:
                fingerprint = storage.make_fingerprint(event)
                is_new = await storage.mark_if_new(fingerprint)
                if not is_new:
                    continue
                new_count += 1
                result = match_policy(event, config.policy.filtering)
                await storage.save_event(event, result.matched, result.reason)
                if result.matched:
                    alerts.notify(event)

            logger.info(
                "poll cycle completed total_events=%s new_events=%s sleep_seconds=%s",
                len(events),
                new_count,
                config.watchlist.poll_seconds,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("polling loop failed: %s", exc)

        await asyncio.sleep(config.watchlist.poll_seconds)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config, storage, alerts = _load_runtime()
    await storage.init()
    app.state.agent_config = config
    app.state.storage = storage
    app.state.alerts = alerts
    logger.info(
        "startup diagnostics watchlist=%s policy=%s db=%s poll_seconds=%s rss=%s github=%s youtube=%s",
        WATCHLIST_PATH,
        POLICY_PATH,
        DB_PATH,
        config.watchlist.poll_seconds,
        len(config.watchlist.rss),
        len(config.watchlist.github),
        len(config.watchlist.youtube),
    )

    task = asyncio.create_task(polling_loop(app))
    app.state.poll_task = task
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="ByteOps Agent", lifespan=lifespan)
templates = Jinja2Templates(directory=str(ROOT / "byteops_agent" / "templates"))


@app.get("/")
def home():
    return {
        "status": "ByteOps Agent running",
        "dashboard": "http://127.0.0.1:8844/dashboard/events",
    }


@app.get("/dashboard/events", response_class=HTMLResponse)
async def dashboard_events(request: Request):
    events = await request.app.state.storage.recent_events(limit=100)
    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={"events": events},
    )


@app.get("/dashboard/matches", response_class=HTMLResponse)
async def dashboard_matches(request: Request):
    matches = await request.app.state.storage.recent_matches(limit=100)
    return templates.TemplateResponse(
        request=request,
        name="matches.html",
        context={"events": matches},
    )


async def run():
    config = uvicorn.Config(app, host="127.0.0.1", port=8844, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
