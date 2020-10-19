# local
from .panels import PerformanceCsvDebugPanel


__VERSION__ = "0.3.0"


# ==============================================================================


def includeme(config):
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
