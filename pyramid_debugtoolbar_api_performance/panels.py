# stdlib

# pyramid
from pyramid.threadlocal import get_current_request
from pyramid.decorator import reify

# pyramid_debugtoolbar
from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import STATIC_PATH
from pyramid_debugtoolbar.utils import ROOT_ROUTE_NAME

# local
from .utils import get_performance_panel

# ==============================================================================


_ = lambda x: x


class PerformanceCsvDebugPanel(DebugPanel):
    """
    Panel that displays a link to Performance downloads
    """

    name = "performance-csv"
    template = "pyramid_debugtoolbar_api_performance:templates/performance_csv.dbtmako"
    title = _("Performance CSV")
    nav_title = _("Performance CSV")

    def __init__(self, original_request):
        self.token = original_request.registry.pdtb_token
        self.pdtb_id = original_request.pdtb_id

    @reify
    def _performance_panel(self):
        # utility for when we can't explicitly access the request
        request = get_current_request()
        performance_panel = get_performance_panel(request.toolbar_panels.values())
        return performance_panel

    @property
    def has_content(self):
        performance_panel = self._performance_panel
        if performance_panel and performance_panel.data:
            return True
        return False

    @property
    def nav_subtitle(self):
        return ""

    def render_content(self, request):
        performance_panel = get_performance_panel(request.toolbar_panels.values())
        if not performance_panel:
            return "No `performance` panel in request."
        if not performance_panel.data:
            return "No data in executed in request."
        # our template might want to reference this for button visibility
        self.data = performance_panel.data
        return super(PerformanceCsvDebugPanel, self).render_content(request)

    def render_vars(self, request):
        return {
            "route_url": request.route_url,
            "static_path": request.static_url(STATIC_PATH),
            "root_path": request.route_url(ROOT_ROUTE_NAME),
            "pdtb_id": self.pdtb_id,
        }
