"""ListenBrainz scrobbling.

Submit ``listen`` events using a personal user token. Token lives in
state.json. Fail silently if not configured.
"""

import json
import time
from urllib.request import Request, urlopen


SUBMIT_URL = "https://api.listenbrainz.org/1/submit-listens"


def submit_listen(token, song, artist, album=None, listened_at=None):
    if not token or not song or not artist:
        return False
    payload = {
        "listen_type": "single",
        "payload": [{
            "listened_at": int(listened_at or time.time()),
            "track_metadata": {
                "track_name": song,
                "artist_name": artist,
                "release_name": album or "",
            },
        }],
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        SUBMIT_URL,
        data=data,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=4) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def submit_now_playing(token, song, artist, album=None):
    if not token or not song or not artist:
        return False
    payload = {
        "listen_type": "playing_now",
        "payload": [{
            "track_metadata": {
                "track_name": song,
                "artist_name": artist,
                "release_name": album or "",
            },
        }],
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        SUBMIT_URL,
        data=data,
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=4) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False
