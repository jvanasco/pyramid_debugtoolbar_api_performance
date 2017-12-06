# local
from .panels import PerformanceCsvDebugPanel


__VERSION__ = '0.1.1'


# ==============================================================================


def includeme(config):
    config.registry.settings['debugtoolbar.extra_panels'].append(PerformanceCsvDebugPanel)
    config.add_route('debugtoolbar.api_performance_csv.function_calls', '/api-performance/function_calls-{request_id}.csv')
    config.add_route('debugtoolbar.api_performance_csv.timing', '/api-performance/timing-{request_id}.csv')
    config.scan('pyramid_debugtoolbar_api_performance.views')
    config.commit()


# ==============================================================================
