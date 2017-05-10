pyramid_debugtoolbar_api_performance
===================================

This allows for .csv output of performance logging.
This package can be useful as part of test suites, allowing developers to run a series of tests and log the performance.

It exposes two routes for csvs:

	timing
	function_calls

both correlate to the official Performance panel

NOTES:
======

This packages requires pyramid_debugtoolbar 4.0 or newer


How to use this package
=======================


Update your ENVIRONMENT.ini file

    debugtoolbar.includes = pyramid_debugtoolbar_api_performance

You MUST be using `pyramid_debugtoolbar` with the SqlAlchemy panel enabled.  This just piggybacks on the existing module's work to log queries.

You MUST use `debugtoolbar.includes`.  This will not work properly via `pyramid.includes`

You can access a csv of the SqlAlchemy report via the following url hack:

    url_html = '/_debug_toolbar/{request_id}'
    url_api =  '/_debug_toolbar/api-performance/timing-{request_id}.csv'
    url_api =  '/_debug_toolbar/api-performance/function_calls-{request_id}.csv'
    
    
    
The file will be downloaded and offer a content-disposition as:

    performance-{request_id}.csv

The CSV columns are:

* xxxx
* xxxx
* xxxx