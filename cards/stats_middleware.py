# -*- coding: utf-8 -*-

import time

# From https://www.stavros.io/posts/django-page-load-time/


class StatsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        "Store the start time when the request comes in."
        request.start_time = time.time()
        resp = self.get_response(request)
        resp = self.process_response(request, resp)
        return resp

    def process_response(self, request, response):
        "Calculate and output the page generation duration"
        # Get the start time from the request and calculate how long
        # the response took.
        duration = time.time() - request.start_time

        # Add the header.
        response["X-Page-Generation-Duration-ms"] = int(duration * 1000)
        return response
