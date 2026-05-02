"""Tiny plugin loader.

Plugins live as Python files under ``~/.config/pymusic/plugins/`` and
expose a ``register(api)`` function. ``api`` is the PluginManager which
gives access to the running player frame and a hook registry::

    def register(api):
        @api.on("track_started")
        def _(track):
            print("now playing:", track)

Hooks fired from the host: ``track_started(meta_dict)``,
``track_finished(meta_dict)``, ``volume_changed(value)``.
"""

import importlib.util
import os
import traceback


PLUGIN_DIR = os.path.expanduser("~/.config/pymusic/plugins")


class PluginManager:

    def __init__(self, frame):
        self.frame = frame
        self._hooks = {}
        self._plugins = []

    # ------------------------------------------------------------------
    # Registration API exposed to plugins
    # ------------------------------------------------------------------
    def on(self, name):
        def decorator(fn):
            self._hooks.setdefault(name, []).append(fn)
            return fn
        return decorator

    @property
    def player(self):
        return self.frame.logic.player

    @property
    def app(self):
        return self.frame

    # ------------------------------------------------------------------
    def fire(self, name, *args, **kwargs):
        for fn in self._hooks.get(name, []):
            try:
                fn(*args, **kwargs)
            except Exception:
                traceback.print_exc()

    # ------------------------------------------------------------------
    def load_all(self):
        if not os.path.isdir(PLUGIN_DIR):
            try:
                os.makedirs(PLUGIN_DIR, exist_ok=True)
            except OSError:
                return

        for fname in sorted(os.listdir(PLUGIN_DIR)):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            path = os.path.join(PLUGIN_DIR, fname)
            try:
                spec = importlib.util.spec_from_file_location(
                    f"pymusic_plugin_{fname[:-3]}", path,
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register"):
                    mod.register(self)
                    self._plugins.append(fname)
            except Exception:
                traceback.print_exc()
