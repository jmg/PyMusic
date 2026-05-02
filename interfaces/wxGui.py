# -*- coding: utf-8 -*-
import io
import json
import os

import wx

from interfaces.wxWidgets.gui import wxGui
from interfaces.wxWidgets.logo import frmLogo
from interfaces.visualization import VisualizationDisplay
from interfaces.spectrum import SpectrumDisplay
from interfaces.wxFrmAddRadio import wxFrmAddRadio
from interfaces.wxFrmGenList import wxFrmGenList
from interfaces.Notify import SongNotify
from interfaces.wxGuiThreads import ShowPosThread, MoveBarThread

from logic.player_logic import PlayerLogic, PlayerDataLogic
from generics.multiprogramming import threaded


class MainWindow(wxGui):

    logic = PlayerLogic()
    data_logic = PlayerDataLogic()

    def __init__(self, parent):
        frmlogo = frmLogo(None)
        frmlogo.Show()

        wxGui.__init__(self, parent)

        self.dir_dialog = wx.DirDialog(
            None, "Choose a Music Folder", style=wx.DD_DEFAULT_STYLE, defaultPath="."
        )

        self.lbSongs.InsertColumn(0, "Path")
        self.lbSongs.InsertColumn(1, "Title")
        self.lbSongs.InsertColumn(2, "Artist")
        self.lbSongs.InsertColumn(3, "Album")
        self.lbSongs.InsertColumn(4, "Year")
        self.lbSongs.InsertColumn(5, "Id")
        self.lbSongs.InsertColumn(6, "Time")
        self.lbSongs.InsertColumn(7, "♪")

        self.lbRadios.InsertColumn(0, "Uri")
        self.lbRadios.InsertColumn(1, "Id")
        self.lbRadios.SetColumnWidth(1, 0)

        self.initialize_songs()
        self.initialize_radios()

        # autosize after the list is loaded
        self.lbSongs.SetColumnWidth(0, 0)
        self.lbSongs.SetColumnWidth(1, 300)
        self.lbSongs.SetColumnWidth(2, 150)
        self.lbSongs.SetColumnWidth(3, 150)
        self.lbSongs.SetColumnWidth(4, 70)
        self.lbSongs.SetColumnWidth(5, 0)
        self.lbSongs.SetColumnWidth(6, 70)
        self.lbSongs.SetColumnWidth(7, 50)
        self.lbRadios.SetColumnWidth(0, 0)
        self.lbRadios.SetColumnWidth(0, 400)

        frmlogo.Hide()

        visual_sizer = self.pnVisual.GetSizer()
        self.visualization = VisualizationDisplay(self.pnVisual, wx.ID_ANY, visual_sizer)
        visual_sizer.Add(self.visualization, 1, wx.EXPAND | wx.ALL, 0)
        self.pnVisual.Layout()

        self._setup_buttons()
        self._setup_menu_extras()
        self._setup_song_context_menu()
        self._setup_seek_bar()
        self._setup_spectrum()
        self._setup_time_label()
        self._setup_cover_tab()
        self._setup_repeat_button()
        self._setup_accelerators()
        self._setup_drop_target()
        self._setup_lyrics_sync()
        self._setup_tray_icon()
        self._setup_mpris()
        self._setup_drag_reorder()
        self._setup_album_view()
        self._setup_folder_view()
        self._setup_karaoke()
        self._setup_plugins()
        self._setup_discord_rpc()
        self._setup_sash()
        self._apply_theme()
        self._load_state()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    # ------------------------------------------------------------------
    # UI polish
    # ------------------------------------------------------------------
    def _setup_buttons(self):
        # Unicode media glyphs as button labels.
        self.btPlay.SetLabel("▶  Play")
        self.btStop.SetLabel("■  Stop")
        self.btPrevious.SetLabel("⏮  Prev")
        self.btNext.SetLabel("⏭  Next")
        self.tgRandom.SetLabel("\U0001F500  Random")

        # Play and Pause are merged: hide btPause and let btPlay act as a
        # tri-state Play/Pause/Resume toggle.
        try:
            sz = self.btPause.GetContainingSizer()
            sz.Detach(self.btPause)
            self.btPause.Hide()
            sz.Layout()
        except Exception:
            pass
        self.btPlay.Unbind(wx.EVT_BUTTON)
        self.btPlay.Bind(wx.EVT_BUTTON, self._on_play_pause_click)

        # Song title: read-only display, larger font.
        self.tbSong.SetEditable(False)
        try:
            self.tbSong.SetWindowStyleFlag(self.tbSong.GetWindowStyleFlag() | wx.TE_READONLY)
        except Exception:
            pass
        try:
            f = self.tbSong.GetFont()
            f.SetPointSize(f.GetPointSize() + 2)
            f.SetWeight(wx.FONTWEIGHT_BOLD)
            self.tbSong.SetFont(f)
        except Exception:
            pass

        # Remove the empty TextCtrl that was sitting next to the song title.
        try:
            sz = self.tbTime.GetContainingSizer()
            sz.Detach(self.tbTime)
            self.tbTime.Hide()
            sz.Layout()
        except Exception:
            pass

        try:
            font = self.btPlay.GetFont()
            font.SetPointSize(font.GetPointSize() + 1)
            for btn in (self.btPlay, self.btStop, self.btPause,
                        self.btPrevious, self.btNext, self.tgRandom):
                btn.SetFont(font)
        except Exception:
            pass

        # Fix typo'd binding in generated base class.
        self.btPrevious.Bind(wx.EVT_BUTTON, self.btPrevious_click)

    def _setup_menu_extras(self):
        # File menu
        self.itAddSongs = wx.MenuItem(
            self.mnFile, wx.ID_ANY, "Add Songs\tCtrl+O",
            "Add individual audio files", wx.ITEM_NORMAL,
        )
        self.mnFile.Insert(1, self.itAddSongs)
        self.Bind(wx.EVT_MENU, self.add_songs_individual, id=self.itAddSongs.GetId())

        self.itImportM3U = self.mnFile.Append(wx.ID_ANY, "Import M3U Playlist...")
        self.itExportM3U = self.mnFile.Append(wx.ID_ANY, "Export Playlist as M3U...")
        self.Bind(wx.EVT_MENU, self._import_m3u, self.itImportM3U)
        self.Bind(wx.EVT_MENU, self._export_m3u, self.itExportM3U)

        # View menu
        self.itAlwaysOnTop = self.mnView.AppendCheckItem(
            wx.ID_ANY, "Always On Top\tCtrl+T", "",
        )
        self.Bind(wx.EVT_MENU, self._toggle_always_on_top, self.itAlwaysOnTop)

        self.itMiniPlayer = self.mnView.AppendCheckItem(
            wx.ID_ANY, "Mini Player\tCtrl+M", "",
        )
        self.Bind(wx.EVT_MENU, self._toggle_mini_player, self.itMiniPlayer)

        self.itFullscreenVis = self.mnView.Append(
            wx.ID_ANY, "Fullscreen Visualization\tF11", "",
        )
        self.Bind(wx.EVT_MENU, self._toggle_fullscreen_vis, self.itFullscreenVis)

        # Smart playlists submenu
        self.mnSmart = wx.Menu()
        for label, kind in (
            ("Recently Added", "recent"),
            ("Most Played", "most_played"),
            ("Never Played", "never_played"),
            ("Recently Played", "last_played"),
        ):
            it = self.mnSmart.Append(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, k=kind: self._load_smart(k), it)
        it_all = self.mnSmart.Append(wx.ID_ANY, "All Songs")
        self.Bind(wx.EVT_MENU, lambda e: self._load_smart("all"), it_all)
        self.mnView.AppendSeparator()
        self.mnView.AppendSubMenu(self.mnSmart, "Smart Playlists")

        # Tools menu
        self.mnTools = wx.Menu()
        it_orphan = self.mnTools.Append(wx.ID_ANY, "Find Orphan Files...")
        self.Bind(wx.EVT_MENU, self._find_orphans_dialog, it_orphan)
        it_token = self.mnTools.Append(wx.ID_ANY, "Set ListenBrainz Token...")
        self.Bind(wx.EVT_MENU, self._set_listenbrainz_token, it_token)
        self.mnBar.Append(self.mnTools, "Tools")

        # Karaoke under View
        it_karaoke = self.mnView.Append(wx.ID_ANY, "Karaoke\tCtrl+K")
        self.Bind(wx.EVT_MENU, lambda e: self._open_karaoke(), it_karaoke)

        # Audio menu
        self.mnAudio = wx.Menu()
        it_eq = self.mnAudio.Append(wx.ID_ANY, "Equalizer...")
        self.Bind(wx.EVT_MENU, self._open_equalizer, it_eq)

        self.itReplayGain = self.mnAudio.AppendCheckItem(
            wx.ID_ANY, "Apply ReplayGain", "",
        )
        self.itReplayGain.Check(True)
        self.Bind(wx.EVT_MENU, self._toggle_replaygain, self.itReplayGain)

        # Crossfade submenu
        mnCrossfade = wx.Menu()
        for label, secs in [("Off", 0), ("1 s", 1), ("2 s", 2), ("3 s", 3),
                            ("5 s", 5), ("8 s", 8)]:
            it = mnCrossfade.AppendRadioItem(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, s=secs: self._set_crossfade(s), it)
            if secs == 0:
                it.Check(True)
        self.mnAudio.AppendSubMenu(mnCrossfade, "Crossfade")

        # Sleep timer submenu
        mnSleep = wx.Menu()
        for label, mins in [("Off", 0), ("15 min", 15), ("30 min", 30),
                            ("45 min", 45), ("1 h", 60), ("2 h", 120)]:
            it = mnSleep.AppendRadioItem(wx.ID_ANY, label)
            self.Bind(wx.EVT_MENU, lambda e, m=mins: self._set_sleep_timer(m), it)
            if mins == 0:
                it.Check(True)
        self.mnAudio.AppendSubMenu(mnSleep, "Sleep Timer")

        self.mnBar.Append(self.mnAudio, "Audio")

    # ------------------------------------------------------------------
    # Draggable sash between the left and right panes
    # ------------------------------------------------------------------
    def _setup_sash(self):
        sizer = self.GetSizer()
        self.sash = _SashPanel(self, self._on_sash_drag)
        sizer.Insert(1, self.sash, 0, wx.EXPAND, 0)
        sizer.Layout()

    def _on_sash_drag(self, screen_x):
        rect = self.GetScreenRect()
        rel = screen_x - rect.x
        rel = max(20, min(rect.width - 20, rel))
        right = max(20, rect.width - rel - self.sash.GetSize().GetWidth())
        items = self.GetSizer().GetChildren()
        items[0].SetProportion(int(rel))
        items[2].SetProportion(int(right))
        self.GetSizer().Layout()
        try:
            self.visualization.size_dirty = True
            self.visualization.Refresh()
        except Exception:
            pass

    def _set_sash_ratio(self, ratio):
        ratio = max(0.02, min(0.98, float(ratio)))
        items = self.GetSizer().GetChildren()
        if len(items) < 3:
            return
        items[0].SetProportion(int(ratio * 1000))
        items[2].SetProportion(int((1 - ratio) * 1000))
        self.GetSizer().Layout()
        try:
            self.visualization.size_dirty = True
            self.visualization.Refresh()
        except Exception:
            pass

    def _get_sash_ratio(self):
        items = self.GetSizer().GetChildren()
        if len(items) < 3:
            return 0.6
        a = items[0].GetProportion()
        b = items[2].GetProportion()
        if a + b == 0:
            return 0.6
        return a / (a + b)

    def _setup_song_context_menu(self):
        self.lbSongs.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_songs_right_click)
        self.lbSongs.Bind(wx.EVT_KEY_DOWN, self._on_songs_key_down)

    def _setup_seek_bar(self):
        self.slPosition.Bind(wx.EVT_SCROLL_THUMBRELEASE, self._on_seek)
        self.slPosition.Bind(wx.EVT_SCROLL_CHANGED, self._on_seek)

    def _setup_spectrum(self):
        self.spectrum = SpectrumDisplay(self.pnPlayList, lambda: self.logic.player)
        self.pnPlayList.GetSizer().Add(self.spectrum, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
        self.pnPlayList.Layout()

    STATE_PATH = os.path.expanduser("~/.config/pymusic/state.json")

    REPEAT_MODES = ("off", "all", "one")
    REPEAT_GLYPHS = {"off": "↻ off", "all": "🔁 all", "one": "🔂 one"}

    def _setup_cover_tab(self):
        self.pnCover = wx.Panel(self.ntRight, wx.ID_ANY)
        self.pnCover.SetBackgroundColour(wx.Colour(15, 15, 25))
        sz = wx.BoxSizer(wx.VERTICAL)
        self.bmCover = wx.StaticBitmap(self.pnCover)
        sz.Add(self.bmCover, 1, wx.ALIGN_CENTER | wx.ALL, 12)
        self.pnCover.SetSizer(sz)
        self.ntRight.InsertPage(0, self.pnCover, "Cover", select=False)

    def _setup_repeat_button(self):
        self._repeat = "off"
        self.btRepeat = wx.Button(self, label=self.REPEAT_GLYPHS["off"])
        font = self.btRepeat.GetFont()
        font.SetPointSize(font.GetPointSize() + 1)
        self.btRepeat.SetFont(font)
        self.btRepeat.Bind(wx.EVT_BUTTON, self._on_repeat_click)

        # Add next to Random in the same row.
        sz = self.tgRandom.GetContainingSizer()
        sz.Add(self.btRepeat, 1, wx.ALL, 5)
        sz.Layout()

    def _on_repeat_click(self, event):
        idx = self.REPEAT_MODES.index(self._repeat)
        self._repeat = self.REPEAT_MODES[(idx + 1) % len(self.REPEAT_MODES)]
        self.btRepeat.SetLabel(self.REPEAT_GLYPHS[self._repeat])

    def _setup_accelerators(self):
        space_id = wx.NewIdRef()
        next_id = wx.NewIdRef()
        prev_id = wx.NewIdRef()
        volup_id = wx.NewIdRef()
        voldown_id = wx.NewIdRef()
        seekfwd_id = wx.NewIdRef()
        seekbk_id = wx.NewIdRef()
        find_id = wx.NewIdRef()

        self.Bind(wx.EVT_MENU, lambda e: self._kbd_play_pause(), id=space_id)
        self.Bind(wx.EVT_MENU, lambda e: self.next(), id=next_id)
        self.Bind(wx.EVT_MENU, lambda e: self.previous(), id=prev_id)
        self.Bind(wx.EVT_MENU, lambda e: self._kbd_volume(+5), id=volup_id)
        self.Bind(wx.EVT_MENU, lambda e: self._kbd_volume(-5), id=voldown_id)
        self.Bind(wx.EVT_MENU, lambda e: self._kbd_seek(+5), id=seekfwd_id)
        self.Bind(wx.EVT_MENU, lambda e: self._kbd_seek(-5), id=seekbk_id)
        self.Bind(wx.EVT_MENU, lambda e: self.tbFinder.SetFocus(), id=find_id)

        accel = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_SPACE, space_id),
            (wx.ACCEL_CTRL,   wx.WXK_RIGHT, next_id),
            (wx.ACCEL_CTRL,   wx.WXK_LEFT,  prev_id),
            (wx.ACCEL_NORMAL, wx.WXK_UP,    volup_id),
            (wx.ACCEL_NORMAL, wx.WXK_DOWN,  voldown_id),
            (wx.ACCEL_NORMAL, wx.WXK_RIGHT, seekfwd_id),
            (wx.ACCEL_NORMAL, wx.WXK_LEFT,  seekbk_id),
            (wx.ACCEL_CTRL,   ord('F'),     find_id),
        ])
        self.SetAcceleratorTable(accel)

    def _kbd_play_pause(self):
        try:
            if self.logic.is_playing():
                self.pause(None)
            elif self.logic.player.isPaused():
                self.resume(None)
            else:
                self.play(None)
        except Exception:
            self.play(None)

    def _kbd_volume(self, delta):
        v = max(0, min(100, self.slVolume.GetValue() + delta))
        self.slVolume.SetValue(v)
        self.logic.change_volume(v / 100.0)

    def _kbd_seek(self, delta_sec):
        try:
            cur_ns = self.logic.player.getSeekedPosition()
            if cur_ns is None:
                return
            new_ns = max(0, cur_ns + delta_sec * 1_000_000_000)
            self.logic.player.seek(new_ns)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Theme / overall UI polish
    # ------------------------------------------------------------------
    BG_DARK = wx.Colour(24, 24, 36)
    BG_PANEL = wx.Colour(32, 32, 48)
    BG_LIST = wx.Colour(28, 28, 42)
    BG_LIST_ALT = wx.Colour(36, 36, 54)
    FG_TEXT = wx.Colour(230, 230, 240)
    FG_DIM = wx.Colour(170, 170, 200)
    ACCENT = wx.Colour(126, 87, 194)
    ACCENT_BG = wx.Colour(70, 50, 110)

    def _apply_theme(self):
        # Frame + main panels
        self.SetBackgroundColour(self.BG_DARK)
        for w in (self.pnPlayList, self.pnRadios, self.m_panel3, self.pnVisual,
                  getattr(self, "pnCover", None), getattr(self, "albumView", None)):
            if w:
                w.SetBackgroundColour(self.BG_PANEL)

        # Song title + search styling
        self.tbSong.SetBackgroundColour(self.BG_PANEL)
        self.tbSong.SetForegroundColour(self.FG_TEXT)
        self.tbFinder.SetBackgroundColour(self.BG_LIST)
        self.tbFinder.SetForegroundColour(self.FG_TEXT)
        try:
            self.tbFinder.SetHint("Search by title, artist, album...")
        except Exception:
            pass

        # Lyrics
        self.tbLyrics.SetBackgroundColour(self.BG_PANEL)
        self.tbLyrics.SetForegroundColour(self.FG_TEXT)

        # Position label
        try:
            self.lbTimePos.SetForegroundColour(self.FG_TEXT)
        except Exception:
            pass

        # ListCtrls: dark + monospace-ish row spacing
        for lst in (self.lbSongs, self.lbRadios):
            lst.SetBackgroundColour(self.BG_LIST)
            lst.SetForegroundColour(self.FG_TEXT)
            try:
                f = lst.GetFont()
                f.SetPointSize(f.GetPointSize() + 1)
                lst.SetFont(f)
            except Exception:
                pass

        # Rename columns to friendlier labels.
        try:
            self.lbSongs.SetColumn(1, wx.ListItem())  # placeholder
        except Exception:
            pass
        # Use SetColumnsOrder/SetItem for headers
        try:
            for col, header in [(1, "Title"), (2, "Artist"), (3, "Album"), (4, "Year")]:
                item = self.lbSongs.GetColumn(col)
                item.SetText(header)
                self.lbSongs.SetColumn(col, item)
        except Exception:
            pass

        # Default frame size
        self.SetSize(wx.Size(1280, 760))
        self.Centre()

        self.Refresh()

    # ------------------------------------------------------------------
    # Drag-reorder rows in the songs list
    # ------------------------------------------------------------------
    def _setup_drag_reorder(self):
        self._drag_indices = []
        self.lbSongs.Bind(wx.EVT_LIST_BEGIN_DRAG, self._on_drag_begin)

    def _on_drag_begin(self, event):
        self._drag_indices = []
        idx = self.lbSongs.GetFirstSelected()
        while idx != -1:
            self._drag_indices.append(idx)
            idx = self.lbSongs.GetNextSelected(idx)
        if not self._drag_indices:
            return
        self.lbSongs.Bind(wx.EVT_LEFT_UP, self._on_drag_drop)
        try:
            self.lbSongs.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        except Exception:
            pass

    def _on_drag_drop(self, event):
        try:
            self.lbSongs.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        except Exception:
            pass
        self.lbSongs.Unbind(wx.EVT_LEFT_UP)

        if not self._drag_indices:
            event.Skip()
            return

        target, _flags = self.lbSongs.HitTest(event.GetPosition())
        if target == wx.NOT_FOUND or target < 0:
            target = self.lbSongs.GetItemCount()

        self._reorder_rows(self._drag_indices, target)
        self._drag_indices = []

    def _reorder_rows(self, source_indices, target):
        # Snapshot the dragged rows (all 6 columns).
        rows = []
        for i in source_indices:
            row = [self.lbSongs.GetItem(i, c).GetText() for c in range(6)]
            rows.append(row)

        # Adjust target while deleting from the bottom.
        adj_target = target
        for i in sorted(source_indices, reverse=True):
            self.lbSongs.DeleteItem(i)
            if i < adj_target:
                adj_target -= 1

        adj_target = max(0, min(adj_target, self.lbSongs.GetItemCount()))
        for offset, row in enumerate(rows):
            idx = self.lbSongs.InsertItem(adj_target + offset, row[0])
            for c in range(1, 6):
                self.lbSongs.SetItem(idx, c, row[c])
            self.lbSongs.SetItemState(idx, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

    # ------------------------------------------------------------------
    # Album grid view
    # ------------------------------------------------------------------
    def _setup_album_view(self):
        from interfaces.album_view import AlbumView
        self.albumView = AlbumView(self.ntDown, on_album_click=self._on_album_clicked)
        self.ntDown.AddPage(self.albumView, "Albums", select=False)
        wx.CallAfter(self._refresh_albums)

    def _setup_folder_view(self):
        self.dirCtrl = wx.GenericDirCtrl(
            self.ntDown, dir=os.path.expanduser("~"),
            filter="Audio files|*.mp3;*.flac;*.ogg;*.opus;*.m4a;*.wav;*.wma;"
                   "*.aac;*.ape;*.alac;*.aiff|All|*.*",
        )
        self.ntDown.AddPage(self.dirCtrl, "Files", select=False)
        try:
            tree = self.dirCtrl.GetTreeCtrl()
            tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_dir_item_activated)
            tree.Bind(wx.EVT_RIGHT_DOWN, self._on_dir_right_click)
        except Exception:
            pass

    def _on_dir_item_activated(self, event):
        path = self.dirCtrl.GetFilePath()
        if path and os.path.isfile(path):
            self._add_files_worker([path])
        elif path and os.path.isdir(path):
            self.dir_worker(path)

    def _on_dir_right_click(self, event):
        path = self.dirCtrl.GetFilePath() or self.dirCtrl.GetPath()
        if not path:
            event.Skip()
            return
        menu = wx.Menu()
        if os.path.isdir(path):
            it = menu.Append(wx.ID_ANY, f"Add directory: {os.path.basename(path)}")
            self.Bind(wx.EVT_MENU, lambda e: self.dir_worker(path), it)
        else:
            it = menu.Append(wx.ID_ANY, f"Add file: {os.path.basename(path)}")
            self.Bind(wx.EVT_MENU, lambda e: self._add_files_worker([path]), it)
        self.dirCtrl.PopupMenu(menu)
        menu.Destroy()

    def _setup_karaoke(self):
        self._karaoke_frame = None

    def _open_karaoke(self):
        if self._karaoke_frame:
            try:
                self._karaoke_frame.Close()
            except Exception:
                pass
            self._karaoke_frame = None
            return
        from interfaces.karaoke import KaraokeFrame
        self._karaoke_frame = KaraokeFrame(self)
        self._karaoke_frame.Show()

    def _setup_plugins(self):
        from interfaces.plugins import PluginManager
        self.plugins = PluginManager(self)
        self.plugins.load_all()

    def _setup_discord_rpc(self):
        try:
            from interfaces.discord_rpc import DiscordPresence
            self._discord = DiscordPresence()
            self._discord.start()
        except Exception:
            self._discord = None

    def _refresh_albums(self):
        try:
            songs = self.data_logic.fetch_all_songs()
            self.albumView.populate(songs)
        except Exception:
            pass

    def _on_album_clicked(self, artist, album):
        if artist == "__ALL__" and album == "__ALL__":
            songs = self.data_logic.fetch_all_songs()
        else:
            songs = self.data_logic.find(album)
            if artist:
                songs = [s for s in songs if (s.artist or "") == artist]
        self.lbSongs.DeleteAllItems()
        self.list_load(songs)
        # Switch to PlayList tab so the user sees the filtered list.
        for i in range(self.ntDown.GetPageCount()):
            if self.ntDown.GetPageText(i) == "PlayList":
                self.ntDown.SetSelection(i)
                break

    # ------------------------------------------------------------------
    # Drag & drop
    # ------------------------------------------------------------------
    def _setup_drop_target(self):
        self.SetDropTarget(_AudioDropTarget(self))

    def _on_files_dropped(self, paths):
        files = []
        dirs = []
        for p in paths:
            if os.path.isdir(p):
                dirs.append(p)
            elif os.path.isfile(p):
                files.append(p)
        if files:
            self._add_files_worker(files)
        for d in dirs:
            self.dir_worker(d)

    # ------------------------------------------------------------------
    # Synced lyrics highlight
    # ------------------------------------------------------------------
    def _set_tab_availability(self, panel, base_label, available):
        """Insert/remove the page so unavailable tabs disappear entirely.

        wx GTK doesn't support gray/disabled individual tabs, so we
        physically remove the page when its content isn't available
        (web-style: tab not visible) and re-insert it when it is.
        """
        # Track the default position to restore later.
        if panel not in self._tab_defaults:
            for i in range(self.ntRight.GetPageCount()):
                if self.ntRight.GetPage(i) is panel:
                    self._tab_defaults[panel] = (i, base_label)
                    break
            else:
                # Panel currently not in the notebook; nothing tracked yet.
                return

        default_idx, _ = self._tab_defaults[panel]

        # Find current index, if any.
        current_idx = -1
        for i in range(self.ntRight.GetPageCount()):
            if self.ntRight.GetPage(i) is panel:
                current_idx = i
                break

        if available and current_idx == -1:
            # Re-insert at its original position (clamped).
            idx = min(default_idx, self.ntRight.GetPageCount())
            try:
                panel.Show()
                self.ntRight.InsertPage(idx, panel, base_label, select=False)
            except Exception:
                pass
        elif not available and current_idx != -1:
            # If user is on it, switch first.
            if self.ntRight.GetSelection() == current_idx:
                for j in range(self.ntRight.GetPageCount()):
                    if j != current_idx:
                        self.ntRight.SetSelection(j)
                        break
            try:
                self.ntRight.RemovePage(current_idx)
                panel.Hide()
            except Exception:
                pass

    def _setup_lyrics_sync(self):
        self._tab_defaults = {}

        # Existing lyrics-sync state below.
        self._synced_lyrics = []
        self._synced_offsets = []
        self._synced_last_idx = -1

        self._lyrics_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_lyrics_tick, self._lyrics_timer)

    def _set_lyrics(self, text, synced):
        self.tbLyrics.SetValue(text or "")
        self._synced_lyrics = list(synced) if synced else []
        self._synced_offsets = []
        self._synced_last_idx = -1

        has = bool(text) and text != "No se encontraron letras"
        self._set_tab_availability(self.m_panel3, "Lyrics", has)

        if self._synced_lyrics:
            # Build display text from synced lines (preserves order/spacing).
            buf = []
            offsets = []
            running = 0
            for _t, line in self._synced_lyrics:
                offsets.append(running)
                buf.append(line)
                running += len(line) + 1  # +1 for newline
            self.tbLyrics.SetValue("\n".join(buf))
            self._synced_offsets = offsets
            if not self._lyrics_timer.IsRunning():
                self._lyrics_timer.Start(400)
        else:
            if self._lyrics_timer.IsRunning():
                self._lyrics_timer.Stop()

    def _on_lyrics_tick(self, event):
        if not self._synced_lyrics:
            return
        try:
            pos_ns = self.logic.player.getSeekedPosition()
        except Exception:
            return
        if pos_ns is None:
            return
        pos_s = pos_ns / 1_000_000_000

        # Find current line: last entry whose timestamp <= pos.
        idx = -1
        for i, (t, _line) in enumerate(self._synced_lyrics):
            if t <= pos_s:
                idx = i
            else:
                break

        if idx < 0 or idx == self._synced_last_idx:
            return
        self._synced_last_idx = idx

        offset = self._synced_offsets[idx]
        try:
            self.tbLyrics.ShowPosition(offset)
            line_end = offset + len(self._synced_lyrics[idx][1])
            self.tbLyrics.SetSelection(offset, line_end)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Tray icon
    # ------------------------------------------------------------------
    def _setup_tray_icon(self):
        try:
            import wx.adv
            self._tray = _PyMusicTrayIcon(self)
        except Exception:
            self._tray = None

    # ------------------------------------------------------------------
    # MPRIS (Linux media bus integration)
    # ------------------------------------------------------------------
    def _setup_mpris(self):
        try:
            from interfaces.mpris import MprisServer
            self._mpris = MprisServer(self)
            self._mpris.start()
        except Exception as e:
            self._mpris = None

    def _mpris_update(self):
        if self._mpris:
            try:
                self._mpris.notify_status()
            except Exception:
                pass

    # ------------------------------------------------------------------
    # State persistence
    # ------------------------------------------------------------------
    def _load_state(self):
        try:
            with open(self.STATE_PATH, "r", encoding="utf-8") as f:
                state = json.load(f)
        except (OSError, ValueError):
            return

        vol = state.get("volume")
        if isinstance(vol, (int, float)):
            self.slVolume.SetValue(int(vol))
            self.logic.change_volume(vol / 100.0)
        repeat = state.get("repeat")
        if repeat in self.REPEAT_MODES:
            self._repeat = repeat
            self.btRepeat.SetLabel(self.REPEAT_GLYPHS[repeat])
        last_dir = state.get("last_dir")
        if last_dir and os.path.isdir(last_dir):
            try:
                self.dir_dialog.SetPath(last_dir)
            except Exception:
                pass

        last_path = state.get("last_path")
        if last_path:
            wx.CallAfter(self._scroll_to_path, last_path)

        token = state.get("listenbrainz_token")
        if token:
            self._lb_token = token

        gains = state.get("eq_gains")
        if isinstance(gains, list) and len(gains) == 10:
            self._apply_equalizer(gains)

        rg = state.get("rg_enabled")
        if isinstance(rg, bool):
            self._rg_enabled = rg
            try:
                self.itReplayGain.Check(rg)
            except Exception:
                pass

        cf = state.get("crossfade_secs")
        if isinstance(cf, int) and cf > 0:
            self._set_crossfade(cf)

        if state.get("always_on_top"):
            self.SetWindowStyle(self.GetWindowStyle() | wx.STAY_ON_TOP)
            try:
                self.itAlwaysOnTop.Check(True)
            except Exception:
                pass

        ratio = state.get("sash_ratio")
        if isinstance(ratio, (int, float)):
            self._set_sash_ratio(ratio)

        size = state.get("window_size")
        if isinstance(size, list) and len(size) == 2:
            try:
                self.SetSize(wx.Size(int(size[0]), int(size[1])))
            except Exception:
                pass
        pos = state.get("window_pos")
        if isinstance(pos, list) and len(pos) == 2:
            try:
                self.SetPosition(wx.Point(int(pos[0]), int(pos[1])))
            except Exception:
                pass

        if state.get("random"):
            self.logic.set_mode(self.logic.modes.RANDOM_PLAY)
            try:
                self.tgRandom.SetValue(True)
            except Exception:
                pass

        widths = state.get("column_widths")
        if isinstance(widths, list):
            for i, w in enumerate(widths):
                if i < self.lbSongs.GetColumnCount():
                    try:
                        self.lbSongs.SetColumnWidth(i, int(w))
                    except Exception:
                        pass

        nd = state.get("ntDown_tab")
        if isinstance(nd, int) and 0 <= nd < self.ntDown.GetPageCount():
            try:
                self.ntDown.SetSelection(nd)
            except Exception:
                pass
        nr = state.get("ntRight_tab")
        if isinstance(nr, int) and 0 <= nr < self.ntRight.GetPageCount():
            try:
                self.ntRight.SetSelection(nr)
            except Exception:
                pass

        fsz = state.get("lyrics_font_size")
        if isinstance(fsz, int) and 6 <= fsz <= 40:
            try:
                f = self.tbLyrics.GetFont()
                f.SetPointSize(fsz)
                self.tbLyrics.SetFont(f)
            except Exception:
                pass

    def _scroll_to_path(self, target):
        for i in range(self.lbSongs.GetItemCount()):
            if self.lbSongs.GetItem(i, 0).GetText() == target:
                self.lbSongs.SetItemState(i, wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                                          wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)
                self.lbSongs.EnsureVisible(i)
                return

    def _save_state(self):
        state = {
            "volume": self.slVolume.GetValue(),
            "repeat": self._repeat,
            "last_dir": self.dir_dialog.GetPath() if hasattr(self, "dir_dialog") else None,
            "last_path": getattr(self, "_current_path", None),
            "listenbrainz_token": getattr(self, "_lb_token", None),
            "eq_gains": getattr(self, "_eq_gains", None),
            "rg_enabled": getattr(self, "_rg_enabled", True),
            "crossfade_secs": getattr(self, "_crossfade_secs", 0),
            "always_on_top": bool(self.GetWindowStyle() & wx.STAY_ON_TOP),
            "sash_ratio": self._get_sash_ratio(),
            "window_size": list(self.GetSize()),
            "window_pos": list(self.GetPosition()),
            "random": (
                self.logic.get_mode() == self.logic.modes.RANDOM_PLAY
            ),
            "ntDown_tab": self.ntDown.GetSelection(),
            "ntRight_tab": self.ntRight.GetSelection(),
            "column_widths": [
                self.lbSongs.GetColumnWidth(c)
                for c in range(self.lbSongs.GetColumnCount())
            ],
            "lyrics_font_size": self.tbLyrics.GetFont().GetPointSize(),
        }
        try:
            os.makedirs(os.path.dirname(self.STATE_PATH), exist_ok=True)
            with open(self.STATE_PATH, "w", encoding="utf-8") as f:
                json.dump(state, f)
        except OSError:
            pass


    def _setup_time_label(self):
        # Move time display next to the seek bar.
        parent_sizer = self.slPosition.GetContainingSizer()
        parent_sizer.Detach(self.slPosition)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.slPosition, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.lbTimePos = wx.StaticText(self, label="00:00 / 00:00")
        font = self.lbTimePos.GetFont()
        font.SetPointSize(font.GetPointSize() + 1)
        self.lbTimePos.SetFont(font)
        row.Add(self.lbTimePos, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 10)
        parent_sizer.Add(row, 0, wx.EXPAND)
        parent_sizer.Layout()
        self.Layout()

    # ------------------------------------------------------------------
    # New handlers
    # ------------------------------------------------------------------
    def _on_seek(self, event):
        try:
            ns = self.slPosition.GetValue() * 1000
            self.logic.player.seek(ns)
        except Exception:
            pass
        event.Skip()

    def _on_songs_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            self._delete_selected_songs()
        else:
            event.Skip()

    def _on_songs_right_click(self, event):
        menu = wx.Menu()
        play_item = menu.Append(wx.ID_ANY, "▶  Play")
        edit_item = menu.Append(wx.ID_ANY, "✎  Edit tags...")
        menu.AppendSeparator()
        del_item = menu.Append(wx.ID_ANY, "⌫  Delete\tDel")

        self.Bind(wx.EVT_MENU, lambda e: self.play(e), play_item)
        self.Bind(wx.EVT_MENU, lambda e: self._edit_selected_tags(), edit_item)
        self.Bind(wx.EVT_MENU, lambda e: self._delete_selected_songs(), del_item)

        self.lbSongs.PopupMenu(menu)
        menu.Destroy()

    # ------------------------------------------------------------------
    # Tag editor
    # ------------------------------------------------------------------
    def _edit_selected_tags(self):
        idx = self.lbSongs.GetFirstSelected()
        if idx < 0:
            return
        try:
            sid = int(self.lbSongs.GetItem(idx, 5).GetText())
        except ValueError:
            return
        path = self.lbSongs.GetItem(idx, 0).GetText()

        def _clean(s):
            return "" if s in (None, "—") else s
        cur = {
            "title": _clean(self.lbSongs.GetItem(idx, 1).GetText()),
            "artist": _clean(self.lbSongs.GetItem(idx, 2).GetText()),
            "album": _clean(self.lbSongs.GetItem(idx, 3).GetText()),
            "year": _clean(self.lbSongs.GetItem(idx, 4).GetText()),
        }
        dlg = _TagEditorDialog(self, cur)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        new = dlg.values()
        dlg.Destroy()

        self.data_logic.update_song_tags(sid, **new)
        self._write_tags_to_file(path, new)

        for col, key in [(1, "title"), (2, "artist"), (3, "album"), (4, "year")]:
            v = new.get(key) or "—"
            self.lbSongs.SetItem(idx, col, v)

    @staticmethod
    def _write_tags_to_file(path, fields):
        try:
            from mutagen.easyid3 import EasyID3
            from mutagen import File as MF
        except ImportError:
            return
        try:
            audio = MF(path, easy=True)
            if audio is None:
                return
            mapping = {"title": "title", "artist": "artist",
                       "album": "album", "year": "date"}
            for k, easy_key in mapping.items():
                v = fields.get(k)
                if v is None:
                    continue
                try:
                    audio[easy_key] = str(v)
                except Exception:
                    pass
            audio.save()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Smart playlists
    # ------------------------------------------------------------------
    def _load_smart(self, kind):
        if kind == "all":
            songs = self.data_logic.fetch_all_songs()
        else:
            songs = self.data_logic.smart_filter(kind)
        self.list_load(songs)
        for i in range(self.ntDown.GetPageCount()):
            if self.ntDown.GetPageText(i) == "PlayList":
                self.ntDown.SetSelection(i)
                break

    # ------------------------------------------------------------------
    # M3U import / export
    # ------------------------------------------------------------------
    def _export_m3u(self, event):
        with wx.FileDialog(self, "Export playlist", wildcard="M3U|*.m3u",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            target = dlg.GetPath()
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for i in range(self.lbSongs.GetItemCount()):
                    path = self.lbSongs.GetItem(i, 0).GetText()
                    title = self.lbSongs.GetItem(i, 1).GetText()
                    artist = self.lbSongs.GetItem(i, 2).GetText()
                    dur = self.lbSongs.GetItem(i, 6).GetText()
                    secs = self._parse_dur(dur)
                    f.write(f"#EXTINF:{secs},{artist} - {title}\n{path}\n")
        except OSError as e:
            wx.MessageBox(f"Could not write playlist: {e}", "Error",
                          wx.ICON_ERROR)

    def _import_m3u(self, event):
        with wx.FileDialog(self, "Import playlist",
                           wildcard="M3U|*.m3u;*.m3u8",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            source = dlg.GetPath()
        try:
            with open(source, "r", encoding="utf-8", errors="replace") as f:
                paths = [
                    line.strip() for line in f
                    if line.strip() and not line.startswith("#")
                ]
        except OSError as e:
            wx.MessageBox(f"Could not read playlist: {e}", "Error",
                          wx.ICON_ERROR)
            return
        # Resolve relative paths.
        base = os.path.dirname(source)
        files = []
        for p in paths:
            if not os.path.isabs(p):
                p = os.path.join(base, p)
            if os.path.exists(p):
                files.append(p)
        if files:
            self._add_files_worker(files)

    @staticmethod
    def _parse_dur(s):
        if not s:
            return -1
        try:
            parts = s.split(":")
            parts = [int(x) for x in parts]
            secs = 0
            for p in parts:
                secs = secs * 60 + p
            return secs
        except ValueError:
            return -1

    # ------------------------------------------------------------------
    # Always-on-top, mini player, fullscreen visualization
    # ------------------------------------------------------------------
    def _toggle_always_on_top(self, event):
        flag = self.GetWindowStyle()
        if event.IsChecked():
            self.SetWindowStyle(flag | wx.STAY_ON_TOP)
        else:
            self.SetWindowStyle(flag & ~wx.STAY_ON_TOP)

    def _toggle_mini_player(self, event):
        on = event.IsChecked()
        sizer = self.GetSizer()
        items = sizer.GetChildren()
        # Hide right notebook + bottom notebook in mini mode.
        items[1].Show(not on)
        # Hide the songs/radios notebook bottom area while keeping controls.
        try:
            self.ntDown.Show(not on)
        except Exception:
            pass
        try:
            self.spectrum.Show(not on)
        except Exception:
            pass

        if on:
            self.SetSize(wx.Size(540, 240))
        else:
            self.SetSize(wx.Size(1280, 760))
            self.Centre()
        sizer.Layout()
        self.Layout()

    def _toggle_fullscreen_vis(self, event):
        if getattr(self, "_fullscreen_vis_frame", None):
            try:
                self._fullscreen_vis_frame.Close()
            except Exception:
                pass
            self._fullscreen_vis_frame = None
            return

        from interfaces.visualization import VisualizationDisplay
        f = wx.Frame(self, title="PyMusic — Visualization", size=(1280, 800),
                     style=wx.DEFAULT_FRAME_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)
        vis = VisualizationDisplay(f, wx.ID_ANY, sizer)
        sizer.Add(vis, 1, wx.EXPAND)
        f.SetSizer(sizer)
        f.ShowFullScreen(True)
        vis.start()

        def _close(_e):
            try:
                vis.stop()
            except Exception:
                pass
            self._fullscreen_vis_frame = None
            f.Destroy()

        f.Bind(wx.EVT_CLOSE, _close)
        f.Bind(wx.EVT_CHAR_HOOK, lambda e: _close(e) if e.GetKeyCode() in
               (wx.WXK_ESCAPE, wx.WXK_F11) else e.Skip())
        self._fullscreen_vis_frame = f

    # ------------------------------------------------------------------
    # Orphan files
    # ------------------------------------------------------------------
    def _find_orphans_dialog(self, event):
        orphans = self.data_logic.find_orphans()
        if not orphans:
            wx.MessageBox("No orphan files in the library.", "Orphans",
                          wx.ICON_INFORMATION)
            return
        msg = "\n".join(f"{o.id}: {o.path}" for o in orphans[:20])
        if len(orphans) > 20:
            msg += f"\n... and {len(orphans) - 20} more"
        msg += f"\n\nRemove all {len(orphans)} from the library?"
        if wx.MessageBox(msg, "Orphans", wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return
        for o in orphans:
            self.data_logic.delete_song(o.id)
        songs = self.data_logic.fetch_all_songs()
        self.list_load(songs)

    def _delete_selected_songs(self):
        ids = []
        paths = set()
        idx = self.lbSongs.GetFirstSelected()
        while idx != -1:
            id_text = self.lbSongs.GetItem(idx, 5).GetText()
            try:
                ids.append(int(id_text))
            except ValueError:
                pass
            paths.add(self.lbSongs.GetItem(idx, 0).GetText())
            idx = self.lbSongs.GetNextSelected(idx)

        if not ids:
            return

        msg = f"Delete {len(ids)} song(s) from the library?"
        if wx.MessageBox(msg, "Confirm", wx.YES_NO | wx.ICON_QUESTION) != wx.YES:
            return

        # Only stop playback if the currently playing track is being deleted.
        current = getattr(self, "_current_path", None)
        if current and current in paths:
            try:
                self.logic.stop()
                self.visualization.stop()
                self.spectrum.stop()
            except Exception:
                pass

        for sid in ids:
            try:
                self.data_logic.delete_song(sid)
            except Exception:
                pass

        songs = self.data_logic.fetch_all_songs()
        self.list_load(songs)
        wx.CallAfter(self._refresh_albums)

    def add_songs_individual(self, event):
        wildcard = (
            "Audio files|*.mp3;*.flac;*.ogg;*.oga;*.opus;*.m4a;*.aac;"
            "*.wav;*.wma;*.ape;*.alac;*.aiff;*.aif;*.dsf;*.dff;*.mpc;*.wv"
            "|All files|*.*"
        )
        with wx.FileDialog(
            self, "Choose audio files", wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            paths = dlg.GetPaths()

        self._add_files_worker(paths)

    @threaded
    def _add_files_worker(self, paths):
        songs = self.data_logic.list_files(paths)
        self.data_logic.add_songs(songs)
        all_songs = self.data_logic.fetch_all_songs()
        self.list_load(all_songs)
        wx.CallAfter(self._refresh_albums)

    def on_close(self, event):
        try:
            self._save_state()
        except Exception:
            pass

        cleanups = (
            lambda: self.visualization.stop(),
            lambda: self.spectrum.stop(),
            lambda: self._lyrics_timer.Stop(),
            lambda: hasattr(self, "_crossfade_timer") and self._crossfade_timer.Stop(),
            lambda: hasattr(self, "_sleep_timer") and self._sleep_timer.Stop(),
            lambda: self._tray and self._tray.RemoveIcon() and self._tray.Destroy(),
            lambda: self._mpris and self._mpris.stop(),
            lambda: self._discord and self._discord.stop(),
            lambda: self._karaoke_frame and self._karaoke_frame.Destroy(),
        )
        for c in cleanups:
            try:
                c()
            except Exception:
                pass

        try:
            self.logic.player.next = None
            self.logic.stop()
            # Release VLC media player completely.
            p = self.logic.player.player
            if p:
                p.release()
            inst = getattr(self.logic.player, "_instance", None)
            if inst:
                inst.release()
        except Exception:
            pass

        try:
            import pygame
            pygame.quit()
        except Exception:
            pass

        self.Destroy()
        # Force the interpreter to exit even if non-daemon threads or
        # native libs (VLC, GLib, Discord IPC) lingered.
        wx.CallAfter(self._force_exit)

    @staticmethod
    def _force_exit():
        import os as _os
        _os._exit(0)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def btPlay_click(self, event):
        self.play(event)

    def lbSongs_dbClick(self, event):
        self.play(event)

    def lbRadios_dbClick(self, event):
        self.play_radio(event)

    def btStop_click(self, event):
        self.stop(event)

    def btPause_click(self, event):
        self.pause(event)

    def btResume_click(self, event):
        self.resume(event)

    def tgRandom_click(self, event):
        self.random_play(event)

    def tbFinder_click(self, event):
        self.finder(event)

    def itAddList_click(self, event):
        self.add_list(event)

    def itGenList_click(self, event):
        self.gen_list(event)

    def itViewLyrics_click(self, event):
        event.Skip()

    def btPrevious_click(self, event):
        self.previous(event)

    def btNext_click(self, event):
        self.next(event)

    def itAddRadio_click(self, event):
        self.add_radio(event)

    def lbRadios_keyDown(self, event):
        self.delete_radio(event)

    def ntDown_Changed(self, event):
        self.change_mode(event)

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------
    def initialize_songs(self):
        self.data_logic.createTable()
        songs = self.data_logic.fetch_all_songs()
        self.list_load(songs)

    def initialize_radios(self):
        self.data_logic.create_table_radios()
        radios = self.data_logic.fetch_radios()
        self.listRadios_load(radios)

    @threaded
    def list_load(self, songs):
        """Load the list_ctrl with a list of songs."""
        wx.CallAfter(self._list_load_main, songs)

    def _list_load_main(self, songs):
        self.lbSongs.DeleteAllItems()
        playing_path = getattr(self, "_current_path", None)
        playing_row = -1
        for song in songs:
            complete_name = (song.path or "").rpartition("/")
            fallback = complete_name[2]
            title = getattr(song, "title", None) or fallback
            index = self.lbSongs.InsertItem(self.lbSongs.GetItemCount(), song.path)
            self.lbSongs.SetItem(index, 1, title)
            self.lbSongs.SetItem(index, 2, song.artist or "—")
            self.lbSongs.SetItem(index, 3, song.album or "—")
            self.lbSongs.SetItem(index, 4, str(song.year) if song.year else "—")
            self.lbSongs.SetItem(index, 5, str(song.id))
            self.lbSongs.SetItem(index, 6, _fmt_duration(getattr(song, "duration", None)))
            self.lbSongs.SetItem(index, 7, str(getattr(song, "play_count", 0) or ""))

            if index % 2 == 1:
                self.lbSongs.SetItemBackgroundColour(index, self.BG_LIST_ALT)
            else:
                self.lbSongs.SetItemBackgroundColour(index, self.BG_LIST)
            self.lbSongs.SetItemTextColour(index, self.FG_TEXT)

            if playing_path and song.path == playing_path:
                playing_row = index

        if playing_row >= 0:
            self._highlight_playing_row(playing_row)

    @threaded
    def listRadios_load(self, radios):
        """Load the list_ctrl with a list of radios."""
        wx.CallAfter(self._listRadios_load_main, radios)

    def _listRadios_load_main(self, radios):
        self.lbRadios.DeleteAllItems()
        for radio in radios:
            index = self.lbRadios.InsertItem(self.lbRadios.GetItemCount(), radio.path)
            self.lbRadios.SetItem(index, 0, radio.path)
            self.lbRadios.SetItem(index, 1, str(radio.id))

    # ------------------------------------------------------------------
    # Playback
    # ------------------------------------------------------------------
    def play(self, event):
        if self.logic.get_man_mode() == self.logic.man_modes.RADIO:
            self.play_radio(event)
        elif self.logic.get_man_mode() == self.logic.man_modes.NORMAL:
            self.play_song(event)

    def play_song(self, event):
        if self.logic.mode == self.logic.modes.NORMAL_PLAY:
            index, path = self.song_to_play()
        elif self.logic.mode == self.logic.modes.RANDOM_PLAY:
            index, path = self.random_song_to_play()
        else:
            return

        song = self.lbSongs.GetItem(index, 1).GetText()
        artist = self.lbSongs.GetItem(index, 2).GetText()

        # Start audio FIRST so playback isn't delayed by I/O.
        self._current_path = path
        self._reset_pause_button()
        id = self.logic.play(path, lambda: wx.CallAfter(self._on_song_finished))

        self.showPosThread = ShowPosThread(self.lbTimePos, self.logic.player, id)
        self.showPosThread.start()
        self.moveBarThread = MoveBarThread(self.slPosition, self.logic.player, id)
        self.moveBarThread.start()
        self.visualization.start()
        self.spectrum.start()

        SongNotify(song)
        self._current_song_meta = (song, artist)
        self._highlight_playing_row(index)
        self.SetTitle(f"{song} — {artist} · PyMusic" if song else "PyMusic")
        self._mpris_update()

        # Background: lyrics + cover + play count (these can take time).
        try:
            sid = int(self.lbSongs.GetItem(index, 5).GetText())
        except ValueError:
            sid = None
        self._read_replaygain(path)
        self._apply_volume()
        try:
            if getattr(self, "_eq_gains", None):
                self.logic.player.set_equalizer(self._eq_gains)
        except Exception:
            pass
        self._fetch_lyrics_async(song, artist)
        self._update_cover_async(path)
        if sid:
            import threading
            threading.Thread(
                target=self.data_logic.bump_play_count, args=(sid,), daemon=True,
            ).start()

        # Plugin / external integrations
        try:
            self.plugins.fire("track_started", {
                "song": song, "artist": artist, "path": path, "id": sid,
            })
        except Exception:
            pass
        if self._discord:
            try:
                self._discord.update_track(song, artist)
            except Exception:
                pass
        self._scrobble_async(song, artist, self.lbSongs.GetItem(index, 3).GetText())

    # ------------------------------------------------------------------
    # Equalizer / ReplayGain / Crossfade / Sleep timer
    # ------------------------------------------------------------------
    EQ_BANDS = ("31", "63", "125", "250", "500", "1k", "2k", "4k", "8k", "16k")

    def _open_equalizer(self, event):
        cur = getattr(self, "_eq_gains", [0.0] * 10)
        dlg = _EqualizerDialog(self, cur, self.EQ_BANDS,
                                on_change=self._apply_equalizer)
        dlg.ShowModal()
        dlg.Destroy()

    def _apply_equalizer(self, gains):
        self._eq_gains = list(gains)
        try:
            self.logic.player.set_equalizer(gains)
        except Exception:
            pass

    def _toggle_replaygain(self, event):
        self._rg_enabled = bool(event.IsChecked())
        # Re-apply current track gain.
        self._apply_volume()

    def _apply_volume(self):
        v = self.slVolume.GetValue() / 100.0
        if getattr(self, "_rg_enabled", True):
            db = getattr(self, "_rg_gain_db", 0.0) or 0.0
            v = v * (10 ** (db / 20))
        self.logic.change_volume(v)

    def _read_replaygain(self, path):
        try:
            from logic.tags import Tags
            self._rg_gain_db = Tags(path).replaygain() or 0.0
        except Exception:
            self._rg_gain_db = 0.0

    def _set_crossfade(self, secs):
        self._crossfade_secs = int(secs)
        if not hasattr(self, "_crossfade_timer"):
            self._crossfade_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, self._crossfade_tick, self._crossfade_timer)
        if self._crossfade_secs > 0:
            if not self._crossfade_timer.IsRunning():
                self._crossfade_timer.Start(200)
        else:
            if self._crossfade_timer.IsRunning():
                self._crossfade_timer.Stop()

    def _crossfade_tick(self, event):
        secs = getattr(self, "_crossfade_secs", 0)
        if secs <= 0:
            return
        try:
            if not self.logic.player.isPlaying():
                self._fading = False
                return
            pos = self.logic.player.getSeekedPosition()
            dur = self.logic.player.getSeekableDuration()
        except Exception:
            return
        if pos is None or dur is None or dur <= 0:
            return

        remaining = (dur - pos) / 1_000_000_000
        if remaining > secs:
            self._fading = False
            return

        # Linear fade-out into next track. progress: 0 → 1
        progress = max(0.0, min(1.0, 1.0 - (remaining / secs)))
        v_user = self.slVolume.GetValue() / 100.0
        rg = (10 ** ((self._rg_gain_db or 0.0) / 20)) if getattr(self, "_rg_enabled", True) else 1.0
        try:
            self.logic.player.change_volume(v_user * rg * (1.0 - progress))
        except Exception:
            pass

    def _set_sleep_timer(self, mins):
        if hasattr(self, "_sleep_timer") and self._sleep_timer.IsRunning():
            self._sleep_timer.Stop()
        if mins <= 0:
            return
        if not hasattr(self, "_sleep_timer"):
            self._sleep_timer = wx.Timer(self)
            self.Bind(wx.EVT_TIMER, lambda e: self._sleep_fire(), self._sleep_timer)
        self._sleep_timer.StartOnce(mins * 60 * 1000)

    def _sleep_fire(self):
        try:
            self.stop(None)
        except Exception:
            pass
        wx.MessageBox("Sleep timer reached. Playback stopped.",
                       "Sleep timer", wx.ICON_INFORMATION)

    @threaded
    def _scrobble_async(self, song, artist, album):
        token = getattr(self, "_lb_token", None)
        if not token:
            return
        try:
            from interfaces.listenbrainz import submit_now_playing, submit_listen
            submit_now_playing(token, song, artist, album)
            submit_listen(token, song, artist, album)
        except Exception:
            pass

    def _set_listenbrainz_token(self, event):
        cur = getattr(self, "_lb_token", "") or ""
        dlg = wx.TextEntryDialog(
            self, "ListenBrainz user token (https://listenbrainz.org/profile/)",
            "Set token", value=cur,
        )
        if dlg.ShowModal() == wx.ID_OK:
            self._lb_token = dlg.GetValue().strip() or None
            self._save_state()
        dlg.Destroy()

    @threaded
    def _fetch_lyrics_async(self, song, artist):
        searcher = self.logic.lyrics_searcher(song, artist)
        lyrics = searcher.get_lyrics()
        synced = searcher.get_synced()
        wx.CallAfter(self._set_lyrics, lyrics, synced)

    @threaded
    def _update_cover_async(self, path):
        from logic.tags import Tags
        cover_bytes = None
        artist = None
        album = None
        try:
            t = Tags(path)
            cover_bytes = t.cover()
            artist = t.artista()
            album = t.album()
        except Exception:
            pass

        if not cover_bytes:
            try:
                from data.musicbrainz import fetch_cover
                cover_bytes = fetch_cover(artist, album)
            except Exception:
                cover_bytes = None

        wx.CallAfter(self._render_cover, cover_bytes)

    def _render_cover(self, cover_bytes):
        self._set_tab_availability(self.pnCover, "Cover", bool(cover_bytes))
        if not cover_bytes:
            self.bmCover.SetBitmap(wx.Bitmap(1, 1))
            self.pnCover.Layout()
            return
        try:
            stream = io.BytesIO(cover_bytes)
            img = wx.Image(stream)
            if not img.IsOk():
                return
            panel_size = self.pnCover.GetClientSize()
            target = max(64, min(panel_size.GetWidth(), panel_size.GetHeight()) - 30)
            target = min(target, 600)
            img = img.Scale(target, target, wx.IMAGE_QUALITY_HIGH)
            self.bmCover.SetBitmap(wx.Bitmap(img))
            self.pnCover.Layout()
        except Exception:
            pass

    def _highlight_playing_row(self, index):
        try:
            count = self.lbSongs.GetItemCount()
            for i in range(count):
                if i == index:
                    self.lbSongs.SetItemBackgroundColour(i, self.ACCENT_BG)
                    self.lbSongs.SetItemTextColour(i, wx.Colour(255, 255, 255))
                else:
                    bg = self.BG_LIST_ALT if i % 2 == 1 else self.BG_LIST
                    self.lbSongs.SetItemBackgroundColour(i, bg)
                    self.lbSongs.SetItemTextColour(i, self.FG_TEXT)
        except Exception:
            pass

    def play_radio(self, event):
        index, radio_to_play = self.radio_to_play()
        self.id = self.logic.play(radio_to_play, self.next)
        SongNotify(radio_to_play)

    def stop(self, event):
        self.logic.stop()
        self.visualization.stop()
        self.spectrum.stop()
        if hasattr(self, "_lyrics_timer") and self._lyrics_timer.IsRunning():
            self._lyrics_timer.Stop()
        self.btPlay.SetLabel("▶  Play")
        self._mpris_update()

    def _stop_audio_only(self):
        """Stop audio without tearing down visuals (used between tracks)."""
        try:
            self.logic.stop()
        except Exception:
            pass

    def _on_play_pause_click(self, event):
        try:
            playing = self.logic.is_playing()
            paused = self.logic.player.isPaused()
        except Exception:
            playing = paused = False
        if playing:
            self.pause(event)
        elif paused:
            self.resume(event)
        else:
            self.play(event)

    def pause(self, event):
        self.logic.pause()
        self.visualization.stop()
        self.spectrum.stop()
        self.btPlay.SetLabel("▶  Resume")

    def resume(self, event):
        self.logic.resume()
        self.visualization.start()
        self.spectrum.start()
        self.btPlay.SetLabel("⏸  Pause")

    def _reset_pause_button(self):
        # When a new track starts, the Play button shows "Pause".
        self.btPlay.SetLabel("⏸  Pause")

    def _find_current_index(self):
        cur = getattr(self, "_current_path", None)
        if not cur:
            return self.lbSongs.GetFirstSelected()
        for i in range(self.lbSongs.GetItemCount()):
            if self.lbSongs.GetItem(i, 0).GetText() == cur:
                return i
        return self.lbSongs.GetFirstSelected()

    def _on_song_finished(self):
        """Called when the player reaches end of stream."""
        if self._repeat == "one":
            # Replay current track without depending on user selection.
            cur_idx = self._find_current_index()
            if cur_idx >= 0:
                self._select_index(cur_idx)
            self._stop_audio_only()
            self.play(None)
            return
        if self._repeat == "off":
            cur = self._find_current_index()
            if cur >= self.get_list_len() - 1:
                self.stop(None)
                return
        self.next()

    def _select_index(self, i):
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        prev = self.lbSongs.GetFirstSelected()
        while prev != -1:
            self.lbSongs.SetItemState(prev, 0, wx.LIST_STATE_SELECTED)
            prev = self.lbSongs.GetNextSelected(prev)
        self.lbSongs.SetItemState(i, SEL_FOC, SEL_FOC)
        self.lbSongs.EnsureVisible(i)

    def next(self, event=None):
        """Play the next song."""
        self._stop_audio_only()
        self.set_next_index()
        self.play(self.next)

    def previous(self, event=None):
        """Play the previous song."""
        self._stop_audio_only()
        self.set_next_index(offset=-1)
        self.play(self.next)

    def get_list_len(self):
        return self.lbSongs.GetItemCount()

    def set_next_index(self, offset=1):
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        index = self.lbSongs.GetFirstSelected()
        self.lbSongs.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

        if index < self.get_list_len() - 1:
            self.lbSongs.SetItemState(index + offset, SEL_FOC, SEL_FOC)
        else:
            self.lbSongs.SetItemState(0, SEL_FOC, SEL_FOC)

    def set_song(self, index):
        """Select a song in the list, update the title textbox and return its path."""
        count = self.get_list_len()
        if count == 0:
            return None
        if index < 0 or index >= count:
            index = 0

        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        current_index = self.lbSongs.GetFirstSelected()
        if current_index >= 0:
            self.lbSongs.SetItemState(current_index, 0, wx.LIST_STATE_SELECTED)
        self.lbSongs.SetItemState(index, SEL_FOC, SEL_FOC)

        song_to_play = self.lbSongs.GetItem(index, 0).GetText()
        title_of_song = self.lbSongs.GetItem(index, 1).GetText()
        self.tbSong.SetValue(title_of_song)
        self.SetTitle(title_of_song)
        self.SetName(title_of_song)

        return song_to_play

    def set_radio(self, index):
        """Select a radio in the list, update the title textbox and return its uri."""
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        current_index = self.lbRadios.GetFirstSelected()
        self.lbRadios.SetItemState(current_index, 0, wx.LIST_STATE_SELECTED)

        if index < self.get_list_len() - 1:
            self.lbRadios.SetItemState(index, SEL_FOC, SEL_FOC)
        else:
            self.lbRadios.SetItemState(0, SEL_FOC, SEL_FOC)

        radio_to_play = self.lbRadios.GetItem(index, 0).GetText()
        self.tbSong.SetValue(radio_to_play)
        return radio_to_play

    def song_to_play(self):
        """Select the current song to play."""
        if self.get_list_len() == 0:
            return -1, None
        index = self.lbSongs.GetFirstSelected()
        if index < 0:
            index = 0
        song_to_play = self.set_song(index)

        while not self.check_exists(song_to_play):
            index += 1
            song_to_play = self.set_song(index)

        return index, song_to_play

    def random_song_to_play(self):
        """Select a random song to play."""
        random_index = self.logic.random_song(0, self.get_list_len() - 1)
        song_to_play = self.set_song(random_index)

        while not self.check_exists(song_to_play):
            random_index = self.logic.random_song(0, self.get_list_len() - 1)
            song_to_play = self.set_song(random_index)

        return random_index, song_to_play

    def radio_to_play(self):
        """Select the current radio to play."""
        index = self.lbRadios.GetFirstSelected()
        return index, self.set_radio(index)

    def check_exists(self, path):
        """Return True if ``path`` exists on the filesystem."""
        return self.logic.check_exists(path)

    def random_play(self, event):
        """Toggle random play mode."""
        if self.logic.get_mode() == self.logic.modes.RANDOM_PLAY:
            self.logic.set_mode(self.logic.modes.NORMAL_PLAY)
        else:
            self.logic.set_mode(self.logic.modes.RANDOM_PLAY)

    def change_mode(self, event):
        """Switch between PLAY_LIST and RADIOS based on the selected notebook page."""
        page = self.ntDown.GetSelection()
        if page == 1:
            self.logic.set_man_mode(self.logic.man_modes.RADIO)
        elif page == 0:
            self.logic.set_man_mode(self.logic.man_modes.NORMAL)

    def finder(self, event):
        """Find a list of songs by a condition. Empty query clears the filter."""
        kc = event.GetKeyCode()
        if kc == 13:  # Enter
            q = self.tbFinder.GetValue().strip()
            if q:
                songs = self.data_logic.find(q)
            else:
                songs = self.data_logic.fetch_all_songs()
            self.lbSongs.DeleteAllItems()
            self.list_load(songs)
        elif kc == wx.WXK_ESCAPE:
            self.tbFinder.SetValue("")
            self._load_smart("all")
        else:
            event.Skip()

    def add_list(self, event):
        if self.dir_dialog.ShowModal() == wx.ID_OK:
            self.dir_worker(self.dir_dialog.GetPath())

    def hide_lyrics(self, event):
        pass

    @threaded
    def dir_worker(self, dir):
        list_dir = self.data_logic.list_dir(dir)
        self.data_logic.add_songs(list_dir)
        songs = self.data_logic.fetch_all_songs()
        self.list_load(songs)
        wx.CallAfter(self._refresh_albums)
        wx.CallAfter(self.Refresh)

    def add_radio(self, event):
        frmAddRadio = wxFrmAddRadio(self)
        frmAddRadio.ShowModal()

    def slVolume_slide(self, event):
        self._apply_volume()

    def delete_radio(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            current_index = self.lbRadios.GetFirstSelected()
            id = self.lbRadios.GetItem(current_index, 1).GetText()
            self.data_logic.delete_radio(id)
            self.initialize_radios()

    def gen_list(self, event):
        frmGenList = wxFrmGenList(self)
        frmGenList.ShowModal()
        if frmGenList.State == frmGenList.OK:
            size = int(frmGenList.size)
            filter = frmGenList.filter
            path = frmGenList.dir
            self.list_generator(path, filter, size)

    @threaded
    def list_generator(self, path, filter, size):
        size *= 1024  # bytes to kilo
        size *= 1024  # kilo to mega
        acum = 0
        songs = self.data_logic.find(filter)
        if not os.path.exists(path):
            os.mkdir(path)
        for song in songs:
            try:
                filesize = os.path.getsize(song.path)
            except OSError:
                continue
            acum += filesize

            if size <= acum:
                break
            command = f'cp "{song.path}" "{path}"'
            print(command)
            try:
                os.system(command)
            except Exception:
                acum -= filesize
                continue


class _AudioDropTarget(wx.FileDropTarget):

    def __init__(self, window):
        super().__init__()
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        try:
            wx.CallAfter(self.window._on_files_dropped, list(filenames))
        except Exception:
            return False
        return True


try:
    import wx.adv as _wxadv

    class _PyMusicTrayIcon(_wxadv.TaskBarIcon):

        def __init__(self, frame):
            super().__init__()
            self.frame = frame
            try:
                bmp = wx.ArtProvider.GetBitmap(wx.ART_HELP_BOOK, wx.ART_OTHER, (16, 16))
                self.SetIcon(wx.Icon(bmp), "PyMusic")
            except Exception:
                pass
            self.Bind(_wxadv.EVT_TASKBAR_LEFT_DCLICK, self._on_show)

        def CreatePopupMenu(self):
            menu = wx.Menu()
            show = menu.Append(wx.ID_ANY, "Show / Hide")
            menu.AppendSeparator()
            play = menu.Append(wx.ID_ANY, "▶  Play / Pause")
            nxt = menu.Append(wx.ID_ANY, "⏭  Next")
            prv = menu.Append(wx.ID_ANY, "⏮  Previous")
            stp = menu.Append(wx.ID_ANY, "■  Stop")
            menu.AppendSeparator()
            quit_ = menu.Append(wx.ID_ANY, "Quit")

            self.Bind(wx.EVT_MENU, self._on_show, show)
            self.Bind(wx.EVT_MENU, lambda e: self.frame._kbd_play_pause(), play)
            self.Bind(wx.EVT_MENU, lambda e: self.frame.next(), nxt)
            self.Bind(wx.EVT_MENU, lambda e: self.frame.previous(), prv)
            self.Bind(wx.EVT_MENU, lambda e: self.frame.stop(None), stp)
            self.Bind(wx.EVT_MENU, lambda e: self.frame.Close(), quit_)
            return menu

        def _on_show(self, event):
            if self.frame.IsShown():
                self.frame.Hide()
            else:
                self.frame.Show()
                self.frame.Raise()
except ImportError:
    _PyMusicTrayIcon = None


def _fmt_duration(seconds):
    if not seconds or seconds <= 0:
        return ""
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    if m >= 60:
        h, m = divmod(m, 60)
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


class _TagEditorDialog(wx.Dialog):

    FIELDS = [("Title", "title"), ("Artist", "artist"),
              ("Album", "album"), ("Year", "year")]

    def __init__(self, parent, current):
        super().__init__(parent, title="Edit tags", size=(520, 320))
        self._inputs = {}

        outer = wx.BoxSizer(wx.VERTICAL)

        for label, key in self.FIELDS:
            row = wx.BoxSizer(wx.VERTICAL)
            lbl = wx.StaticText(self, label=label)
            f = lbl.GetFont()
            f.SetWeight(wx.FONTWEIGHT_BOLD)
            lbl.SetFont(f)
            row.Add(lbl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 2)

            tc = wx.TextCtrl(self, value=current.get(key) or "")
            tc.SetMinSize(wx.Size(-1, 28))
            row.Add(tc, 0, wx.EXPAND)
            self._inputs[key] = tc

            outer.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 14)

        btns = wx.StdDialogButtonSizer()
        ok = wx.Button(self, wx.ID_OK, "Save")
        cancel = wx.Button(self, wx.ID_CANCEL)
        btns.AddButton(ok)
        btns.AddButton(cancel)
        btns.Realize()
        outer.Add(btns, 0, wx.ALIGN_RIGHT | wx.ALL, 14)

        self.SetSizer(outer)
        self.Layout()

    def values(self):
        return {k: tc.GetValue().strip() for k, tc in self._inputs.items()}


class _EqualizerDialog(wx.Dialog):

    PRESETS = {
        "Flat":    [0]*10,
        "Rock":    [3, 2, 1, 0, -1, -1, 1, 2, 3, 4],
        "Pop":     [-1, 1, 2, 3, 2, 0, -1, -2, -2, -1],
        "Jazz":    [2, 1, 1, 2, -1, -1, 0, 1, 2, 2],
        "Classical": [3, 2, 1, 1, -1, -1, -1, 1, 2, 3],
        "Bass Boost": [6, 5, 4, 3, 1, 0, 0, 0, 0, 0],
        "Vocal":   [-2, -1, 0, 2, 4, 4, 3, 2, 0, -1],
    }

    def __init__(self, parent, gains, bands, on_change):
        super().__init__(parent, title="Equalizer", size=(560, 360))
        self.SetBackgroundColour(wx.Colour(28, 28, 42))
        self._on_change = on_change
        self._sliders = []

        outer = wx.BoxSizer(wx.VERTICAL)

        preset_row = wx.BoxSizer(wx.HORIZONTAL)
        preset_row.Add(wx.StaticText(self, label="Preset:"),
                       0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        self.cbPreset = wx.Choice(self, choices=list(self.PRESETS.keys()))
        self.cbPreset.SetSelection(0)
        self.cbPreset.Bind(wx.EVT_CHOICE, self._on_preset)
        preset_row.Add(self.cbPreset, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 6)
        outer.Add(preset_row, 0, wx.EXPAND)

        grid = wx.BoxSizer(wx.HORIZONTAL)
        for i, label in enumerate(bands):
            col = wx.BoxSizer(wx.VERTICAL)
            sl = wx.Slider(self, value=int(gains[i]),
                           minValue=-20, maxValue=20,
                           style=wx.SL_VERTICAL | wx.SL_INVERSE)
            sl.SetMinSize(wx.Size(40, 200))
            sl.Bind(wx.EVT_SLIDER, self._on_slide)
            col.Add(sl, 1, wx.ALIGN_CENTER | wx.ALL, 4)
            lbl = wx.StaticText(self, label=label)
            lbl.SetForegroundColour(wx.Colour(220, 220, 230))
            col.Add(lbl, 0, wx.ALIGN_CENTER)
            grid.Add(col, 1, wx.EXPAND | wx.ALL, 4)
            self._sliders.append(sl)

        outer.Add(grid, 1, wx.EXPAND | wx.ALL, 6)

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(wx.Button(self, wx.ID_OK, "Close"))
        btns.Realize()
        outer.Add(btns, 0, wx.ALIGN_CENTER | wx.BOTTOM, 6)

        self.SetSizer(outer)

    def _on_slide(self, event):
        gains = [s.GetValue() for s in self._sliders]
        if self._on_change:
            self._on_change(gains)

    def _on_preset(self, event):
        name = self.cbPreset.GetStringSelection()
        gains = self.PRESETS.get(name, [0]*10)
        for i, v in enumerate(gains):
            self._sliders[i].SetValue(v)
        if self._on_change:
            self._on_change(gains)


class _SashPanel(wx.Panel):

    WIDTH = 6

    def __init__(self, parent, on_drag):
        super().__init__(parent, size=(self.WIDTH, -1))
        self.SetBackgroundColour(wx.Colour(60, 60, 90))
        self.SetCursor(wx.Cursor(wx.CURSOR_SIZEWE))
        self._on_drag = on_drag
        self._dragging = False
        self.Bind(wx.EVT_LEFT_DOWN, self._down)
        self.Bind(wx.EVT_LEFT_UP, self._up)
        self.Bind(wx.EVT_MOTION, self._motion)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, lambda e: setattr(self, "_dragging", False))

    def _down(self, e):
        self._dragging = True
        try:
            self.CaptureMouse()
        except Exception:
            pass

    def _up(self, e):
        if self._dragging:
            self._dragging = False
            try:
                self.ReleaseMouse()
            except Exception:
                pass

    def _motion(self, e):
        if self._dragging and e.Dragging():
            sx, _sy = self.ClientToScreen(e.GetPosition())
            self._on_drag(sx)
