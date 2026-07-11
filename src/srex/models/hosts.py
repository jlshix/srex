import os
from typing import Self
from urllib.parse import unquote, urlparse

from pydantic import BaseModel, SecretStr

from ..utils import read_file_to_model

from .base import ListModel


class Host(BaseModel):
    """A remote host definition."""

    hostname: str
    port: int = 22
    username: str = os.environ.get("USER", "")
    password: SecretStr | None = None

    @classmethod
    def from_netloc(cls, netloc: str) -> Self:
        """Parse a host from a netloc string like ``user:password@hostname:port``.

        Uses :func:`urllib.parse.urlparse` under the hood, with ``ssh://``
        prepended to make the netloc parseable.
        """
        parsed = urlparse(f"ssh://{netloc}")
        hostname = parsed.hostname or ""
        port = parsed.port or 22
        username = (
            unquote(parsed.username)
            if parsed.username
            else os.environ.get("USER", "")
        )
        password = (
            SecretStr(unquote(parsed.password)) if parsed.password else None
        )
        return cls.model_validate(
            {"hostname": hostname, "port": port, "username": username, "password": password}
        )


class Hosts(ListModel[Host]):
    """A collection of :class:`Host` instances."""

    @classmethod
    def from_param(cls, s: str, sep: str = ",") -> Self:
        """Build a :class:`Hosts` from a parameter string.

        If *s* starts with ``@`` the remainder is treated as a file path
        (JSON or YAML).  Otherwise *s* is split on *sep* and each item is
        parsed via :meth:`Host.from_netloc`.
        """
        if not s.startswith("@"):
            return cls.model_validate(
                [Host.from_netloc(item) for item in s.split(sep)]
            )
        return read_file_to_model(s[1:], cls)
