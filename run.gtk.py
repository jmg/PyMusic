# -*- coding: utf-8 -*-

from interfaces.gui import MainWindow
from interfaces.console import ConsoleProxy
import sys
import gtk

if __name__ == '__main__':

    if len(sys.argv) > 1:
        ConsoleProxy(sys.argv[1:])
    else:
        gui_player = MainWindow()
        gui_player.window.show()
        gtk.main()
