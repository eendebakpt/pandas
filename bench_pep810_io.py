"""
Import-time benchmark helper for the PEP 810 lazy-import work.

Runs a small set of workloads under ``python -X importtime`` and reports both
the total import cost and the cumulative cost of the deferrable ``pandas.io``
backends. The same helper can be used on Python 3.15+ to measure real PEP 810
behavior, or on older Pythons as an upper bound where ``__lazy_modules__`` is a
no-op.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable
import re
import statistics
import subprocess
import sys

PY = sys.executable
N = 5

DEFERRABLE = [
    "pandas.io.clipboards",
    "pandas.io.excel",
    "pandas.io.feather_format",
    "pandas.io.html",
    "pandas.io.iceberg",
    "pandas.io.json",
    "pandas.io.orc",
    "pandas.io.parquet",
    "pandas.io.pickle",
    "pandas.io.pytables",
    "pandas.io.sas",
    "pandas.io.spss",
    "pandas.io.sql",
    "pandas.io.stata",
    "pandas.io.xml",
]

BENCHMARKS = [
    ("import numpy", "import numpy"),
    ("import pandas", "import pandas"),
    (
        "import pandas + pd.read_csv",
        "import pandas as pd; from io import StringIO; "
        "pd.read_csv(StringIO('a,b\\n1,2'))",
    ),
    (
        "import pandas + df.plot()",
        "import pandas as pd; df = pd.DataFrame({'a':[1,2,3],'b':[4,5,6]}); df.plot()",
    ),
]

_ROW = re.compile(r"import time:\s+(\d+)\s*\|\s+(\d+)\s*\|\s*([| ]*)(\S+)")


def import_time(code: str) -> tuple[float, dict[str, tuple[int, int]]]:
    """Run ``code`` under -X importtime; return (total_ms, {mod: (self_us, cum_us)})."""
    out = subprocess.run(
        [PY, "-X", "importtime", "-c", code],
        capture_output=True,
        text=True,
        check=True,
    ).stderr
    mods: dict[str, tuple[int, int]] = {}
    for line in out.splitlines():
        m = _ROW.match(line)
        if not m:
            continue
        self_us, cum_us, _, name = m.groups()
        mods[name] = (int(self_us), int(cum_us))
    total_us = sum(s for s, _ in mods.values())
    return total_us / 1000.0, mods


def cum(mods: dict[str, tuple[int, int]], names: Iterable[str]) -> float:
    total = 0.0
    for n in names:
        for k, (_, c) in mods.items():
            if k == n:
                total += c / 1000.0
                break
    return total


def bench(label: str, code: str) -> None:
    totals: list[float] = []
    deferrable_totals: list[float] = []
    last_mods: dict[str, tuple[int, int]] = {}
    for _ in range(N):
        total_ms, mods = import_time(code)
        totals.append(total_ms)
        deferrable_totals.append(cum(mods, DEFERRABLE))
        last_mods = mods
    total_med = statistics.median(totals)
    def_med = statistics.median(deferrable_totals)
    loaded = [m for m in DEFERRABLE if m in last_mods]
    saved_pct = def_med / total_med * 100 if total_med else 0.0
    print(
        f"\n[{label}]  total import={total_med:6.1f} ms   "
        f"deferrable={def_med:6.1f} ms   ({saved_pct:.0f}% of total)"
    )
    print(f"  loaded deferrable backends: {len(loaded)}/{len(DEFERRABLE)}")


def per_backend_breakdown() -> None:
    print("\nPer-backend cumulative cost during `import pandas`:")
    _, mods = import_time("import pandas")
    total = 0.0
    for mod in DEFERRABLE:
        c = mods.get(mod, (0, 0))[1] / 1000.0
        total += c
        print(f"  {mod:35s} {c:6.2f} ms")
    print(f"  {'TOTAL':35s} {total:6.2f} ms")


def main() -> None:
    print(f"Python: {sys.version.splitlines()[0]}")
    for label, code in BENCHMARKS:
        bench(label, code)
    per_backend_breakdown()


if __name__ == "__main__":
    main()
