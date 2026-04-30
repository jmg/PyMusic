"""Audio playback backend.

Wraps libVLC via the python-vlc bindings. libVLC handles every format
the legacy gstreamer pipeline did and gracefully streams network radios.
"""

from __future__ import annotations

import enum
import logging
from collections.abc import Callable
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import vlc  # type: ignore[import-untyped]
except (ImportError, OSError):  # pragma: no cover - vlc may be missing in CI
    vlc = None  # type: ignore[assignment]


class PlayerError(RuntimeError):
    pass


class State(enum.Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


_VLC_STATE_MAP: dict[int, State] = {}


def _build_state_map() -> None:
    if vlc is None:
        return
    _VLC_STATE_MAP.update({
        vlc.State.NothingSpecial: State.STOPPED,
        vlc.State.Opening: State.PLAYING,
        vlc.State.Buffering: State.PLAYING,
        vlc.State.Playing: State.PLAYING,
        vlc.State.Paused: State.PAUSED,
        vlc.State.Stopped: State.STOPPED,
        vlc.State.Ended: State.ENDED,
        vlc.State.Error: State.ERROR,
    })


_build_state_map()


class Player:
    """Thin, testable wrapper around :class:`vlc.MediaPlayer`."""

    def __init__(self) -> None:
        if vlc is None:
            raise PlayerError(
                "python-vlc is required. Install with `pip install python-vlc` "
                "and ensure libvlc is on your system."
            )
        self._instance = vlc.Instance("--no-video", "--quiet")
        self._player: vlc.MediaPlayer = self._instance.media_player_new()
        self._volume: int = 80
        self._player.audio_set_volume(self._volume)
        self._on_end: Optional[Callable[[], None]] = None
        self._media_path: str = ""
        self._is_stream: bool = False

        # Hook end-of-track event so the GUI can advance.
        em = self._player.event_manager()
        em.event_attach(vlc.EventType.MediaPlayerEndReached, self._fire_on_end)

    # ---- core controls -------------------------------------------------

    def play(self, path_or_url: str) -> None:
        if not path_or_url:
            raise PlayerError("empty path")
        media = self._instance.media_new(path_or_url)
        self._player.set_media(media)
        self._media_path = path_or_url
        self._is_stream = "://" in path_or_url
        rc = self._player.play()
        if rc == -1:
            raise PlayerError(f"libvlc refused to play {path_or_url!r}")

    def pause(self) -> None:
        if self._player.is_playing():
            self._player.pause()

    def resume(self) -> None:
        if not self._player.is_playing():
            self._player.play()

    def toggle_pause(self) -> None:
        self._player.pause()  # libvlc toggles when called this way

    def stop(self) -> None:
        self._player.stop()
        self._media_path = ""

    # ---- volume / position --------------------------------------------

    @property
    def volume(self) -> int:
        return self._volume

    @volume.setter
    def volume(self, value: int) -> None:
        self._volume = max(0, min(100, int(value)))
        self._player.audio_set_volume(self._volume)

    def get_position(self) -> float:
        """Position in [0.0, 1.0]. Returns 0 for streams without duration."""
        pos = self._player.get_position()
        return max(0.0, pos)

    def set_position(self, value: float) -> None:
        if self._is_stream:
            return
        self._player.set_position(max(0.0, min(1.0, float(value))))

    def get_time(self) -> float:
        """Elapsed time in seconds. -1 if unknown."""
        ms = self._player.get_time()
        return ms / 1000.0 if ms >= 0 else -1.0

    def get_length(self) -> float:
        """Total length in seconds. 0 for live streams."""
        ms = self._player.get_length()
        return ms / 1000.0 if ms > 0 else 0.0

    # ---- state ---------------------------------------------------------

    @property
    def state(self) -> State:
        if vlc is None:
            return State.ERROR
        return _VLC_STATE_MAP.get(self._player.get_state(), State.STOPPED)

    @property
    def is_playing(self) -> bool:
        return self.state is State.PLAYING

    @property
    def is_stream(self) -> bool:
        return self._is_stream

    @property
    def current_media(self) -> str:
        return self._media_path

    # ---- callbacks -----------------------------------------------------

    def on_end(self, callback: Optional[Callable[[], None]]) -> None:
        self._on_end = callback

    def _fire_on_end(self, _event) -> None:  # noqa: ANN001
        cb = self._on_end
        if cb is None:
            return
        try:
            cb()
        except Exception:  # noqa: BLE001
            logger.exception("on_end callback raised")

    # ---- cleanup -------------------------------------------------------

    def release(self) -> None:
        try:
            self._player.stop()
            self._player.release()
            self._instance.release()
        except Exception:  # noqa: BLE001
            pass
