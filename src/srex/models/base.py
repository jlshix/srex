from pydantic import RootModel


class ListModel[T](RootModel[list[T]]):
    """A generic list model that wraps ``RootModel[list[T]]``."""
