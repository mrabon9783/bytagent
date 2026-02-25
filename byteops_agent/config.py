from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class RSSSource(BaseModel):
    name: str
    url: str


class GitHubSource(BaseModel):
    owner: str
    repo: str
    watch: list[str] = Field(default_factory=list)


class YouTubeSource(BaseModel):
    name: str
    channel_id: str


class WatchlistConfig(BaseModel):
    poll_seconds: int = 240
    rss: list[RSSSource] = Field(default_factory=list)
    github: list[GitHubSource] = Field(default_factory=list)
    youtube: list[YouTubeSource] = Field(default_factory=list)


class DesktopNotifications(BaseModel):
    provider: str = "plyer"
    windows_preferred: bool = True


class TTSSettings(BaseModel):
    enabled: bool = False
    engine: str = "pyttsx3"
    voice_hint: str = "zira"
    cooldown_seconds: int = 120


class NotificationsConfig(BaseModel):
    enabled: bool = True
    desktop: DesktopNotifications = Field(default_factory=DesktopNotifications)
    tts: TTSSettings = Field(default_factory=TTSSettings)


class FilteringConfig(BaseModel):
    min_severity: str = "low"
    include_keywords: list[str] = Field(default_factory=list)
    exclude_keywords: list[str] = Field(default_factory=list)


class RoutingSettings(BaseModel):
    enabled: bool = True


class RoutingConfig(BaseModel):
    rss: RoutingSettings = Field(default_factory=RoutingSettings)
    github: RoutingSettings = Field(default_factory=RoutingSettings)
    youtube: RoutingSettings = Field(default_factory=RoutingSettings)


class PolicyConfig(BaseModel):
    defaults: dict[str, Any] = Field(default_factory=dict)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    filtering: FilteringConfig = Field(default_factory=FilteringConfig)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)


class AgentConfig(BaseModel):
    watchlist: WatchlistConfig
    policy: PolicyConfig


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return raw


def load_agent_config(watchlist_path: Path, policy_path: Path) -> AgentConfig:
    watchlist = WatchlistConfig.model_validate(_load_yaml(watchlist_path))
    policy = PolicyConfig.model_validate(_load_yaml(policy_path))
    return AgentConfig(watchlist=watchlist, policy=policy)
