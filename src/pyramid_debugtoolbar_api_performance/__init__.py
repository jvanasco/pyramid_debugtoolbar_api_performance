# type: from pyramid.config import Configurator
from ._version import __VERSION__


# ==============================================================================


def includeme(config):
    # type: (Configurator) -> None
    """Register the CSV panel and routes with the debug toolbar."""
    # Older setuptools imports this package to read its version at build time.
    from .panels import PerformanceCsvDebugPanel

    config.add_debugtoolbar_panel(PerformanceCsvDebugPanel)
    config.add_route(
        "debugtoolbar.api_performance_csv.function_calls",
        "/api-performance/function_calls-{request_id}.csv",
    )
    config.add_route(
        "debugtoolbar.api_performance_csv.timing",
        "/api-performance/timing-{request_id}.csv",
    )
    config.scan("pyramid_debugtoolbar_api_performance.views")
    config.commit()


# ==============================================================================
