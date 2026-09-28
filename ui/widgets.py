from __future__ import annotations

from datetime import date

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from models.task import Task


class StatCard(QFrame):
    def __init__(self, label: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("statCard")
        self.setMinimumHeight(88)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 13, 16, 13)
        self.value_label = QLabel("0")
        self.value_label.setStyleSheet(f"color: {accent}; font-size: 19pt; font-weight: 700")
        caption = QLabel(label)
        caption.setObjectName("muted")
        layout.addWidget(self.value_label)
        layout.addWidget(caption)

    def set_value(self, value: int) -> None:
        self.value_label.setText(str(value))


class TaskCard(QFrame):
    clicked = Signal(str)
    completion_changed = Signal(str, bool)

    def __init__(self, task: Task) -> None:
        super().__init__()
        self.task_id = task.id
        self.setObjectName("taskCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.installEventFilter(self)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 13, 16, 13)
        row.setSpacing(13)
        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.setCursor(Qt.CursorShape.PointingHandCursor)
        checkbox.toggled.connect(lambda checked: self.completion_changed.emit(self.task_id, checked))
        row.addWidget(checkbox, 0, Qt.AlignmentFlag.AlignTop)

        content = QWidget()
        content.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        content.setStyleSheet("background: transparent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        title = QLabel(task.title)
        title.setObjectName("sectionTitle")
        if task.completed:
            title.setStyleSheet("color: #888888; text-decoration: line-through")
        content_layout.addWidget(title)
        if task.description:
            description = QLabel(task.description)
            description.setObjectName("muted")
            description.setWordWrap(True)
            description.setMaximumHeight(42)
            content_layout.addWidget(description)

        details = QHBoxLayout()
        details.setSpacing(12)
        due_text = task.due.strftime("%b %d, %Y") if task.due else "No due date"
        if task.due == date.today() and not task.completed:
            due_text = "Today"
        elif task.due and task.due < date.today() and not task.completed:
            due_text = f"Overdue · {due_text}"
        due_label = QLabel(due_text)
        due_label.setObjectName("muted")
        priority = QLabel(task.priority)
        priority_colors = {"Low": "#73C991", "Medium": "#E5B45E", "High": "#FF845E"}
        priority.setStyleSheet(
            f"color: {priority_colors.get(task.priority, '#E5B45E')}; "
            "background: #242424; border-radius: 7px; padding: 3px 8px"
        )
        updated = QLabel(f"Updated {task.last_updated.strftime('%b %d')}")
        updated.setObjectName("muted")
        details.addWidget(due_label)
        details.addWidget(priority)
        details.addWidget(updated)
        details.addStretch(1)
        content_layout.addLayout(details)
        row.addWidget(content, 1)

    def eventFilter(self, watched: object, event: QEvent) -> bool:
        if watched is self and event.type() == QEvent.Type.MouseButtonRelease:
            if getattr(event, "button", lambda: None)() == Qt.MouseButton.LeftButton:
                self.clicked.emit(self.task_id)
        return super().eventFilter(watched, event)