from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from services.task_manager import TaskManager


class TrashDialog(QDialog):
    def __init__(self, manager: TaskManager, on_change, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.on_change = on_change
        self.setWindowTitle("Trash")
        self.resize(650, 500)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        header = QHBoxLayout()
        title = QLabel("Trash")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        self.empty_button = QPushButton("Empty trash")
        self.empty_button.setObjectName("dangerButton")
        self.empty_button.clicked.connect(self.empty_trash)
        header.addWidget(self.empty_button)
        close = QPushButton("Close")
        close.clicked.connect(self.accept)
        header.addWidget(close)
        layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.items = QVBoxLayout(self.container)
        self.items.setContentsMargins(0, 8, 4, 0)
        self.items.setSpacing(9)
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll, 1)
        self.refresh()

    def refresh(self) -> None:
        while self.items.count():
            item = self.items.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        tasks = self.manager.trash()
        self.empty_button.setEnabled(bool(tasks))
        if not tasks:
            empty = QLabel("Trash is empty")
            empty.setObjectName("muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items.addWidget(empty)
        for task in tasks:
            row = QFrame()
            row.setObjectName("taskCard")
            row_layout = QHBoxLayout(row)
            label = QLabel(task.title)
            label.setWordWrap(True)
            row_layout.addWidget(label, 1)
            restore = QPushButton("Restore")
            restore.clicked.connect(lambda checked=False, task_id=task.id: self.restore(task_id))
            remove = QPushButton("Delete forever")
            remove.setObjectName("dangerButton")
            remove.clicked.connect(lambda checked=False, task_id=task.id: self.delete_forever(task_id))
            row_layout.addWidget(restore)
            row_layout.addWidget(remove)
            self.items.addWidget(row)
        self.items.addStretch(1)

    def restore(self, task_id: str) -> None:
        self.manager.restore(task_id)
        self.on_change()
        self.refresh()

    def delete_forever(self, task_id: str) -> None:
        task = self.manager.get(task_id)
        if task is None:
            return
        answer = QMessageBox.question(
            self, "Delete permanently?", f"Permanently delete \"{task.title}\"? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.manager.delete_permanently(task_id)
            self.on_change()
            self.refresh()

    def empty_trash(self) -> None:
        answer = QMessageBox.question(
            self, "Empty trash?", "Permanently delete every task in the trash? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.manager.empty_trash()
            self.on_change()
            self.refresh()