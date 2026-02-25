from __future__ import annotations

from dataclasses import dataclass

from .config import FilteringConfig

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(slots=True)
class Event:
    source_type: str
    source_name: str
    title: str
    summary: str
    url: str
    severity: str = "low"


@dataclass(slots=True)
class PolicyMatch:
    matched: bool
    reason: str


def infer_severity(text: str) -> str:
    low = text.lower()
    if any(k in low for k in ["critical", "actively exploited", "rce"]):
        return "critical"
    if any(k in low for k in ["high", "urgent", "zero-day", "0day"]):
        return "high"
    if any(k in low for k in ["moderate", "medium"]):
        return "medium"
    return "low"


def event_from_payload(source_type: str, source_name: str, title: str, summary: str, url: str) -> Event:
    severity = infer_severity(f"{title} {summary}")
    return Event(
        source_type=source_type,
        source_name=source_name,
        title=title,
        summary=summary,
        url=url,
        severity=severity,
    )


def _severity_at_least(severity: str, threshold: str) -> bool:
    return SEVERITY_ORDER.get(severity, 1) >= SEVERITY_ORDER.get(threshold, 1)


def match_policy(event: Event, filtering: FilteringConfig) -> PolicyMatch:
    haystack = f"{event.title} {event.summary} {event.source_name}".lower()
    if not _severity_at_least(event.severity, filtering.min_severity):
        return PolicyMatch(False, f"severity<{filtering.min_severity}")

    for excluded in filtering.exclude_keywords:
        if excluded.lower() in haystack:
            return PolicyMatch(False, f"excluded:{excluded}")

    includes = filtering.include_keywords
    if includes and not any(word.lower() in haystack for word in includes):
        return PolicyMatch(False, "include_keywords_not_matched")

    return PolicyMatch(True, "matched")
