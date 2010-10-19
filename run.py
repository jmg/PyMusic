#/usr/bin/env python
# -*- coding: utf-8 -*-

import wxversion
wxversion.select("2.8")

from wx import App

from interfaces.wxGui import MainWindow
from interfaces.console import ConsoleProxy
import sys
import gtk

if __name__ == '__main__':

    if len(sys.argv) > 1:
        ConsoleProxy(sys.argv[1:])
    else:
        app = App(0)
        frame = MainWindow(None)
        frame.Show()
        app.MainLoop()
