from __future__ import annotations

from datetime import date
from typing import Iterable

from models.task import PRIORITIES, Task
from services.json_database import JsonDatabase


class TaskManager:
    def __init__(self, database: JsonDatabase) -> None:
        self.database = database
        self._tasks = [Task.from_dict(item) for item in database.load()["tasks"]]

    def _save(self) -> None:
        self.database.save({"tasks": [task.to_dict() for task in self._tasks]})

    def all_tasks(self, include_deleted: bool = False) -> list[Task]:
        return [task for task in self._tasks if include_deleted or not task.deleted]

    def get(self, task_id: str) -> Task | None:
        return next((task for task in self._tasks if task.id == task_id), None)

    def add(self, title: str, description: str = "", due_date: str | None = None,
            priority: str = "Medium") -> Task:
        if not title.strip():
            raise ValueError("A task title is required.")
        if priority not in PRIORITIES:
            raise ValueError("Choose Low, Medium, or High priority.")
        task = Task(title=title, description=description, due_date=due_date, priority=priority)
        self._tasks.append(task)
        self._save()
        return task

    def update(self, task_id: str, *, title: str, description: str,
               due_date: str | None, priority: str, completed: bool) -> Task:
        task = self.get(task_id)
        if task is None or task.deleted:
            raise ValueError("This task is no longer available.")
        if not title.strip():
            raise ValueError("A task title is required.")
        if priority not in PRIORITIES:
            raise ValueError("Choose Low, Medium, or High priority.")
        task.title = title.strip()
        task.description = description.strip()
        task.due_date = due_date or None
        task.priority = priority
        task.completed = completed
        task.touch()
        self._save()
        return task

    def set_completed(self, task_id: str, completed: bool) -> None:
        task = self.get(task_id)
        if task is None or task.deleted:
            return
        task.completed = completed
        task.touch()
        self._save()

    def move_to_trash(self, task_id: str) -> None:
        task = self.get(task_id)
        if task is not None and not task.deleted:
            task.deleted = True
            task.touch()
            self._save()

    def restore(self, task_id: str) -> None:
        task = self.get(task_id)
        if task is not None and task.deleted:
            task.deleted = False
            task.touch()
            self._save()

    def delete_permanently(self, task_id: str) -> None:
        self._tasks = [task for task in self._tasks if task.id != task_id]
        self._save()

    def empty_trash(self) -> None:
        self._tasks = [task for task in self._tasks if not task.deleted]
        self._save()

    def query(self, filter_name: str = "All", search: str = "",
              sort_name: str = "Due date") -> list[Task]:
        today = date.today()
        needle = search.strip().casefold()
        tasks: Iterable[Task] = (task for task in self._tasks if not task.deleted)
        if filter_name == "Today":
            tasks = (task for task in tasks if not task.completed and task.due == today)
        elif filter_name == "Upcoming":
            tasks = (task for task in tasks if not task.completed and task.due is not None and task.due > today)
        elif filter_name == "Completed":
            tasks = (task for task in tasks if task.completed)
        if needle:
            tasks = (task for task in tasks if needle in task.title.casefold()
                     or needle in task.description.casefold())
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sorters = {
            "Due date": lambda task: (task.due is None, task.due or date.max),
            "Priority": lambda task: (priority_order.get(task.priority, 1), task.due is None,
                                      task.due or date.max),
            "Recently updated": lambda task: task.last_updated,
            "Created date": lambda task: task.created_at,
        }
        visible = list(tasks)
        if sort_name in ("Recently updated", "Created date"):
            visible.sort(key=sorters[sort_name], reverse=True)
        else:
            visible.sort(key=sorters.get(sort_name, sorters["Due date"]))
        # A stable second sort preserves the selected order within each completion group.
        visible.sort(key=lambda task: task.completed)
        return visible

    def stats(self) -> dict[str, int]:
        active = [task for task in self._tasks if not task.deleted]
        today = date.today()
        return {
            "total": len(active),
            "today": sum(not task.completed and task.due == today for task in active),
            "completed": sum(task.completed for task in active),
            "pending": sum(not task.completed for task in active),
        }

    def trash(self) -> list[Task]:
        return sorted((task for task in self._tasks if task.deleted),
                      key=lambda task: task.last_updated, reverse=True)