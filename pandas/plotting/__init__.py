"""
Plotting public API.

Authors of third-party plotting backends should implement a module with a
public ``plot(data, kind, **kwargs)``. The parameter `data` will contain
the data structure and can be a `Series` or a `DataFrame`. For example,
for ``df.plot()`` the parameter `data` will contain the DataFrame `df`.
In some cases, the data structure is transformed before being sent to
the backend (see PlotAccessor.__call__ in pandas/plotting/_core.py for
the exact transformations).

The parameter `kind` will be one of:

- line
- bar
- barh
- box
- hist
- kde
- area
- pie
- scatter
- hexbin

See the pandas API reference for documentation on each kind of plot.

Any other keyword argument is currently assumed to be backend specific,
but some parameters may be unified and added to the signature in the
future (e.g. `title` which should be useful for any backend).

Currently, all the Matplotlib functions in pandas are accessed through
the selected backend. For example, `pandas.plotting.boxplot` (equivalent
to `DataFrame.boxplot`) is also accessed in the selected backend. This
is expected to change, and the exact API is under discussion. But with
the current version, backends are expected to implement the next functions:

- plot (describe above, used for `Series.plot` and `DataFrame.plot`)
- hist_series and hist_frame (for `Series.hist` and `DataFrame.hist`)
- boxplot (`pandas.plotting.boxplot(df)` equivalent to `DataFrame.boxplot`)
- boxplot_frame and boxplot_frame_groupby
- register and deregister (register converters for the tick formats)
- Plots not called as `Series` and `DataFrame` methods:
  - table
  - andrews_curves
  - autocorrelation_plot
  - bootstrap_plot
  - lag_plot
  - parallel_coordinates
  - radviz
  - scatter_matrix

Use the code in pandas/plotting/_matplotlib.py and
https://github.com/pyviz/hvplot as a reference on how to write a backend.

For the discussion about the API see
https://github.com/pandas-dev/pandas/issues/26747.
"""

from importlib import import_module

_ATTR_TO_MODULE = {
    "PlotAccessor": ("pandas.plotting._core", "PlotAccessor"),
    "andrews_curves": ("pandas.plotting._misc", "andrews_curves"),
    "autocorrelation_plot": ("pandas.plotting._misc", "autocorrelation_plot"),
    "bootstrap_plot": ("pandas.plotting._misc", "bootstrap_plot"),
    "boxplot": ("pandas.plotting._core", "boxplot"),
    "boxplot_frame": ("pandas.plotting._core", "boxplot_frame"),
    "boxplot_frame_groupby": ("pandas.plotting._core", "boxplot_frame_groupby"),
    "deregister_matplotlib_converters": (
        "pandas.plotting._misc",
        "deregister",
    ),
    "hist_frame": ("pandas.plotting._core", "hist_frame"),
    "hist_series": ("pandas.plotting._core", "hist_series"),
    "lag_plot": ("pandas.plotting._misc", "lag_plot"),
    "parallel_coordinates": ("pandas.plotting._misc", "parallel_coordinates"),
    "plot_params": ("pandas.plotting._misc", "plot_params"),
    "radviz": ("pandas.plotting._misc", "radviz"),
    "register_matplotlib_converters": ("pandas.plotting._misc", "register"),
    "scatter_matrix": ("pandas.plotting._misc", "scatter_matrix"),
    "table": ("pandas.plotting._misc", "table"),
}

__all__ = [
    "PlotAccessor",
    "andrews_curves",
    "autocorrelation_plot",
    "bootstrap_plot",
    "boxplot",
    "boxplot_frame",
    "boxplot_frame_groupby",
    "deregister_matplotlib_converters",
    "hist_frame",
    "hist_series",
    "lag_plot",
    "parallel_coordinates",
    "plot_params",
    "radviz",
    "register_matplotlib_converters",
    "scatter_matrix",
    "table",
]


def __getattr__(name: str) -> object:
    try:
        module_name, attr_name = _ATTR_TO_MODULE[name]
    except KeyError as err:
        raise AttributeError(
            f"module 'pandas.plotting' has no attribute '{name}'"
        ) from err

    return getattr(import_module(module_name), attr_name)


def __dir__() -> list[str]:
    return [*list(globals().keys()), *_ATTR_TO_MODULE.keys()]
