from __future__ import annotations

import sys
import os
import shutil
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

from services.json_database import JsonDatabase
from services.notification_service import NotificationService
from services.task_manager import TaskManager
from ui.home import HomeWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Annour's Todos")
    app.setQuitOnLastWindowClosed(False)
    resource_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    stylesheet = resource_dir / "styles" / "dark_orange.qss"
    app.setStyleSheet(stylesheet.read_text(encoding="utf-8"))
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    data_dir = local_app_data / "AnnoursTodos"
    task_file = data_dir / "tasks.json"
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
        if not task_file.exists():
            shutil.copyfile(resource_dir / "data" / "tasks.example.json", task_file)
        manager = TaskManager(JsonDatabase(task_file))
    except (OSError, ValueError) as error:
        QMessageBox.critical(None, "Task data error", str(error))
        return 1
    window = HomeWindow(manager)
    window.show()
    notifications = NotificationService(manager, window.showNormal)
    app._notification_service = notifications
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())