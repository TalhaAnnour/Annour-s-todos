from __future__ import annotations

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDateEdit, QDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QTextEdit, QVBoxLayout,
)

from models.task import Task
from services.task_manager import TaskManager


class DetailsDialog(QDialog):
    def __init__(self, manager: TaskManager, task: Task, parent=None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.task = task
        self.setWindowTitle("Task details")
        self.setMinimumWidth(460)
        self.setModal(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(15)
        heading = QLabel("Task details")
        heading.setObjectName("sectionTitle")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setSpacing(12)
        self.title_input = QLineEdit(task.title)
        self.title_input.setMaxLength(180)
        self.description_input = QTextEdit(task.description)
        self.description_input.setFixedHeight(110)
        self.due_enabled = QCheckBox("Set due date")
        self.due_date = QDateEdit(QDate.currentDate())
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("MMM d, yyyy")
        self.due_enabled.setChecked(task.due is not None)
        if task.due:
            self.due_date.setDate(QDate(task.due.year, task.due.month, task.due.day))
        self.due_date.setEnabled(self.due_enabled.isChecked())
        self.due_enabled.toggled.connect(self.due_date.setEnabled)
        date_row = QHBoxLayout()
        date_row.addWidget(self.due_enabled)
        date_row.addWidget(self.due_date, 1)
        self.priority = QComboBox()
        self.priority.addItems(["Low", "Medium", "High"])
        self.priority.setCurrentText(task.priority)
        form.addRow("Title", self.title_input)
        form.addRow("Description", self.description_input)
        form.addRow("Due date", date_row)
        form.addRow("Priority", self.priority)
        layout.addLayout(form)
        self.completed = QCheckBox("Mark as completed")
        self.completed.setChecked(task.completed)
        layout.addWidget(self.completed)

        buttons = QHBoxLayout()
        delete = QPushButton("Move to trash")
        delete.setObjectName("dangerButton")
        delete.clicked.connect(self.delete_task)
        buttons.addWidget(delete)
        buttons.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save changes")
        save.setObjectName("primaryButton")
        save.clicked.connect(self.save_task)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def save_task(self) -> None:
        try:
            self.manager.update(
                self.task.id,
                title=self.title_input.text(),
                description=self.description_input.toPlainText(),
                due_date=self.due_date.date().toString("yyyy-MM-dd") if self.due_enabled.isChecked() else None,
                priority=self.priority.currentText(),
                completed=self.completed.isChecked(),
            )
        except ValueError as error:
            QMessageBox.warning(self, "Check task", str(error))
            self.title_input.setFocus()
            return
        self.accept()

    def delete_task(self) -> None:
        answer = QMessageBox.question(
            self,
            "Move to trash?",
            f"Move \"{self.task.title}\" to the trash? You can restore it later.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.manager.move_to_trash(self.task.id)
            self.accept()