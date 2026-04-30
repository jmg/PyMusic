"""Application entry point for the Qt GUI."""

from __future__ import annotations

import logging
import sys


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QPalette, QColor
        from PySide6.QtWidgets import QApplication
    except ImportError:
        sys.stderr.write(
            "PySide6 is not installed. Install it with:\n  pip install PySide6\n"
        )
        return 2

    from .main_window import MainWindow

    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("PyMusic")
    app.setOrganizationName("PyMusic")
    app.setStyle("Fusion")
    app.setPalette(_dark_palette(QPalette, QColor, Qt))

    window = MainWindow()
    window.show()
    return app.exec()


def _dark_palette(QPalette, QColor, Qt):  # noqa: ANN001
    p = QPalette()
    p.setColor(QPalette.Window, QColor(38, 40, 46))
    p.setColor(QPalette.WindowText, QColor(220, 220, 220))
    p.setColor(QPalette.Base, QColor(28, 30, 35))
    p.setColor(QPalette.AlternateBase, QColor(45, 47, 54))
    p.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    p.setColor(QPalette.ToolTipText, QColor(38, 40, 46))
    p.setColor(QPalette.Text, QColor(220, 220, 220))
    p.setColor(QPalette.Button, QColor(45, 47, 54))
    p.setColor(QPalette.ButtonText, QColor(220, 220, 220))
    p.setColor(QPalette.BrightText, QColor(255, 0, 0))
    p.setColor(QPalette.Link, QColor(96, 167, 255))
    p.setColor(QPalette.Highlight, QColor(96, 167, 255))
    p.setColor(QPalette.HighlightedText, QColor(28, 30, 35))
    return p


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
