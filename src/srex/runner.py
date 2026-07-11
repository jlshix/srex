from dataclasses import dataclass, field
from typing import Sequence

import asyncssh

from .models.contexts import ExecContext
from .models.hosts import Host
from .models.results import TaskResult
from .models.tasks import Task


@dataclass
class HostRunResult:
    """Results for all tasks executed on one host."""

    host: Host
    results: list[TaskResult] = field(default_factory=list)
    failed: bool = False


async def run(hosts: Sequence[Host], tasks: Sequence[Task]) -> list[HostRunResult]:
    """Run *tasks* on every host in order."""
    results: list[HostRunResult] = []
    for host in hosts:
        results.append(await run_host(host, tasks))
    return results


async def run_host(host: Host, tasks: Sequence[Task]) -> HostRunResult:
    """Run *tasks* on a single host."""
    host_result = HostRunResult(host=host)
    password = host.password.get_secret_value() if host.password else None

    async with asyncssh.connect(
        host.hostname,
        port=host.port,
        username=host.username,
        password=password,
    ) as conn:
        ctx = ExecContext(conn=conn)
        render_ctx = _render_context(host)
        for task in tasks:
            rendered_task = task.render(render_ctx)
            result = await rendered_task.exec(ctx)
            host_result.results.append(result)

            if result.rc != 0 and not rendered_task.ignore_errors:
                host_result.failed = True
                break

    return host_result


def _render_context(host: Host) -> dict[str, object]:
    return {
        "host": {
            "hostname": host.hostname,
            "port": host.port,
            "username": host.username,
        },
        "hostname": host.hostname,
        "port": host.port,
        "username": host.username,
    }
