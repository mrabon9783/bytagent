from __future__ import annotations

import logging
from typing import Iterable

import feedparser
import httpx

from .config import GitHubSource, RSSSource, YouTubeSource
from .policy import Event, event_from_payload

logger = logging.getLogger(__name__)


def _trim(text: str | None, size: int = 500) -> str:
    if not text:
        return ""
    text = " ".join(text.split())
    return text[:size]


def poll_rss(sources: Iterable[RSSSource]) -> list[Event]:
    events: list[Event] = []
    for src in sources:
        feed = feedparser.parse(src.url)
        for entry in feed.entries[:20]:
            title = entry.get("title", "untitled")
            summary = _trim(entry.get("summary", ""))
            url = entry.get("link", src.url)
            events.append(event_from_payload("rss", src.name, title, summary, url))
    logger.info("rss polling produced %s events", len(events))
    return events


async def poll_github_releases(sources: Iterable[GitHubSource], token: str | None = None) -> list[Event]:
    events: list[Event] = []
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    async with httpx.AsyncClient(timeout=20) as client:
        for src in sources:
            if "releases" not in src.watch:
                continue
            url = f"https://api.github.com/repos/{src.owner}/{src.repo}/releases"
            try:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
            except Exception as exc:
                logger.warning("github poll failed for %s/%s: %s", src.owner, src.repo, exc)
                continue
            for rel in resp.json()[:10]:
                title = rel.get("name") or rel.get("tag_name") or "release"
                body = _trim(rel.get("body", ""))
                link = rel.get("html_url", url)
                events.append(event_from_payload("github", f"{src.owner}/{src.repo}", title, body, link))
    logger.info("github polling produced %s events", len(events))
    return events


def poll_youtube(sources: Iterable[YouTubeSource]) -> list[Event]:
    events: list[Event] = []
    for src in sources:
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={src.channel_id}"
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:10]:
            title = entry.get("title", "video")
            summary = _trim(entry.get("summary", ""))
            link = entry.get("link", feed_url)
            events.append(event_from_payload("youtube", src.name, title, summary, link))
    logger.info("youtube polling produced %s events", len(events))
    return events
