"""Minimal MPRIS2 server using jeepney (pure Python D-Bus).

Implements org.mpris.MediaPlayer2 and ...Player just enough so that
playerctl, GNOME shell, KDE Plasma's media indicator and similar tools
recognise PyMusic and can drive Play/Pause/Next/Previous.
"""

import threading

try:
    from jeepney import DBusAddress, MessageGenerator, new_method_return, new_signal
    from jeepney.bus_messages import message_bus
    from jeepney.io.blocking import open_dbus_connection
    from jeepney.wrappers import new_error
    _JEEPNEY = True
except ImportError:
    _JEEPNEY = False


BUS_NAME = "org.mpris.MediaPlayer2.PyMusic"
OBJECT_PATH = "/org/mpris/MediaPlayer2"

ROOT_IFACE = "org.mpris.MediaPlayer2"
PLAYER_IFACE = "org.mpris.MediaPlayer2.Player"
PROPS_IFACE = "org.freedesktop.DBus.Properties"
INTROSPECT_IFACE = "org.freedesktop.DBus.Introspectable"

INTROSPECT_XML = """<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
  <interface name="org.freedesktop.DBus.Introspectable">
    <method name="Introspect"><arg name="data" type="s" direction="out"/></method>
  </interface>
  <interface name="org.freedesktop.DBus.Properties">
    <method name="Get"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="out"/></method>
    <method name="GetAll"><arg type="s" direction="in"/><arg type="a{sv}" direction="out"/></method>
    <method name="Set"><arg type="s" direction="in"/><arg type="s" direction="in"/><arg type="v" direction="in"/></method>
  </interface>
  <interface name="org.mpris.MediaPlayer2">
    <method name="Raise"/>
    <method name="Quit"/>
    <property name="CanQuit" type="b" access="read"/>
    <property name="CanRaise" type="b" access="read"/>
    <property name="HasTrackList" type="b" access="read"/>
    <property name="Identity" type="s" access="read"/>
    <property name="SupportedMimeTypes" type="as" access="read"/>
    <property name="SupportedUriSchemes" type="as" access="read"/>
  </interface>
  <interface name="org.mpris.MediaPlayer2.Player">
    <method name="Next"/>
    <method name="Previous"/>
    <method name="Pause"/>
    <method name="PlayPause"/>
    <method name="Stop"/>
    <method name="Play"/>
    <property name="PlaybackStatus" type="s" access="read"/>
    <property name="Metadata" type="a{sv}" access="read"/>
    <property name="Volume" type="d" access="readwrite"/>
    <property name="CanGoNext" type="b" access="read"/>
    <property name="CanGoPrevious" type="b" access="read"/>
    <property name="CanPlay" type="b" access="read"/>
    <property name="CanPause" type="b" access="read"/>
    <property name="CanSeek" type="b" access="read"/>
    <property name="CanControl" type="b" access="read"/>
  </interface>
</node>
"""


