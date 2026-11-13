# stdlib
import csv
import os
import re

# pyramid
from pyramid.response import Response

from pyramid.request import Request
from pyramid_debugtoolbar.panels.performance import PerformanceDebugPanel
from pyramid.view import view_config
from pyramid.exceptions import NotFound

# Python 2's csv module requires a byte buffer.
from six import StringIO

# local
from .utils import get_performance_panel


# encoding used to write filedata
ENCODING = os.environ.get("pyramid_debugtoolbar_api_sqlalchemy_encoding", "utf-8")


# ==============================================================================


def _standardized_setup(request):
    # type: (Request) -> tuple[str, PerformanceDebugPanel]
    """Resolve the performance panel for the requested history entry."""
    request_id = request.matchdict["request_id"]
    toolbar = request.pdtb_history.get(request_id, None)
    if toolbar is None:
        raise NotFound

    panel = get_performance_panel(toolbar.panels)
    if panel is None or not panel.data:
        raise NotFound

    return request_id, panel


def _csv_response(csvfile, report, request_id):
    # type: (StringIO, str, str) -> Response
    """Return a CSV attachment with a header-safe filename."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", request_id)
    filename = "performance-%s-%s.csv" % (report, safe_id)
    response = Response(
        content_type="text/csv", body=csvfile.getvalue(), charset=ENCODING
    )
    response.headers["Content-Disposition"] = str('attachment; filename="%s"' % filename)
    response.cache_control.no_store = True
    return response


@view_config(route_name="debugtoolbar.api_performance_csv.timing")
def csv_timing(request):
    # type: (Request) -> Response
    """Export timing rows for a recorded request."""
    (request_id, panel) = _standardized_setup(request)

    csvfile = StringIO()
    csvwriter = csv.writer(csvfile)
    for row in panel.data["timing_rows"]:
        # row is `label, timing`
        # example:
        # 'timing_rows': (('User CPU time', '119.678 msec'),
        #                 ('System CPU time', '64.695 msec'),
        #                 ('Total CPU time', '184.373 msec'),
        #                 ('Elapsed time', '205.099 msec'),
        #                 ('Context switches', '19 voluntary, 1233 involuntary')
        #                 )
        csvwriter.writerow(row)
    return _csv_response(csvfile, "timing", request_id)


@view_config(route_name="debugtoolbar.api_performance_csv.function_calls")
def csv_function_calls(request):
    # type: (Request) -> Response
    """Export profiler rows for a recorded request."""
    (request_id, panel) = _standardized_setup(request)

    csvfile = StringIO()
    csvwriter = csv.writer(csvfile)
    if panel.data["stats"]:
        csvwriter.writerow(("Calls", "Total", "Percall", "Cumu", "CumuPer", "Func"))
        for row in panel.data["function_calls"]:
            csvwriter.writerow(
                (
                    row["ncalls"],
                    row["tottime"],
                    row["percall"],
                    row["cumtime"],
                    row["percall_cum"],
                    row["filename_long"],
                )
            )
    return _csv_response(csvfile, "function_calls", request_id)
