import json
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")


def read_raw(path: str | Path) -> Any:
    """Read a JSON or YAML file and return its raw contents."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        return json.loads(path.read_text())

    if suffix in (".yaml", ".yml"):
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML files; install it with `pip install pyyaml`"
            ) from None
        return yaml.safe_load(path.read_text())

    raise ValueError(
        f"Unsupported file format: {suffix!r}; expected .json, .yaml, or .yml"
    )


def read_file_to_model(path: str | Path, model: type[T]) -> T:
    """Read a file and validate its contents as *model*."""
    return model.model_validate(read_raw(path))
