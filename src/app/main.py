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
    """Run the PySide6 application event loop.
    
    Note: If GUI crashes on macOS, set environment variable:
        export QT_QPA_PLATFORM=offscreen
    """

    # Allow disabling path manipulation when the environment is healthy (e.g., py312)
    if os.environ.get("TCG_SKIP_QT_PATHS") != "1":
        qt_root = Path(PySide6.__file__).resolve().parent / "Qt"
        plugin_root = qt_root / "plugins"
        # Set Qt plugin paths
        os.environ.setdefault("QT_QPA_PLATFORM_PLUGIN_PATH", str(plugin_root / "platforms"))
        os.environ.setdefault("QT_PLUGIN_PATH", str(plugin_root))
        # Set framework paths for macOS (can be sensitive; avoid overriding existing env)
        framework_root = qt_root / "lib"
        if framework_root.exists():
            os.environ.setdefault("DYLD_FRAMEWORK_PATH", str(framework_root))
            os.environ.setdefault("DYLD_LIBRARY_PATH", str(framework_root))

    app = QApplication(sys.argv)
    
    # Verify platform
    platform = os.environ.get("QT_QPA_PLATFORM", "default")
    if platform == "offscreen":
        print("⚠️  Running in offscreen mode (no GUI will be displayed)")
        print("   This is a workaround for Qt plugin issues on macOS")
    
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
