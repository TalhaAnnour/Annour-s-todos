from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
    QScrollArea, QToolButton, QVBoxLayout, QWidget,
)

from services.task_manager import TaskManager
from ui.add_task import AddTaskDialog
from ui.details import DetailsDialog
from ui.trash import TrashDialog
from ui.widgets import StatCard, TaskCard


class HomeWindow(QMainWindow):
    def __init__(self, manager: TaskManager) -> None:
        super().__init__()
        self.manager = manager
        self.active_filter = "All"
        self.setWindowTitle("Annour's Todos")
        self.resize(1040, 780)
        self.setMinimumSize(680, 560)

        root = QWidget()
        self.setCentralWidget(root)
        page = QVBoxLayout(root)
        page.setContentsMargins(34, 26, 34, 24)
        page.setSpacing(18)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        app_title = QLabel("Annour's Todos")
        app_title.setObjectName("pageTitle")
        subtitle = QLabel("A little more focus, every day.")
        subtitle.setObjectName("muted")
        titles.addWidget(app_title)
        titles.addWidget(subtitle)
        header.addLayout(titles, 1)
        self.trash_button = QPushButton("Trash")
        self.trash_button.clicked.connect(self.open_trash)
        header.addWidget(self.trash_button, 0, Qt.AlignmentFlag.AlignTop)
        page.addLayout(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search tasks and descriptions")
        self.search.textChanged.connect(self.refresh)
        page.addWidget(self.search)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(4)
        self.filter_buttons: dict[str, QToolButton] = {}
        for name in ("All", "Today", "Upcoming", "Completed"):
            button = QToolButton()
            button.setText(name)
            button.setObjectName("filterButton")
            button.setCheckable(True)
            button.setChecked(name == self.active_filter)
            button.clicked.connect(lambda checked=False, value=name: self.set_filter(value))
            self.filter_buttons[name] = button
            filter_row.addWidget(button)
        filter_row.addStretch(1)
        filter_row.addWidget(QLabel("Sort"))
        self.sort = QComboBox()
        self.sort.addItems(["Due date", "Priority", "Recently updated", "Created date"])
        self.sort.currentTextChanged.connect(self.refresh)
        self.sort.setMinimumWidth(160)
        filter_row.addWidget(self.sort)
        page.addLayout(filter_row)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(10)
        self.stats_cards = {
            "total": StatCard("Total tasks", "#F4F4F4"),
            "today": StatCard("Due today", "#FF7A00"),
            "completed": StatCard("Completed", "#73C991"),
            "pending": StatCard("Pending", "#E5B45E"),
        }
        for card in self.stats_cards.values():
            stats_layout.addWidget(card, 1)
        page.addLayout(stats_layout)

        section = QHBoxLayout()
        section_title = QLabel("Your tasks")
        section_title.setObjectName("sectionTitle")
        section.addWidget(section_title)
        section.addStretch(1)
        page.addLayout(section)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.task_container = QWidget()
        self.task_layout = QVBoxLayout(self.task_container)
        self.task_layout.setContentsMargins(0, 0, 4, 0)
        self.task_layout.setSpacing(10)
        self.scroll.setWidget(self.task_container)
        page.addWidget(self.scroll, 1)

        footer = QHBoxLayout()
        footer.addStretch(1)
        self.add_button = QPushButton("+  Add task")
        self.add_button.setObjectName("primaryButton")
        self.add_button.clicked.connect(self.open_add)
        footer.addWidget(self.add_button)
        page.addLayout(footer)
        self.refresh()

    def set_filter(self, name: str) -> None:
        self.active_filter = name
        for label, button in self.filter_buttons.items():
            button.setChecked(label == name)
        self.refresh()

    def refresh(self, *_args) -> None:
        stats = self.manager.stats()
        for name, card in self.stats_cards.items():
            card.set_value(stats[name])
        while self.task_layout.count():
            item = self.task_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        tasks = self.manager.query(self.active_filter, self.search.text(), self.sort.currentText())
        if not tasks:
            empty = QLabel("No tasks here yet" if not self.search.text() else "No matching tasks")
            empty.setObjectName("muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setMinimumHeight(110)
            self.task_layout.addWidget(empty)
        for task in tasks:
            card = TaskCard(task)
            card.clicked.connect(self.open_details)
            card.completion_changed.connect(self.toggle_task)
            self.task_layout.addWidget(card)
        self.task_layout.addStretch(1)

    def toggle_task(self, task_id: str, completed: bool) -> None:
        self.manager.set_completed(task_id, completed)
        self.refresh()

    def open_add(self) -> None:
        if AddTaskDialog(self.manager, self).exec():
            self.refresh()

    def open_details(self, task_id: str) -> None:
        task = self.manager.get(task_id)
        if task is not None:
            DetailsDialog(self.manager, task, self).exec()
            self.refresh()

    def open_trash(self) -> None:
        TrashDialog(self.manager, self.refresh, self).exec()
        self.refresh()