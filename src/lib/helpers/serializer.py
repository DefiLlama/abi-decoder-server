#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any

import simplejson


class Request:
    @staticmethod
    def parse(data: str):
        return simplejson.loads(data)


class Response:
    @staticmethod
    def make_response(data: Any, status: int = 200):
        return {
            "statusCode": status,
            "body": simplejson.dumps(data),
            "headers": {
                "content-type": "application/json",
                "access-control-allow-origin": "*",
                "access-control-allow-headers": "*",
            },
        }

    @staticmethod
    def make_bad_request(data: str):
        return Response.make_response({"error": data}, status=400)
