Use this branch to reproduce the import-time measurements on another system.

Recommended setup

1. Use Python 3.15.
2. Create a fresh virtual environment.
3. Install build dependencies: `pip install meson-python meson Cython==3.2.8 numpy matplotlib`.
4. Install this checkout into that environment.

Windows example

```powershell
py -3.15 -m venv .venv-pep810
.\.venv-pep810\Scripts\python.exe -m pip install meson-python meson Cython==3.2.8 numpy matplotlib
.\.venv-pep810\Scripts\python.exe -m pip install . --no-build-isolation
Set-Location $env:TEMP
C:\path\to\checkout\.venv-pep810\Scripts\python.exe C:\path\to\checkout\bench_pep810_io.py
```

Notes

- Run the benchmark from outside the repository checkout so `import pandas` resolves to the installed build, not the source tree.
- The script prints import-time results for `numpy`, plain `pandas`, `pd.read_csv(...)`, and `df.plot()`.
- The benchmark uses `python -X importtime`, so each cell is reported as `self / cumulative` time in milliseconds.
