from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonDatabase:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save({"tasks": []})

    def load(self) -> dict[str, Any]:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                value = json.load(file)
        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(f"Could not read task data at {self.path}: {error}") from error
        if not isinstance(value, dict) or not isinstance(value.get("tasks"), list):
            raise ValueError(f"Task data at {self.path} must contain a tasks list")
        return value

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(self.path.suffix + ".tmp")
        try:
            # Replace only after the complete JSON document has reached disk.
            with temporary_path.open("w", encoding="utf-8", newline="\n") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
                file.write("\n")
                file.flush()
                os.fsync(file.fileno())
            temporary_path.replace(self.path)
        finally:
            if temporary_path.exists():
                temporary_path.unlink()