from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
)

from services.task_manager import TaskManager


class AddTaskDialog(QDialog):
    def __init__(self, manager: TaskManager, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("Add task")
        self.setMinimumWidth(430)
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(15)
        heading = QLabel("New task")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(12)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("What needs to get done?")
        self.title_input.setMaxLength(180)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add a few details (optional)")
        self.description_input.setFixedHeight(92)
        self.due_enabled = QCheckBox("Set due date")
        self.due_date = QDateEdit(QDate.currentDate())
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("MMM d, yyyy")
        self.due_date.setEnabled(False)
        self.due_enabled.toggled.connect(self.due_date.setEnabled)
        date_row = QHBoxLayout()
        date_row.addWidget(self.due_enabled)
        date_row.addWidget(self.due_date, 1)
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText("Medium")
        form.addRow("Title", self.title_input)
        form.addRow("Description", self.description_input)
        form.addRow("Due date", date_row)
        form.addRow("Priority", self.priority)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save task")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save_task)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)
        self.title_input.setFocus()

    def save_task(self) -> None:
        try:
            self.manager.add(
                self.title_input.text(),
                self.description_input.toPlainText(),
                self.due_date.date().toString("yyyy-MM-dd") if self.due_enabled.isChecked() else None,
                self.priority.currentText(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Check task", str(error))
            self.title_input.setFocus()
            return
        self.accept()