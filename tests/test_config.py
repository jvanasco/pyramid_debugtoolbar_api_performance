from __future__ import print_function
from __future__ import unicode_literals

# stdlib
import re
import unittest

# pyramid testing requirements
from pyramid import testing
from pyramid.exceptions import ConfigurationError
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
        self.assertTrue(resp3.text.startswith("User CPU time,"))

        # function csv
        match = re_csv_function_link.search(resp2.text)
        self.assertTrue(match)
        (_function_link, _id) = match.groups()
        req4 = Request.blank(_function_link)
        req4.remote_addr = "127.0.0.1"
        resp4 = req4.get_response(app)
        self.assertEqual(resp4.status_code, 200)
        self.assertTrue(
            resp4.text.startswith("Calls,Total,Percall,Cumu,CumuPer,Func\r\n")
        )
