"""Desktop notifications via libnotify (PyGObject) with a no-op fallback."""

try:
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify

    Notify.init('PyMusic')

    def _notify(song):
        notification = Notify.Notification.new(str(song))
        try:
            notification.show()
        except Exception:
            pass
        return notification

except (ImportError, ValueError):
    def _notify(song):
        return None


class SongNotify:
    """Pop a small libnotify bubble with the currently playing song."""

    def __init__(self, song):
        self._handle = _notify(song)
