"""Main application window — the heart of the modernized player."""

from __future__ import annotations

import logging
import random
from enum import Enum
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QItemSelectionModel, Qt, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QStatusBar,
    QStyle,
    QTabWidget,
    QTableView,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .. import library, lyrics, tags
from ..db import Radio, Song
from ..player import Player, PlayerError, State
from ..tags import format_duration
from .dialogs import AddRadioDialog, GenerateListDialog, TagEditorDialog
from .models import RadioTableModel, SongTableModel
from .workers import submit

logger = logging.getLogger(__name__)


class PlayMode(Enum):
    NORMAL = "normal"
    RANDOM = "random"
    REPEAT_ONE = "repeat_one"
    REPEAT_ALL = "repeat_all"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PyMusic")
        self.resize(1200, 720)

        self._player: Optional[Player] = None
        self._current_song: Optional[Song] = None
        self._mode = PlayMode.NORMAL
        self._seek_in_progress = False

        self._build_ui()
        self._init_player()
        self._connect_signals()
        self._load_library()
        self._load_radios()

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(500)
        self._tick_timer.timeout.connect(self._on_tick)
        self._tick_timer.start()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)
        self.setCentralWidget(central)

        self._build_menus()
        self._build_toolbar()

        # ---- Top: now playing ---------------------------------------
        now_playing_row = QHBoxLayout()
        self._now_playing = QLabel("Nothing playing")
        font = self._now_playing.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        self._now_playing.setFont(font)
        now_playing_row.addWidget(self._now_playing, 1)

        self._mode_label = QLabel("Mode: normal")
        now_playing_row.addWidget(self._mode_label)
        root.addLayout(now_playing_row)

        # ---- Middle: splitter (library left, side panel right) -------
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter, 1)

        # Left: tabs for Library / Radios
        left = QTabWidget()
        splitter.addWidget(left)

        # Library tab
        library_tab = QWidget()
        lib_layout = QVBoxLayout(library_tab)
        lib_layout.setContentsMargins(0, 0, 0, 0)
        search_row = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search artist, title, album, genre…  (Ctrl+F)")
        self._search.setClearButtonEnabled(True)
        search_row.addWidget(self._search)
        self._stats_label = QLabel("")
        search_row.addWidget(self._stats_label)
        lib_layout.addLayout(search_row)

        self._song_model = SongTableModel()
        self._song_view = QTableView()
        self._song_view.setModel(self._song_model)
        self._song_view.setSelectionBehavior(QTableView.SelectRows)
        self._song_view.setSelectionMode(QTableView.ExtendedSelection)
        self._song_view.setSortingEnabled(False)
        self._song_view.verticalHeader().setVisible(False)
        self._song_view.setAlternatingRowColors(True)
        header = self._song_view.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsClickable(True)
        self._song_view.doubleClicked.connect(self._play_selected_song)
        self._song_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._song_view.customContextMenuRequested.connect(self._song_context_menu)
        lib_layout.addWidget(self._song_view)
        left.addTab(library_tab, "Library")

        # Radios tab
        radio_tab = QWidget()
        rad_layout = QVBoxLayout(radio_tab)
        rad_layout.setContentsMargins(0, 0, 0, 0)
        radio_buttons = QHBoxLayout()
        self._btn_add_radio = QPushButton("Add Radio…")
        self._btn_remove_radio = QPushButton("Remove")
        radio_buttons.addWidget(self._btn_add_radio)
        radio_buttons.addWidget(self._btn_remove_radio)
        radio_buttons.addStretch(1)
        rad_layout.addLayout(radio_buttons)

        self._radio_model = RadioTableModel()
        self._radio_view = QTableView()
        self._radio_view.setModel(self._radio_model)
        self._radio_view.setSelectionBehavior(QTableView.SelectRows)
        self._radio_view.setSelectionMode(QTableView.SingleSelection)
        self._radio_view.verticalHeader().setVisible(False)
        self._radio_view.setAlternatingRowColors(True)
        self._radio_view.doubleClicked.connect(self._play_selected_radio)
        rad_layout.addWidget(self._radio_view)
        left.addTab(radio_tab, "Radios")
        self._tabs = left

        # Right: lyrics / details
        right = QTabWidget()
        splitter.addWidget(right)

        self._lyrics_view = QTextEdit()
        self._lyrics_view.setReadOnly(True)
        self._lyrics_view.setPlaceholderText("Lyrics will appear here when a song starts playing.")
        right.addTab(self._lyrics_view, "Lyrics")

        self._details_view = QTextEdit()
        self._details_view.setReadOnly(True)
        right.addTab(self._details_view, "Details")

        splitter.setSizes([850, 350])

        # ---- Bottom: transport controls -----------------------------
        controls = QWidget()
        ctl = QVBoxLayout(controls)
        ctl.setContentsMargins(0, 0, 0, 0)

        slider_row = QHBoxLayout()
        self._time_label = QLabel("0:00")
        self._position = QSlider(Qt.Horizontal)
        self._position.setRange(0, 1000)
        self._duration_label = QLabel("0:00")
        slider_row.addWidget(self._time_label)
        slider_row.addWidget(self._position, 1)
        slider_row.addWidget(self._duration_label)
        ctl.addLayout(slider_row)

        button_row = QHBoxLayout()
        style = self.style()
        self._btn_prev = QPushButton(style.standardIcon(QStyle.SP_MediaSkipBackward), "")
        self._btn_play = QPushButton(style.standardIcon(QStyle.SP_MediaPlay), "")
        self._btn_pause = QPushButton(style.standardIcon(QStyle.SP_MediaPause), "")
        self._btn_stop = QPushButton(style.standardIcon(QStyle.SP_MediaStop), "")
        self._btn_next = QPushButton(style.standardIcon(QStyle.SP_MediaSkipForward), "")
        for b in (self._btn_prev, self._btn_play, self._btn_pause, self._btn_stop, self._btn_next):
            b.setIconSize(b.iconSize() * 1.4)
            b.setFlat(False)
            button_row.addWidget(b)
        button_row.addSpacing(16)

        self._btn_random = QPushButton("Shuffle")
        self._btn_random.setCheckable(True)
        button_row.addWidget(self._btn_random)
        self._btn_repeat = QPushButton("Repeat")
        self._btn_repeat.setCheckable(True)
        button_row.addWidget(self._btn_repeat)

        button_row.addStretch(1)
        button_row.addWidget(QLabel("Vol"))
        self._volume = QSlider(Qt.Horizontal)
        self._volume.setRange(0, 100)
        self._volume.setValue(80)
        self._volume.setFixedWidth(140)
        button_row.addWidget(self._volume)
        ctl.addLayout(button_row)
        root.addWidget(controls)

        self.setStatusBar(QStatusBar())

    def _build_menus(self) -> None:
        bar = self.menuBar()

        file_menu = bar.addMenu("&File")
        self.act_scan = QAction("&Scan Folder…", self)
        self.act_scan.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(self.act_scan)
        self.act_clean = QAction("Remove &Missing Files", self)
        file_menu.addAction(self.act_clean)
        file_menu.addSeparator()
        self.act_export = QAction("&Generate Playlist Folder…", self)
        file_menu.addAction(self.act_export)
        file_menu.addSeparator()
        self.act_quit = QAction("&Quit", self)
        self.act_quit.setShortcut(QKeySequence("Ctrl+Q"))
        file_menu.addAction(self.act_quit)

        edit_menu = bar.addMenu("&Edit")
        self.act_edit_tags = QAction("Edit &Tags of Selected…", self)
        self.act_edit_tags.setShortcut(QKeySequence("F2"))
        edit_menu.addAction(self.act_edit_tags)
        self.act_focus_search = QAction("&Search…", self)
        self.act_focus_search.setShortcut(QKeySequence("Ctrl+F"))
        edit_menu.addAction(self.act_focus_search)

        play_menu = bar.addMenu("&Play")
        self.act_play = QAction("&Play / Pause", self)
        self.act_play.setShortcut(QKeySequence("Space"))
        play_menu.addAction(self.act_play)
        self.act_next = QAction("&Next", self)
        self.act_next.setShortcut(QKeySequence("Ctrl+Right"))
        play_menu.addAction(self.act_next)
        self.act_prev = QAction("Pre&vious", self)
        self.act_prev.setShortcut(QKeySequence("Ctrl+Left"))
        play_menu.addAction(self.act_prev)
        self.act_stop = QAction("&Stop", self)
        self.act_stop.setShortcut(QKeySequence("Ctrl+."))
        play_menu.addAction(self.act_stop)

        radio_menu = bar.addMenu("&Radio")
        self.act_add_radio = QAction("&Add Radio…", self)
        radio_menu.addAction(self.act_add_radio)

        help_menu = bar.addMenu("&Help")
        self.act_about = QAction("&About PyMusic", self)
        help_menu.addAction(self.act_about)

    def _build_toolbar(self) -> None:
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(tb)
        tb.addAction(self.act_scan)
        tb.addAction(self.act_clean)
        tb.addSeparator()
        tb.addAction(self.act_export)
        tb.addSeparator()
        tb.addAction(self.act_edit_tags)

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------

    def _init_player(self) -> None:
        try:
            self._player = Player()
        except PlayerError as exc:
            QMessageBox.critical(
                self,
                "Audio Backend Unavailable",
                f"Could not initialize libVLC:\n\n{exc}\n\n"
                "Install python-vlc and libvlc to enable playback.",
            )
            self._player = None
            return
        self._player.on_end(self._on_track_ended)
        self._player.volume = self._volume.value()

    def _connect_signals(self) -> None:
        self._search.textChanged.connect(self._on_search_changed)

        # Buttons
        self._btn_play.clicked.connect(self._play_or_resume)
        self._btn_pause.clicked.connect(self._pause)
        self._btn_stop.clicked.connect(self._stop)
        self._btn_next.clicked.connect(self._play_next)
        self._btn_prev.clicked.connect(self._play_previous)
        self._btn_random.toggled.connect(self._on_shuffle_toggled)
        self._btn_repeat.toggled.connect(self._on_repeat_toggled)
        self._volume.valueChanged.connect(self._on_volume_changed)

        # Slider
        self._position.sliderPressed.connect(lambda: setattr(self, "_seek_in_progress", True))
        self._position.sliderReleased.connect(self._on_seek_released)

        # Radios
        self._btn_add_radio.clicked.connect(self._add_radio)
        self._btn_remove_radio.clicked.connect(self._remove_radio)

        # Menu actions
        self.act_scan.triggered.connect(self._scan_folder)
        self.act_clean.triggered.connect(self._clean_missing)
        self.act_export.triggered.connect(self._open_generate_dialog)
        self.act_quit.triggered.connect(self.close)
        self.act_edit_tags.triggered.connect(self._edit_selected_tags)
        self.act_focus_search.triggered.connect(lambda: (self._search.setFocus(), self._search.selectAll()))
        self.act_play.triggered.connect(self._play_or_resume)
        self.act_next.triggered.connect(self._play_next)
        self.act_prev.triggered.connect(self._play_previous)
        self.act_stop.triggered.connect(self._stop)
        self.act_add_radio.triggered.connect(self._add_radio)
        self.act_about.triggered.connect(self._show_about)

    # ------------------------------------------------------------------
    # Library loading
    # ------------------------------------------------------------------

    def _load_library(self, query: str = "") -> None:
        def fetch():
            if query.strip():
                return library.search_songs(query)
            return library.fetch_all_songs()

        def done(songs):
            self._song_model.replace(songs)
            self._auto_size_columns()
            self._update_stats_label()

        submit(fetch, on_finished=done, on_error=self._show_error)

    def _load_radios(self) -> None:
        def done(radios):
            self._radio_model.replace(radios)
            self._radio_view.resizeColumnsToContents()

        submit(library.fetch_radios, on_finished=done, on_error=self._show_error)

    def _auto_size_columns(self) -> None:
        view = self._song_view
        view.resizeColumnsToContents()
        # Keep the title column generous; clamp the rest.
        widths = {0: 50, 1: 320, 2: 200, 3: 200, 4: 60, 5: 120, 6: 80, 7: 70}
        for col, w in widths.items():
            view.setColumnWidth(col, w)

    def _update_stats_label(self) -> None:
        def done(s):
            self._stats_label.setText(
                f"{s['songs']} songs · {s['artists']} artists · "
                f"{s['albums']} albums · {format_duration(s['duration'])}"
            )
        submit(library.stats, on_finished=done, on_error=self._show_error)

    def _on_search_changed(self, text: str) -> None:
        self._search_debounce_text = text
        if not hasattr(self, "_search_timer"):
            self._search_timer = QTimer(self)
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(
                lambda: self._load_library(self._search_debounce_text)
            )
        self._search_timer.start(180)

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------

    def _play_or_resume(self) -> None:
        if self._player is None:
            return
        if self._player.state is State.PAUSED:
            self._player.resume()
            return
        if self._tabs.currentIndex() == 1:
            self._play_selected_radio()
            return
        self._play_selected_song()

    def _play_selected_song(self, *_: object) -> None:
        if self._player is None:
            return
        rows = self._song_view.selectionModel().selectedRows()
        if not rows:
            song = self._song_model.song_at(0)
        else:
            song = self._song_model.song_at(rows[0].row())
        if song is None:
            return
        self._play_song(song)

    def _play_song(self, song: Song) -> None:
        if self._player is None:
            return
        if not Path(song.path).exists():
            self._statusbar_message(f"Missing file: {song.path}", warning=True)
            self._play_next()
            return
        try:
            self._player.play(song.path)
        except PlayerError as exc:
            self._show_error(str(exc))
            return
        self._current_song = song
        title = song.display_title
        artist = song.artist or "Unknown"
        self._now_playing.setText(f"♪  {artist} — {title}")
        self.setWindowTitle(f"PyMusic — {artist} — {title}")
        self._update_details(song)
        self._fetch_lyrics(song)
        # Highlight the row
        for row in range(self._song_model.rowCount()):
            s = self._song_model.song_at(row)
            if s and s.id == song.id:
                idx = self._song_model.index(row, 0)
                flags = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
                self._song_view.selectionModel().select(idx, flags)
                self._song_view.scrollTo(idx)
                break
        # Increment play count asynchronously
        submit(library.mark_played, song.id, on_error=self._show_error)

    def _play_selected_radio(self, *_: object) -> None:
        if self._player is None:
            return
        rows = self._radio_view.selectionModel().selectedRows()
        if not rows:
            return
        radio = self._radio_model.radio_at(rows[0].row())
        if radio is None:
            return
        try:
            self._player.play(radio.url)
        except PlayerError as exc:
            self._show_error(str(exc))
            return
        self._current_song = None
        self._now_playing.setText(f"📻  {radio.name or radio.url}")
        self.setWindowTitle(f"PyMusic — {radio.name or radio.url}")
        self._lyrics_view.clear()
        self._details_view.setPlainText(f"Streaming: {radio.url}\n{radio.genre or ''}")

    def _pause(self) -> None:
        if self._player is None:
            return
        self._player.pause()

    def _stop(self) -> None:
        if self._player is None:
            return
        self._player.stop()
        self._now_playing.setText("Stopped")
        self.setWindowTitle("PyMusic")
        self._position.setValue(0)
        self._time_label.setText("0:00")
        self._duration_label.setText("0:00")

    def _play_next(self) -> None:
        idx = self._current_index_in_view()
        count = self._song_model.rowCount()
        if count == 0:
            return
        if self._mode is PlayMode.RANDOM:
            new = random.randrange(count)
        elif self._mode is PlayMode.REPEAT_ONE and idx >= 0:
            new = idx
        else:
            new = (idx + 1) % count if idx >= 0 else 0
            if new == 0 and idx >= 0 and self._mode is not PlayMode.REPEAT_ALL and not self._btn_repeat.isChecked():
                # Reached end without repeat: stop.
                self._stop()
                return
        song = self._song_model.song_at(new)
        if song is not None:
            self._play_song(song)

    def _play_previous(self) -> None:
        idx = self._current_index_in_view()
        count = self._song_model.rowCount()
        if count == 0:
            return
        new = (idx - 1) % count if idx > 0 else count - 1
        song = self._song_model.song_at(new)
        if song is not None:
            self._play_song(song)

    def _current_index_in_view(self) -> int:
        if self._current_song is None:
            return -1
        for row in range(self._song_model.rowCount()):
            s = self._song_model.song_at(row)
            if s and s.id == self._current_song.id:
                return row
        return -1

    def _on_track_ended(self) -> None:
        # Called from VLC's thread — schedule on the UI thread.
        QTimer.singleShot(0, self._play_next)

    def _on_volume_changed(self, value: int) -> None:
        if self._player:
            self._player.volume = value

    def _on_shuffle_toggled(self, checked: bool) -> None:
        if checked:
            self._mode = PlayMode.RANDOM
            self._btn_repeat.setChecked(False)
        else:
            self._mode = PlayMode.NORMAL
        self._mode_label.setText(f"Mode: {self._mode.value}")

    def _on_repeat_toggled(self, checked: bool) -> None:
        if checked:
            self._mode = PlayMode.REPEAT_ALL
            self._btn_random.setChecked(False)
        else:
            self._mode = PlayMode.NORMAL
        self._mode_label.setText(f"Mode: {self._mode.value}")

    def _on_seek_released(self) -> None:
        if self._player is None:
            self._seek_in_progress = False
            return
        self._player.set_position(self._position.value() / 1000.0)
        self._seek_in_progress = False

    def _on_tick(self) -> None:
        if self._player is None or self._seek_in_progress:
            return
        if self._player.state is not State.PLAYING:
            return
        length = self._player.get_length()
        time = max(self._player.get_time(), 0.0)
        if length > 0:
            self._position.setValue(int(self._player.get_position() * 1000))
            self._duration_label.setText(format_duration(length))
        else:
            self._duration_label.setText("∞" if self._player.is_stream else "0:00")
        self._time_label.setText(format_duration(time))

    # ------------------------------------------------------------------
    # Details / lyrics
    # ------------------------------------------------------------------

    def _update_details(self, song: Song) -> None:
        text = (
            f"Title:  {song.display_title}\n"
            f"Artist: {song.artist or '-'}\n"
            f"Album:  {song.album or '-'}\n"
            f"Year:   {song.year or '-'}\n"
            f"Genre:  {song.genre or '-'}\n"
            f"Track:  {song.track_number or '-'}\n"
            f"Length: {format_duration(song.duration or 0)}\n"
            f"Plays:  {song.play_count or 0}\n"
            f"Path:   {song.path}\n"
        )
        self._details_view.setPlainText(text)

    def _fetch_lyrics(self, song: Song) -> None:
        self._lyrics_view.setPlaceholderText("Fetching lyrics…")
        self._lyrics_view.clear()
        artist = song.artist
        title = song.title or song.display_title

        def done(text: str) -> None:
            if self._current_song is None or self._current_song.id != song.id:
                return
            self._lyrics_view.setPlainText(text or "(no lyrics found)")
            self._lyrics_view.setPlaceholderText("Lyrics will appear here when a song starts playing.")

        submit(lyrics.get_lyrics, artist, title, on_finished=done, on_error=lambda e: done(""))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _scan_folder(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Choose music folder", str(Path.home()))
        if not path:
            return

        self._statusbar_message(f"Scanning {path}…")

        def progress(p):
            self.statusBar().showMessage(
                f"Scanning… {p.scanned} files, {p.added} added, {p.skipped} skipped"
            )

        def done(p):
            self.statusBar().showMessage(
                f"Scan finished: {p.added} new, {p.skipped} known.", 5000
            )
            self._load_library(self._search.text())

        submit(library.scan_directory, path,
               on_progress=progress, on_finished=done, on_error=self._show_error)

    def _clean_missing(self) -> None:
        def done(removed):
            QMessageBox.information(self, "Cleanup",
                                    f"Removed {removed} entries with missing files.")
            self._load_library(self._search.text())

        submit(library.remove_missing_files, on_finished=done, on_error=self._show_error)

    def _open_generate_dialog(self) -> None:
        dlg = GenerateListDialog(self)
        if dlg.exec() != dlg.Accepted:
            return
        query, dest, max_mb = dlg.values()

        self._statusbar_message(f"Copying songs to {dest}…")

        def done(result):
            mb = result.total_bytes / (1024 * 1024)
            QMessageBox.information(
                self, "Generate Playlist",
                f"Copied {result.copied} songs ({mb:.1f} MB).\n"
                f"Skipped: {result.skipped}\n"
                f"Errors: {len(result.errors)}",
            )

        submit(
            library.generate_playlist_to_dir,
            filter_query=query,
            destination=dest,
            max_size_mb=max_mb,
            on_finished=done,
            on_error=self._show_error,
        )

    def _add_radio(self) -> None:
        dlg = AddRadioDialog(self)
        if dlg.exec() != dlg.Accepted:
            return
        url, name, genre = dlg.values()

        def done(_):
            self._load_radios()
            self.statusBar().showMessage(f"Added radio {name or url}", 3000)

        submit(library.add_radio, url, name, genre, on_finished=done, on_error=self._show_error)

    def _remove_radio(self) -> None:
        rows = self._radio_view.selectionModel().selectedRows()
        if not rows:
            return
        radio = self._radio_model.radio_at(rows[0].row())
        if radio is None:
            return
        if QMessageBox.question(self, "Remove Radio", f"Remove {radio.name or radio.url}?") != QMessageBox.Yes:
            return

        def done(_):
            self._load_radios()

        submit(library.delete_radio, radio.id, on_finished=done, on_error=self._show_error)

    def _edit_selected_tags(self) -> None:
        rows = self._song_view.selectionModel().selectedRows()
        if not rows:
            return
        song = self._song_model.song_at(rows[0].row())
        if song is None:
            return
        tag = tags.TagInfo(
            title=song.title or song.display_title,
            artist=song.artist or "",
            album=song.album or "",
            year=song.year or "",
            genre=song.genre or "",
            track_number=song.track_number or 0,
        )
        dlg = TagEditorDialog(tag, file_path=song.path, parent=self)
        if dlg.exec() != dlg.Accepted:
            return
        new_tag = dlg.result_tag()

        def done(_):
            self._load_library(self._search.text())

        submit(library.update_song_tags, song.id, new_tag, on_finished=done, on_error=self._show_error)

    def _song_context_menu(self, pos) -> None:
        from PySide6.QtWidgets import QMenu

        index = self._song_view.indexAt(pos)
        if not index.isValid():
            return
        menu = QMenu(self)
        menu.addAction("Play", self._play_selected_song)
        menu.addAction("Edit Tags…", self._edit_selected_tags)
        menu.addSeparator()
        menu.addAction("Remove from library", self._delete_selected_songs)
        menu.exec(self._song_view.viewport().mapToGlobal(pos))

    def _delete_selected_songs(self) -> None:
        rows = self._song_view.selectionModel().selectedRows()
        if not rows:
            return
        if QMessageBox.question(
            self, "Remove",
            f"Remove {len(rows)} song(s) from the library? Files on disk are kept.",
        ) != QMessageBox.Yes:
            return
        ids = [self._song_model.song_at(r.row()).id for r in rows if self._song_model.song_at(r.row())]

        def work():
            for sid in ids:
                library.delete_song(sid)
            return len(ids)

        def done(_):
            self._load_library(self._search.text())

        submit(work, on_finished=done, on_error=self._show_error)

    def _show_about(self) -> None:
        from .. import __version__
        QMessageBox.about(
            self, "About PyMusic",
            f"<h3>PyMusic {__version__}</h3>"
            "<p>A modern music player and library manager.</p>"
            "<p>Built with PySide6, libVLC, mutagen and SQLAlchemy.</p>",
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _show_error(self, message: str) -> None:
        logger.error("UI error: %s", message)
        self.statusBar().showMessage(message, 6000)

    def _statusbar_message(self, message: str, *, warning: bool = False) -> None:
        self.statusBar().showMessage(message, 4000)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt override
        if self._player is not None:
            self._player.release()
        super().closeEvent(event)
