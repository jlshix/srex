from dataclasses import dataclass

import asyncssh


@dataclass
class ExecContext:
    """Execution context passed to :meth:`Task.exec`.

    Attributes:
        conn: An established asyncssh connection to the target host.
    """

    conn: asyncssh.SSHClientConnection
