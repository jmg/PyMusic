"""Discord rich presence integration.

Activates only if pypresence is installed and a Discord client is
listening on the local IPC socket. Silent fallback otherwise.
"""

import time

try:
    from pypresence import Presence
    _AVAILABLE = True
except ImportError:
    Presence = None
    _AVAILABLE = False

# Public Discord application id; users can replace via env var.
import os
APP_ID = os.environ.get("PYMUSIC_DISCORD_APP_ID", "1252525252525252525")


class DiscordPresence:

    def __init__(self):
        self.rpc = None
        self._started_at = None

    def start(self):
        if not _AVAILABLE:
            return
        try:
            self.rpc = Presence(APP_ID)
            self.rpc.connect()
        except Exception:
            self.rpc = None

    def update_track(self, song, artist):
        if not self.rpc:
            return
        try:
            if not self._started_at:
                self._started_at = int(time.time())
            self.rpc.update(
                details=song or "Unknown",
                state=f"by {artist}" if artist else "PyMusic",
                start=self._started_at,
                large_image="logo",
                large_text="PyMusic",
            )
        except Exception:
            pass

    def clear(self):
        if not self.rpc:
            return
        try:
            self.rpc.clear()
            self._started_at = None
        except Exception:
            pass

    def stop(self):
        if not self.rpc:
            return
        try:
            self.rpc.close()
        except Exception:
            pass
        self.rpc = None
