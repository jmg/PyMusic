#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from interfaces.gui import MainWindow
from interfaces.console import ConsoleProxy


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ConsoleProxy(sys.argv[1:])
    else:
        gui_player = MainWindow()
        gui_player.window.show()
        Gtk.main()
