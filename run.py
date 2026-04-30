#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from wx import App

from interfaces.wxGui import MainWindow
from interfaces.console import ConsoleProxy


def main():
    if len(sys.argv) > 1:
        ConsoleProxy(sys.argv[1:])
    else:
        app = App(0)
        frame = MainWindow(None)
        frame.Show()
        app.MainLoop()


if __name__ == '__main__':
    main()
