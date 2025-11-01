"""Application entrypoint for the desktop problem scraper."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def run() -> None:
    """Run the PySide6 application event loop."""

    app = QApplication(sys.argv)
    app.setApplicationName("Problem Scraper")
    app.setOrganizationName("TestCaseGenerator")

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    # Ensure runtime folders (like temporary output) are cleaned up if needed.
    if hasattr(window, "cleanup"):
        window.cleanup()
    sys.exit(exit_code)


if __name__ == "__main__":  # pragma: no cover - manual execution path
    run()
