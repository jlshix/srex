import inspect
from abc import ABC, abstractmethod
from typing import Any, Literal, Self

from jinja2 import Environment
from pydantic import BaseModel, ValidationError

from ..utils import read_raw

from .base import ListModel
from .contexts import ExecContext

_JINJA2_ENV = Environment()
_JINJA2_MARKERS = ("{{", "{%", "{#")
_TASK_REGISTRY: dict[str, type["Task"]] = {}


class Task(BaseModel, ABC):
    """Base task definition."""

    name: str
    action: str
    ignore_errors: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and "action" in cls.__dict__:
            _TASK_REGISTRY[cls.__dict__["action"]] = cls

    @abstractmethod
    async def exec(self, ctx: ExecContext) -> "TaskResult":
        """Execute the task and return the result."""
        ...

    def render(self, ctx: dict[str, Any]) -> Self:
        """Render Jinja2 templates in all :class:`str` fields using *ctx*.

        Fields whose value does not contain any Jinja2 markers are left
        untouched.  Returns a new instance (or ``self`` if nothing changed).
        """
        updates: dict[str, str] = {}
        for field_name, field_info in self.model_fields.items():
            if field_info.annotation is not str:
                continue
            value: str = getattr(self, field_name)
            if not _needs_render(value):
                continue
            updates[field_name] = _JINJA2_ENV.from_string(value).render(**ctx)
        if not updates:
            return self
        return self.model_copy(update=updates)


def _needs_render(value: str) -> bool:
    return any(marker in value for marker in _JINJA2_MARKERS)


class TaskResult(BaseModel):
    """Result of executing a task."""

    task: Task
    rc: int
    stdout: str = ""
    stderr: str = ""


class ShellTask(Task):
    """Run a shell command on the remote host."""

    action: Literal["shell"] = "shell"
    command: str

    async def exec(self, ctx: ExecContext) -> TaskResult:
        result = await ctx.conn.run(self.command, check=False)
        return TaskResult(
            task=self,
            rc=result.exit_status,
            stdout=result.stdout or "",
            stderr=result.stderr or "",
        )


class FetchTask(Task):
    """Fetch a file from the remote host to a local path."""

    action: Literal["fetch"] = "fetch"
    src: str
    dst: str

    async def exec(self, ctx: ExecContext) -> TaskResult:
        async with ctx.conn.start_sftp_client() as sftp:
            await sftp.get(self.src, self.dst)
        return TaskResult(task=self, rc=0)


def _dispatch(item: dict[str, Any]) -> Task:
    """Instantiate the correct :class:`Task` subclass based on ``action``."""
    action = item.get("action")
    task_cls = _TASK_REGISTRY.get(action)
    if task_cls is None:
        raise ValueError(f"Unknown task action: {action!r}")
    return task_cls.model_validate(item)


class Tasks[T: Task](ListModel[T]):
    """A collection of :class:`Task` instances."""

    @classmethod
    def from_param(cls, s: str) -> Self:
        """Build a :class:`Tasks` from a file path prefixed with ``@``.

        The file (JSON or YAML) must contain a list of task dicts.  Each
        dict is dispatched to the registered :class:`Task` subclass using
        its ``action`` field.
        """
        raw = read_raw(s[1:])
        return cls.model_validate([_dispatch(item) for item in raw])
