#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from src.lib.helpers.types import APIGatewayEvent, Context
from src.lib.helpers.serializer import Response, Request
from src.lib.helpers import parser


def upload_source_code(event: APIGatewayEvent, context: Context):
    if (ev := event.get("body")) is not None:
        ret = Request.parse(ev)

        # TODO: remove this in when making public.
        address = ret["address"]
        chain = ret["chain"]
        # end
        source = ret["source"]

        ret = parser.handle_source_code(chain, address, source)

        return Response.make_response(
            {
                "uploaded": {
                    "functions": len(ret["functions"]),
                    "events": len(ret["events"]),
                }
            }
        )

    return Response.make_bad_request("no data provided")
