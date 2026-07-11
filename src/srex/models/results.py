from typing import Any

from pydantic import BaseModel


class TaskResult(BaseModel):
    """Result of executing a task."""

    task: Any
    rc: int = 0
    stdout: str = ""
    stderr: str = ""

    def name(self) -> str:
        return self.task.name
