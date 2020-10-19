# stdlib
import csv
import os

# pyramid
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.exceptions import NotFound

# pypi
import six

# from six import BytesIO
from six import StringIO

# local
from .utils import get_performance_panel


# encoding used to write filedata
ENCODING = os.environ.get("pyramid_debugtoolbar_api_sqlalchemy_encoding", "utf-8")


# ==============================================================================


def _standardized_setup(request):
    """returns panel after some processing"""
    history = request.pdtb_history
    try:
        last_request_pair = history.last(1)[0]
    except IndexError:
        last_request_pair = None
        last_request_id = None
    else:
        last_request_id = last_request_pair[0]

    request_id = request.matchdict.get("request_id", last_request_id)
    toolbar = history.get(request_id, None)

    if not toolbar:
        raise NotFound

    panel = get_performance_panel(toolbar.panels)
    if not panel:
        raise NotFound

    return request_id, panel


@view_config(route_name="debugtoolbar.api_performance_csv.timing")
def csv_timing(request):
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
    csvfile.seek(0)
    as_csv = Response(
        content_type="text/csv", body=csvfile.read(), status=200, charset=ENCODING
    )
    as_csv.headers["Content-Disposition"] = str(
        "attachment; filename= performance-timing-%s.csv" % request_id
    )
    return as_csv


@view_config(route_name="debugtoolbar.api_performance_csv.function_calls")
def csv_function_calls(request):
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
    csvfile.seek(0)
    as_csv = Response(
        content_type="text/csv", body=csvfile.read(), status=200, charset=ENCODING
    )
    as_csv.headers["Content-Disposition"] = str(
        "attachment; filename= performance-function_calls-%s.csv" % request_id
    )
    return as_csv
