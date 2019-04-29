# pyramid_debugtoolbar
from pyramid_debugtoolbar.panels.performance import PerformanceDebugPanel


# ==============================================================================


def get_performance_panel(toolbar_panels):
    # PY3 - `toolbar_panels` is a view, not a list
    for panel in toolbar_panels:
        if isinstance(panel, PerformanceDebugPanel):
            return panel
    return None
