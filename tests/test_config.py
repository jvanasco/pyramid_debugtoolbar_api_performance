from __future__ import print_function
from __future__ import unicode_literals

# stdlib
import re
import unittest

# pyramid testing requirements
from pyramid import testing
from pyramid.response import Response
from pyramid.request import Request


# ------------------------------------------------------------------------------


# used to ensure the toolbar link is injected into requests
re_toolbar_link = re.compile(r'(?:href="http://localhost)(/_debug_toolbar/[\d]+)"')
re_csv_timing_link = re.compile(
    r'href="(/_debug_toolbar/api-performance/timing-([\d]+).csv)"'
)
re_csv_function_link = re.compile(
    r'href="(/_debug_toolbar/api-performance/function_calls-([\d]+).csv)"'
)


class TestDebugtoolbarPanel(unittest.TestCase):
    def setUp(self):
        self.config = config = testing.setUp()
        config.add_settings(
            {"debugtoolbar.includes": ["pyramid_debugtoolbar_api_performance"]}
        )
        config.include("pyramid_debugtoolbar")
        self.settings = config.registry.settings

        # create a view
        def empty_view(request):
            return Response(
                "<html><head></head><body>OK</body></html>", content_type="text/html"
            )

        config.add_view(empty_view)
        config.add_notfound_view(lambda request: Response(status=404))

    def tearDown(self):
        testing.tearDown()

    def test_panel_injected(self):

        # make the app
        app = self.config.make_wsgi_app()
        # make a request
        req1 = Request.blank("/")
        req1.remote_addr = "127.0.0.1"
        resp1 = req1.get_response(app)
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("http://localhost/_debug_toolbar/", resp1.text)

        # check the toolbar
        links = re_toolbar_link.findall(resp1.text)
        self.assertIsNotNone(links)
        self.assertIsInstance(links, list)
        self.assertEqual(len(links), 1)
        toolbar_link = links[0]

        req2 = Request.blank(toolbar_link)
        req2.remote_addr = "127.0.0.1"
        resp2 = req2.get_response(app)
        self.assertEqual(resp2.status_code, 200)

        self.assertIn('<li class="" id="pDebugPanel-performance-csv">', resp2.text)
        self.assertIn(
            '<div id="pDebugPanel-performance-csv-content" class="panelContent" style="display: none;">',
            resp2.text,
        )
        self.assertIn(
            """<div class="pDebugPanelTitle">
              <h3>Performance CSV</h3>
            </div>""",
            resp2.text,
        )
        self.assertIn(
            "The profiler was not activated for this request. Activate the checkbox in the toolbar to use it.",
            resp2.text,
        )

    def test_panel_works(self):
        # make the app
        app = self.config.make_wsgi_app()
        # make a request
        req1 = Request.blank("/")
        req1.remote_addr = "127.0.0.1"
        # ENABLE THE PERfORMANCE CONTROL PANEL
        req1.cookies = {"pdtb_active": "performance"}
        resp1 = req1.get_response(app)
        self.assertEqual(resp1.status_code, 200)
        self.assertIn("http://localhost/_debug_toolbar/", resp1.text)

        # check the toolbar
        links = re_toolbar_link.findall(resp1.text)
        self.assertIsNotNone(links)
        self.assertIsInstance(links, list)
        self.assertEqual(len(links), 1)
        toolbar_link = links[0]

        req2 = Request.blank(toolbar_link)
        req2.remote_addr = "127.0.0.1"
        resp2 = req2.get_response(app)
        self.assertEqual(resp2.status_code, 200)

        self.assertIn('<li class="" id="pDebugPanel-performance-csv">', resp2.text)
        self.assertIn(
            '<div id="pDebugPanel-performance-csv-content" class="panelContent" style="display: none;">',
            resp2.text,
        )
        self.assertIn(
            """<div class="pDebugPanelTitle">
              <h3>Performance CSV</h3>
            </div>""",
            resp2.text,
        )
        self.assertIn(
            "performance logging is available for this request as a CSV via the link below:",
            resp2.text,
        )

        # timing csv
        match = re_csv_timing_link.search(resp2.text)
        self.assertTrue(match)
        (_timing_link, _id) = match.groups()
        req3 = Request.blank(_timing_link)
        req3.remote_addr = "127.0.0.1"
        resp3 = req3.get_response(app)
        self.assertEqual(resp3.status_code, 200)
        self.assertEqual(
            resp3.headers["Content-Disposition"],
            'attachment; filename="performance-timing-%s.csv"' % _id,
        )
        self.assertTrue(resp3.cache_control.no_store)
        denied = Request.blank(_timing_link)
        denied.remote_addr = "192.0.2.1"
        self.assertEqual(denied.get_response(app).status_code, 404)
        self.assertTrue(resp3.text.startswith("User CPU time,"))

        # function csv
        match = re_csv_function_link.search(resp2.text)
        self.assertTrue(match)
        (_function_link, _id) = match.groups()
        req4 = Request.blank(_function_link)
        req4.remote_addr = "127.0.0.1"
        resp4 = req4.get_response(app)
        self.assertEqual(resp4.status_code, 200)
        self.assertEqual(
            resp4.headers["Content-Disposition"],
            'attachment; filename="performance-function_calls-%s.csv"' % _id,
        )
        self.assertTrue(resp4.cache_control.no_store)
        denied = Request.blank(_function_link)
        denied.remote_addr = "192.0.2.1"
        self.assertEqual(denied.get_response(app).status_code, 404)
        self.assertTrue(
            resp4.text.startswith("Calls,Total,Percall,Cumu,CumuPer,Func\r\n")
        )

    def test_csv_missing_history(self):
        # type: () -> None
        """Both CSV routes return 404 when the request is absent from history."""
        app = self.config.make_wsgi_app()
        for report in ("timing", "function_calls"):
            request = Request.blank(
                "/_debug_toolbar/api-performance/%s-missing.csv" % report
            )
            request.remote_addr = "127.0.0.1"
            self.assertEqual(request.get_response(app).status_code, 404)


    def test_spreadsheet_exports(self):
        # type: () -> None
        """Protect both CSV text fields while preserving default output."""
        from pyramid_debugtoolbar.panels.performance import PerformanceDebugPanel

        app = self.config.make_wsgi_app()
        initial = Request.blank("/")
        initial.remote_addr = "127.0.0.1"
        initial.get_response(app)
        request_id, toolbar = self.config.registry.pdtb_history.last(1)[0]
        panel = next(p for p in toolbar.panels if isinstance(p, PerformanceDebugPanel))
        panel.data.update(
            timing_rows=[(str("=label"), str("-2 msec"))],
            stats=True,
            function_calls=[
                dict(
                    ncalls="1",
                    tottime="-2",
                    percall="3",
                    cumtime="4",
                    percall_cum="5",
                    filename_long=" @module",
                )
            ],
        )

        for report, raw, safe in (
            ("timing", "=label,-2 msec", "'=label,-2 msec"),
            ("function_calls", "1,-2,3,4,5, @module", "1,-2,3,4,5,' @module"),
        ):
            path = "/_debug_toolbar/api-performance/%s-%s.csv" % (report, request_id)
            for query, row in (("", raw), ("?spreadsheet=1", safe)):
                request = Request.blank(path + query)
                request.remote_addr = "127.0.0.1"
                response = request.get_response(app)
                self.assertEqual(response.status_code, 200)
                self.assertIn(row + "\r\n", response.text)
                self.assertTrue(response.cache_control.no_store)
                if query:
                    self.assertTrue(
                        response.headers["Content-Disposition"].endswith(
                            '-spreadsheet.csv"'
                        )
                    )
