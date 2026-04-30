"""Reusable dialogs: tag editor, add radio, generate playlist."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..tags import TagInfo


class TagEditorDialog(QDialog):
    def __init__(self, tag: TagInfo, *, file_path: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit Tags")
        self.setMinimumWidth(420)

        self._title = QLineEdit(tag.title)
        self._artist = QLineEdit(tag.artist)
        self._album = QLineEdit(tag.album)
        self._year = QLineEdit(tag.year)
        self._genre = QLineEdit(tag.genre)
        self._track = QSpinBox()
        self._track.setMaximum(9999)
        self._track.setValue(int(tag.track_number or 0))

        form = QFormLayout()
        if file_path:
            file_label = QLabel(file_path)
            file_label.setWordWrap(True)
            file_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            form.addRow("File:", file_label)
        form.addRow("Title:", self._title)
        form.addRow("Artist:", self._artist)
        form.addRow("Album:", self._album)
        form.addRow("Year:", self._year)
        form.addRow("Genre:", self._genre)
        form.addRow("Track #:", self._track)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def result_tag(self) -> TagInfo:
        return TagInfo(
            title=self._title.text().strip(),
            artist=self._artist.text().strip(),
            album=self._album.text().strip(),
            year=self._year.text().strip(),
            genre=self._genre.text().strip(),
            track_number=int(self._track.value()),
        )


class AddRadioDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Radio Stream")
        self.setMinimumWidth(420)

        self._name = QLineEdit()
        self._name.setPlaceholderText("Metro 95.1")
        self._url = QLineEdit()
        self._url.setPlaceholderText("https://example.com/stream.mp3")
        self._genre = QLineEdit()

        form = QFormLayout()
        form.addRow("Name:", self._name)
        form.addRow("URL:", self._url)
        form.addRow("Genre:", self._genre)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _accept(self) -> None:
        if not self._url.text().strip():
            self._url.setFocus()
            return
        self.accept()

    def values(self) -> tuple[str, str, str]:
        return (
            self._url.text().strip(),
            self._name.text().strip(),
            self._genre.text().strip(),
        )


class GenerateListDialog(QDialog):
    """Replicates legacy "Generate List" — copy filtered songs to a folder."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Generate Playlist Folder")
        self.setMinimumWidth(480)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("artist or album substring (empty = all)")
        self._size = QSpinBox()
        self._size.setRange(1, 1024 * 1024)
        self._size.setSuffix(" MB")
        self._size.setValue(700)
        self._dir = QLineEdit()
        browse = QPushButton("Browse…")
        browse.clicked.connect(self._browse)
        dir_row = QWidget()
        dir_layout = QHBoxLayout(dir_row)
        dir_layout.setContentsMargins(0, 0, 0, 0)
        dir_layout.addWidget(self._dir)
        dir_layout.addWidget(browse)

        form = QFormLayout()
        form.addRow("Filter:", self._filter)
        form.addRow("Max size:", self._size)
        form.addRow("Destination:", dir_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose destination folder", str(Path.home()))
        if path:
            self._dir.setText(path)

    def _accept(self) -> None:
        if not self._dir.text().strip():
            self._dir.setFocus()
            return
        self.accept()

    def values(self) -> tuple[str, str, int]:
        return (
            self._filter.text().strip(),
            self._dir.text().strip(),
            int(self._size.value()),
        )
