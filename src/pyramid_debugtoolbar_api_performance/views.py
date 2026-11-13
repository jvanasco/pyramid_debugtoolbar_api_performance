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
from six import PY2, StringIO, binary_type

# local
from .spreadsheet_utils import sanitize_spreadsheet_cell
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


def _spreadsheet_text(value):
    # type: (str) -> str
    """Sanitize a CSV text field using the export's encoding."""
    if isinstance(value, binary_type):
        value = value.decode(ENCODING)
    value = sanitize_spreadsheet_cell(value)
    return value.encode(ENCODING) if PY2 else value


def _csv_response(csvfile, report, request_id, spreadsheet):
    # type: (StringIO, str, str, bool) -> Response
    """Return a CSV attachment with a header-safe filename."""
    safe_id = re.sub(r"[^a-zA-Z0-9_-]", "_", request_id)
    suffix = "-spreadsheet" if spreadsheet else ""
    filename = "performance-%s-%s%s.csv" % (report, safe_id, suffix)
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

    spreadsheet = request.GET.get("spreadsheet") == "1"
    csvfile = StringIO()
    csvwriter = csv.writer(csvfile)
    for label, timing in panel.data["timing_rows"]:
        if spreadsheet:
            label = _spreadsheet_text(label)
        csvwriter.writerow((label, timing))
    return _csv_response(csvfile, "timing", request_id, spreadsheet)


@view_config(route_name="debugtoolbar.api_performance_csv.function_calls")
def csv_function_calls(request):
    # type: (Request) -> Response
    """Export profiler rows for a recorded request."""
    (request_id, panel) = _standardized_setup(request)

    spreadsheet = request.GET.get("spreadsheet") == "1"
    csvfile = StringIO()
    csvwriter = csv.writer(csvfile)
    if panel.data["stats"]:
        csvwriter.writerow(("Calls", "Total", "Percall", "Cumu", "CumuPer", "Func"))
        for row in panel.data["function_calls"]:
            filename = row["filename_long"]
            if spreadsheet:
                filename = _spreadsheet_text(filename)
            csvwriter.writerow(
                (
                    row["ncalls"],
                    row["tottime"],
                    row["percall"],
                    row["cumtime"],
                    row["percall_cum"],
                    filename,
                )
            )
    return _csv_response(csvfile, "function_calls", request_id, spreadsheet)
