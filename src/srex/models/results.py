from typing import Protocol

from pydantic import BaseModel

class TaskProtocol(Protocol):
    name: str

class TaskResult[T: TaskProtocol](BaseModel):
    """Result of executing a task."""

    task: T
    rc: int = 0
    stdout: str = ""
    stderr: str = ""

    def name(self) -> str:
        return self.task.name
