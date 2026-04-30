"""Qt item models for songs and radios."""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from ..db import Radio, Song
from ..tags import format_duration


class SongTableModel(QAbstractTableModel):
    HEADERS = ("#", "Title", "Artist", "Album", "Year", "Genre", "Length", "Plays")

    def __init__(self, songs: Optional[list[Song]] = None) -> None:
        super().__init__()
        self._songs: list[Song] = list(songs or [])

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        if parent.isValid():
            return 0
        return len(self._songs)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return section + 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        song = self._songs[index.row()]
        col = index.column()
        if role == Qt.DisplayRole:
            return [
                song.track_number or "",
                song.display_title,
                song.artist or "",
                song.album or "",
                song.year or "",
                song.genre or "",
                format_duration(song.duration or 0),
                song.play_count or 0,
            ][col]
        if role == Qt.ToolTipRole:
            return song.path
        if role == Qt.UserRole:
            return song.id
        if role == Qt.TextAlignmentRole and col in (0, 6, 7):
            return int(Qt.AlignRight | Qt.AlignVCenter)
        return None

    # ---- helpers used by the controller --------------------------------

    def replace(self, songs: list[Song]) -> None:
        self.beginResetModel()
        self._songs = list(songs)
        self.endResetModel()

    def song_at(self, row: int) -> Optional[Song]:
        if 0 <= row < len(self._songs):
            return self._songs[row]
        return None

    @property
    def songs(self) -> list[Song]:
        return self._songs


class RadioTableModel(QAbstractTableModel):
    HEADERS = ("Name", "URL", "Genre")

    def __init__(self, radios: Optional[list[Radio]] = None) -> None:
        super().__init__()
        self._radios: list[Radio] = list(radios or [])

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        if parent.isValid():
            return 0
        return len(self._radios)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return len(self.HEADERS)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole) -> Any:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.HEADERS[section]
        return section + 1

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        radio = self._radios[index.row()]
        if role == Qt.DisplayRole:
            return [radio.name or "(unnamed)", radio.url, radio.genre or ""][index.column()]
        if role == Qt.UserRole:
            return radio.id
        return None

    def replace(self, radios: list[Radio]) -> None:
        self.beginResetModel()
        self._radios = list(radios)
        self.endResetModel()

    def radio_at(self, row: int) -> Optional[Radio]:
        if 0 <= row < len(self._radios):
            return self._radios[row]
        return None
