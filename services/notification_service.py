from __future__ import annotations

from datetime import date

from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon

from services.task_manager import TaskManager


class NotificationService(QObject):
    def __init__(self, manager: TaskManager, show_window) -> None:
        super().__init__()
        self.manager = manager
        self.notified_today: set[str] = set()
        self.tray = QSystemTrayIcon(self)
        self.tray.setIcon(QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.tray.setToolTip("Annour's Todos")
        menu = QMenu()
        open_action = QAction("Open Annour's Todos", self)
        open_action.triggered.connect(show_window)
        exit_action = QAction("Quit", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: show_window() if reason == QSystemTrayIcon.ActivationReason.Trigger else None
        )
        self.tray.show()

        self.timer = QTimer(self)
        # Recheck periodically so tasks made due while the app is open are announced too.
        self.timer.setInterval(15 * 60 * 1000)
        self.timer.timeout.connect(self.check_due_tasks)
        self.timer.start()
        self.notify_overdue_on_startup()
        self.check_due_tasks()

    def notify_overdue_on_startup(self) -> None:
        today = date.today()
        overdue = [task for task in self.manager.all_tasks()
                   if not task.completed and task.due is not None and task.due < today]
        if overdue:
            count = len(overdue)
            self.tray.showMessage(
                "Overdue tasks",
                f"You have {count} overdue task{'s' if count != 1 else ''} to review.",
                QSystemTrayIcon.MessageIcon.Warning,
                9000,
            )

    def check_due_tasks(self) -> None:
        today = date.today()
        due = [task for task in self.manager.all_tasks()
               if not task.completed and task.due == today and task.id not in self.notified_today]
        for task in due:
            self.notified_today.add(task.id)
            self.tray.showMessage(
                "Task due today",
                task.title,
                QSystemTrayIcon.MessageIcon.Information,
                7000,
            )