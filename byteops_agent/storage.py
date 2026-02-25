from __future__ import annotations

import hashlib
from pathlib import Path

import aiosqlite

from .policy import Event


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS dedupe_fingerprints (
                    fingerprint TEXT PRIMARY KEY,
                    first_seen_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    url TEXT,
                    severity TEXT NOT NULL,
                    matched INTEGER NOT NULL,
                    match_reason TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            await db.commit()

    @staticmethod
    def make_fingerprint(event: Event) -> str:
        payload = f"{event.source_type}|{event.source_name}|{event.title}|{event.url}".encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    async def mark_if_new(self, fingerprint: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT OR IGNORE INTO dedupe_fingerprints(fingerprint) VALUES (?)",
                (fingerprint,),
            )
            await db.commit()
            return cursor.rowcount == 1

    async def save_event(self, event: Event, matched: bool, reason: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO events(source_type, source_name, title, summary, url, severity, matched, match_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.source_type,
                    event.source_name,
                    event.title,
                    event.summary,
                    event.url,
                    event.severity,
                    1 if matched else 0,
                    reason,
                ),
            )
            await db.commit()

    async def recent_events(self, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM events ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
                (limit,),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]

    async def recent_matches(self, limit: int = 50) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM events WHERE matched = 1 ORDER BY datetime(created_at) DESC, id DESC LIMIT ?",
                (limit,),
            )
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
