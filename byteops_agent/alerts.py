from __future__ import annotations

import logging
import time

from .config import NotificationsConfig
from .policy import Event

logger = logging.getLogger(__name__)


class AlertManager:
    def __init__(self, config: NotificationsConfig):
        self.config = config
        self._last_tts_at = 0.0

    def notify(self, event: Event) -> None:
        if not self.config.enabled:
            return

        self._desktop_notify(event)
        self._tts_notify(event)

    def _desktop_notify(self, event: Event) -> None:
        # Optional winotify path on Windows if installed.
        if self.config.desktop.windows_preferred:
            try:
                from winotify import Notification  # type: ignore

                toast = Notification(
                    app_id="ByteOps Agent",
                    title=f"[{event.severity.upper()}] {event.source_name}",
                    msg=event.title,
                )
                toast.show()
                return
            except Exception:
                pass

        try:
            from plyer import notification

            notification.notify(
                title=f"[{event.severity.upper()}] {event.source_name}",
                message=event.title,
                app_name="ByteOps Agent",
                timeout=8,
            )
        except Exception as exc:
            logger.warning("desktop notification failed: %s", exc)

    def _tts_notify(self, event: Event) -> None:
        tts = self.config.tts
        if not tts.enabled:
            return

        now = time.time()
        if now - self._last_tts_at < tts.cooldown_seconds:
            return

        if tts.engine != "pyttsx3":
            return

        try:
            import pyttsx3

            engine = pyttsx3.init()
            if tts.voice_hint:
                for voice in engine.getProperty("voices"):
                    if tts.voice_hint.lower() in (voice.name or "").lower():
                        engine.setProperty("voice", voice.id)
                        break
            engine.say(f"{event.source_name}. {event.title}")
            engine.runAndWait()
            self._last_tts_at = now
        except Exception as exc:
            logger.warning("tts failed: %s", exc)
