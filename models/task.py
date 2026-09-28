from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any
from uuid import uuid4


PRIORITIES = ("Low", "Medium", "High")


@dataclass
class Task:
    title: str
    description: str = ""
    due_date: str | None = None
    priority: str = "Medium"
    id: str = ""
    created_at: str = ""
    updated_at: str = ""
    completed: bool = False
    deleted: bool = False

    def __post_init__(self) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        if not self.id:
            self.id = str(uuid4())
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
        self.title = self.title.strip()
        self.description = self.description.strip()
        if self.priority not in PRIORITIES:
            self.priority = "Medium"
        if self.due_date == "":
            self.due_date = None

    @property
    def due(self) -> date | None:
        if not self.due_date:
            return None
        try:
            return date.fromisoformat(self.due_date)
        except ValueError:
            return None

    @property
    def last_updated(self) -> datetime:
        try:
            return datetime.fromisoformat(self.updated_at)
        except ValueError:
            return datetime.min

    def touch(self) -> None:
        self.updated_at = datetime.now().isoformat(timespec="seconds")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Task:
        return cls(
            title=str(data.get("title", "")),
            description=str(data.get("description", "")),
            due_date=data.get("due_date") or None,
            priority=str(data.get("priority", "Medium")),
            id=str(data.get("id", "")),
            created_at=str(data.get("created_at", "")),
            updated_at=str(data.get("updated_at", "")),
            completed=bool(data.get("completed", False)),
            deleted=bool(data.get("deleted", False)),
        )