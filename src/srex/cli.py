import asyncio
from pathlib import Path

import typer

from .models.hosts import Hosts
from .models.tasks import Tasks
from .runner import HostRunResult, run

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Simple remote execution tool."""


@app.command("run")
def run_command(
    hosts: str = typer.Option(
        ...,
        "--hosts",
        "-H",
        help="Hosts as user:password@host:port entries, or @hosts.yaml.",
    ),
    tasks: Path = typer.Option(
        ...,
        "--tasks",
        "-t",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="YAML file containing task definitions.",
    ),
) -> None:
    """Run tasks from a YAML file on one or more SSH hosts."""
    parsed_hosts = Hosts.from_param(hosts)
    parsed_tasks = Tasks.from_param(f"@{tasks}")
    results = asyncio.run(run(parsed_hosts.root, parsed_tasks.root))
    _print_results(results)

    if any(result.failed for result in results):
        raise typer.Exit(1)


def _print_results(results: list[HostRunResult]) -> None:
    for host_result in results:
        typer.echo(f"[{host_result.host.hostname}]")
        for result in host_result.results:
            typer.echo(f"- {result.name()}: rc={result.rc}")
            if result.stdout:
                typer.echo(result.stdout.rstrip())
            if result.stderr:
                typer.echo(result.stderr.rstrip(), err=True)


if __name__ == "__main__":
    app()
