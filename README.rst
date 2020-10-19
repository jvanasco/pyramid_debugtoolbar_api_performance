pyramid_debugtoolbar_api_performance
====================================

.. image:: https://github.com/jvanasco/pyramid_debugtoolbar_api_performance/workflows/Python%20package/badge.svg
        :alt: Build Status

`pyramid_debugtoolbar_api_performance` extends the existing `pyramid_debugtoolbar`
Performance Panel to support downloadable CSV files of profiling data.

This package does not replace the default panel, and requires it to be active.

This package is designed for application profile and to be a useful part of test
suites, allowing developers to run a series of tests and log the Performance
performance.

The package exposes two routes for CSV data:

* timing
* function_calls

Both correlate to the official Performance panel data.

The urls are generated in a machine-friendly format, so you can regex the
`request_id` off a page and pull it from the API.  This is explained below...


NOTES:
======

This packages requires pyramid_debugtoolbar 4.0 or newer


How to use this package
=======================


Update your ENVIRONMENT.ini file

.. code-block:: python

    debugtoolbar.includes = pyramid_debugtoolbar_api_performance

You MUST be using `pyramid_debugtoolbar` with the Performance panel enabled.
This package simply piggybacks on the existing module's work to log queries.

You MUST use `debugtoolbar.includes`.  This will not work properly via `pyramid.includes`

You can access a csv of the Profiling report via the following url hack:

.. code-block:: python

    url_html = '/_debug_toolbar/{request_id}'
    url_api =  '/_debug_toolbar/api-performance/timing-{request_id}.csv'
    url_api =  '/_debug_toolbar/api-performance/function_calls-{request_id}.csv'
    
    
The file will be downloaded and offer a content-disposition as:

.. code-block:: shell

    performance-{request_id}.csv

Configuration
=======================

By default, this package writes CSV files using "UTF-8" encoding.

To change this, use the environment variable `pyramid_debugtoolbar_api_performance_encoding`

.. code-block:: shell

	export pyramid_debugtoolbar_api_performance_encoding=ascii
