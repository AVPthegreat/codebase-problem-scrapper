"""Application entrypoint for the desktop problem scraper."""

from __future__ import annotations

import sys
import os
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication
import PySide6

from app.ui.main_window import MainWindow


def run() -> None:
    """Run the PySide6 application event loop."""

    qt_root = Path(PySide6.__file__).resolve().parent / "Qt"
    plugin_root = qt_root / "plugins"
    existing_plugin_path = os.environ.get("QT_PLUGIN_PATH")
    os.environ["QT_PLUGIN_PATH"] = (
        str(plugin_root)
        if not existing_plugin_path
        else f"{str(plugin_root)}:{existing_plugin_path}"
    )
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(plugin_root / "platforms")
    framework_root = qt_root / "lib"
    if framework_root.exists():
        existing_framework_path = os.environ.get("DYLD_FRAMEWORK_PATH")
        os.environ["DYLD_FRAMEWORK_PATH"] = (
            str(framework_root)
            if not existing_framework_path
            else f"{str(framework_root)}:{existing_framework_path}"
        )
    if str(plugin_root) not in QCoreApplication.libraryPaths():
        QCoreApplication.addLibraryPath(str(plugin_root))

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
