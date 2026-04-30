"""Application configuration and paths.

Resolves database, cache, and config locations, preferring an
in-repo database when present (so the legacy ``database/MusicaInYou.db``
keeps working) and falling back to platform-appropriate user dirs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from platformdirs import user_cache_dir, user_config_dir, user_data_dir
except ImportError:  # pragma: no cover - platformdirs is required at runtime
    def user_data_dir(app: str) -> str:
        return os.path.join(os.path.expanduser("~"), f".{app}")

    def user_cache_dir(app: str) -> str:
        return os.path.join(os.path.expanduser("~"), f".{app}", "cache")

    def user_config_dir(app: str) -> str:
        return os.path.join(os.path.expanduser("~"), f".{app}", "config")


APP_NAME = "PyMusic"
LEGACY_DB = Path(__file__).resolve().parent.parent / "database" / "MusicaInYou.db"


def _default_db_path() -> Path:
    if LEGACY_DB.exists():
        return LEGACY_DB
    return Path(user_data_dir(APP_NAME)) / "library.db"


@dataclass(frozen=True)
class Settings:
    db_path: Path = field(default_factory=_default_db_path)
    cache_dir: Path = field(default_factory=lambda: Path(user_cache_dir(APP_NAME)))
    config_dir: Path = field(default_factory=lambda: Path(user_config_dir(APP_NAME)))
    audio_extensions: tuple[str, ...] = (
        ".mp3", ".flac", ".ogg", ".oga", ".m4a", ".aac",
        ".wav", ".wma", ".opus", ".alac", ".aiff",
    )

    def ensure_dirs(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def lyrics_cache_dir(self) -> Path:
        return self.cache_dir / "lyrics"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.ensure_dirs()
    return _settings


def configure(db_path: Path | str | None = None) -> Settings:
    """Override settings (used by tests and the CLI's --db flag)."""
    global _settings
    if db_path is None:
        _settings = Settings()
    else:
        _settings = Settings(db_path=Path(db_path))
    _settings.ensure_dirs()
    return _settings
