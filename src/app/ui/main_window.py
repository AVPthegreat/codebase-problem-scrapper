"""Main window for the desktop scraper."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.orchestrator import ScrapeOrchestrator


class ScrapeWorker(QObject):
    """Background worker that runs the scrape orchestrator in a thread."""

    finished = Signal(Path)
    failed = Signal(str)
    log = Signal(str)

    def __init__(self, prompt: str, output_dir: Optional[Path] = None) -> None:
        super().__init__()
        self._prompt = prompt
        self._output_dir = output_dir
        if output_dir is not None:
            self._orchestrator = ScrapeOrchestrator(base_output=output_dir)
        else:
            self._orchestrator = ScrapeOrchestrator()

    @Slot()
    def run(self) -> None:
        try:
            self.log.emit("Starting scraping workflow...")
            zip_path = self._orchestrator.generate_bundle(
                self._prompt,
                log_callback=self.log.emit,
            )
            self.log.emit(f"Generated bundle: {zip_path}")
            self.finished.emit(zip_path)
        except Exception as exc:  # pragma: no cover - UI runtime path
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    """Primary application window housing prompt input and controls."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Problem Scraper")
        self.resize(900, 600)

        self._prompt_input = QPlainTextEdit(self)
        self._prompt_input.setPlaceholderText(
            "Describe the problems you need, e.g. 'Give me 10 medium sorting questions with input/output details.'"
        )

        self._generate_button = QPushButton("Generate", self)
        self._generate_button.clicked.connect(self._on_generate_clicked)

        self._save_button = QPushButton("Save ZIP As…", self)
        self._save_button.setEnabled(False)
        self._save_button.clicked.connect(self._on_save_clicked)

        self._status_label = QLabel("Idle", self)
        self._progress_bar = QProgressBar(self)
        self._progress_bar.setRange(0, 0)  # Indeterminate until real progress available
        self._progress_bar.setVisible(False)

        self._log_output = QTextEdit(self)
        self._log_output.setReadOnly(True)

        button_row = QHBoxLayout()
        button_row.addWidget(self._generate_button)
        button_row.addWidget(self._save_button)
        button_row.addStretch()

        status_row = QHBoxLayout()
        status_row.addWidget(QLabel("Status:", self))
        status_row.addWidget(self._status_label)
        status_row.addWidget(self._progress_bar)
        status_row.addStretch()

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Prompt", self))
        layout.addWidget(self._prompt_input, stretch=2)
        layout.addLayout(button_row)
        layout.addLayout(status_row)
        layout.addWidget(QLabel("Log", self))
        layout.addWidget(self._log_output, stretch=3)

        container = QWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self._current_thread: Optional[QThread] = None
        self._latest_zip: Optional[Path] = None

    def cleanup(self) -> None:
        if self._current_thread and self._current_thread.isRunning():
            self._current_thread.quit()
            self._current_thread.wait(1000)

    @Slot()
    def _on_generate_clicked(self) -> None:
        prompt = self._prompt_input.toPlainText().strip()
        if not prompt:
            self._append_log("Prompt required.")
            return

        if self._current_thread and self._current_thread.isRunning():
            self._append_log("A generation task is already running.")
            return

        self._set_busy(True)
        self._status_label.setText("Working…")
        self._append_log(f"Starting generation for prompt: {prompt}")

        worker = ScrapeWorker(prompt)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(self._on_generation_finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.failed.connect(self._on_generation_failed)
        worker.failed.connect(thread.quit)
        worker.failed.connect(worker.deleteLater)
        worker.log.connect(self._append_log)
        thread.finished.connect(thread.deleteLater)

        self._current_thread = thread
        thread.start()

    @Slot(Path)
    def _on_generation_finished(self, zip_path: Path) -> None:
        self._latest_zip = zip_path
        self._set_busy(False)
        self._save_button.setEnabled(True)
        self._status_label.setText("Completed")
        self._append_log(f"ZIP ready: {zip_path}")

    @Slot(str)
    def _on_generation_failed(self, message: str) -> None:
        self._set_busy(False)
        self._status_label.setText("Error")
        self._append_log(f"Error: {message}")

    @Slot()
    def _on_save_clicked(self) -> None:
        if not self._latest_zip:
            return

        suggested_name = self._latest_zip.name
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Generated ZIP",
            str(self._latest_zip.parent / suggested_name),
            "ZIP Files (*.zip)",
        )
        if not file_path:
            return

        destination = Path(file_path)
        destination.write_bytes(self._latest_zip.read_bytes())
        self._append_log(f"Saved archive to {destination}")

    def _append_log(self, message: str) -> None:
        self._log_output.append(message)

    def _set_busy(self, busy: bool) -> None:
        self._generate_button.setEnabled(not busy)
        self._progress_bar.setVisible(busy)
        self._progress_bar.setMinimum(0 if busy else 0)
        self._progress_bar.setMaximum(0 if busy else 1)