class MprisServer:

    def __init__(self, frame):
        if not _JEEPNEY:
            raise RuntimeError("jeepney not available")
        self.frame = frame
        self.conn = None
        self.thread = None
        self._stop = threading.Event()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def start(self):
        self.conn = open_dbus_connection(bus="SESSION")
        # Request name on bus
        reply = self.conn.send_and_get_reply(
            message_bus.RequestName(BUS_NAME, 0)
        )
        if reply.body and reply.body[0] not in (1, 4):
            # 1 = primary owner, 4 = already owner
            raise RuntimeError(f"could not own bus name (code {reply.body[0]})")

        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()

    def stop(self):
        self._stop.set()
        try:
            if self.conn:
                self.conn.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Serve loop
    # ------------------------------------------------------------------
    def _serve(self):
        while not self._stop.is_set():
            try:
                msg = self.conn.receive()
            except Exception:
                break
            if msg is None:
                continue
            try:
                self._handle(msg)
            except Exception:
                continue

    def _handle(self, msg):
        h = msg.header
        if h.message_type.name != "method_call":
            return
        iface = h.fields.get(2)   # interface
        member = h.fields.get(3)  # member

        if iface == INTROSPECT_IFACE and member == "Introspect":
            self.conn.send(new_method_return(msg, "s", (INTROSPECT_XML,)))
            return

        if iface == PROPS_IFACE:
            self._handle_props(msg, member)
            return

        if iface == ROOT_IFACE:
            self._handle_root(msg, member)
            return

        if iface == PLAYER_IFACE:
            self._handle_player(msg, member)
            return

        self.conn.send(new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod",
                                  "s", (f"{iface}.{member}",)))

    # ------------------------------------------------------------------
    def _props_for(self, iface):
        if iface == ROOT_IFACE:
            return {
                "CanQuit": ("b", True),
                "CanRaise": ("b", True),
                "HasTrackList": ("b", False),
                "Identity": ("s", "PyMusic"),
                "SupportedMimeTypes": ("as", ["audio/mpeg", "audio/ogg", "audio/x-wav"]),
                "SupportedUriSchemes": ("as", ["file"]),
            }
        if iface == PLAYER_IFACE:
            return {
                "PlaybackStatus": ("s", self._status()),
                "Metadata": ("a{sv}", self._metadata()),
                "Volume": ("d", self._volume()),
                "CanGoNext": ("b", True),
                "CanGoPrevious": ("b", True),
                "CanPlay": ("b", True),
                "CanPause": ("b", True),
                "CanSeek": ("b", False),
                "CanControl": ("b", True),
            }
        return {}

    def _handle_props(self, msg, member):
        body = msg.body
        if member == "Get":
            iface, name = body
            props = self._props_for(iface)
            if name in props:
                sig, val = props[name]
                self.conn.send(new_method_return(msg, "v", ((sig, val),)))
            else:
                self.conn.send(new_error(msg, "org.freedesktop.DBus.Error.UnknownProperty",
                                          "s", (name,)))
        elif member == "GetAll":
            iface, = body
            props = self._props_for(iface)
            out = {k: (sig, v) for k, (sig, v) in props.items()}
            self.conn.send(new_method_return(msg, "a{sv}", (out,)))
        elif member == "Set":
            iface, name, value = body
            if iface == PLAYER_IFACE and name == "Volume":
                _sig, vol = value
                try:
                    self.frame.slVolume.SetValue(int(vol * 100))
                    self.frame.logic.change_volume(float(vol))
                except Exception:
                    pass
            self.conn.send(new_method_return(msg))

    def _handle_root(self, msg, member):
        if member == "Raise":
            try:
                self.frame.Show()
                self.frame.Raise()
            except Exception:
                pass
            self.conn.send(new_method_return(msg))
        elif member == "Quit":
            try:
                self.frame.Close()
            except Exception:
                pass
            self.conn.send(new_method_return(msg))
        else:
            self.conn.send(new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod",
                                      "s", (member,)))

    def _handle_player(self, msg, member):
        actions = {
            "Play": self.frame._kbd_play_pause,
            "Pause": lambda: self.frame.pause(None),
            "PlayPause": self.frame._kbd_play_pause,
            "Stop": lambda: self.frame.stop(None),
            "Next": self.frame.next,
            "Previous": self.frame.previous,
        }
        if member in actions:
            try:
                actions[member]()
            except Exception:
                pass
            self.conn.send(new_method_return(msg))
        else:
            self.conn.send(new_error(msg, "org.freedesktop.DBus.Error.UnknownMethod",
                                      "s", (member,)))

    # ------------------------------------------------------------------
    def _status(self):
        try:
            p = self.frame.logic.player
            if p.isPlaying():
                return "Playing"
            if p.isPaused():
                return "Paused"
        except Exception:
            pass
        return "Stopped"

    def _metadata(self):
        meta = {"mpris:trackid": ("o", "/org/mpris/MediaPlayer2/PyMusic/Track")}
        info = getattr(self.frame, "_current_song_meta", None)
        if info:
            song, artist = info
            meta["xesam:title"] = ("s", song or "")
            meta["xesam:artist"] = ("as", [artist or ""])
        return meta

    def _volume(self):
        try:
            return self.frame.slVolume.GetValue() / 100.0
        except Exception:
            return 1.0

    # ------------------------------------------------------------------
    def notify_status(self):
        """Emit PropertiesChanged so MPRIS clients refresh the now-playing."""
        if not self.conn:
            return
        changed = {
            "PlaybackStatus": ("s", self._status()),
            "Metadata": ("a{sv}", self._metadata()),
        }
        try:
            sig = new_signal(
                OBJECT_PATH, PROPS_IFACE, "PropertiesChanged", "sa{sv}as",
                (PLAYER_IFACE, changed, []),
            )
            self.conn.send(sig)
        except Exception:
            pass
