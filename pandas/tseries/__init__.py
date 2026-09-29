from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # import modules that have public classes/functions:
    from pandas.tseries import (
        frequencies,
        offsets,
    )

    # and mark only those modules as public
    __all__ = ["frequencies", "offsets"]


def __getattr__(name: str) -> object:
    if name in {"frequencies", "offsets"}:
        return import_module(f"pandas.tseries.{name}")
    raise AttributeError(f"module 'pandas.tseries' has no attribute '{name}'")


def __dir__() -> list[str]:
    return [*list(globals().keys()), "frequencies", "offsets"]
