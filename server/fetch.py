#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hexbytes import HexBytes

from lib.helpers.types import APIGatewayEvent, Context
from lib.helpers.aws import get_abi_data_pseudo_batch
from lib.helpers.serializer import Response


def fetch_hex(event: APIGatewayEvent, context: Context):
    if (ev := event.get("queryStringParameters")) is not None:
        function_sigs = ev.get("functions", "").split(",")
        event_sigs = ev.get("events", "").split(",")
        res = {}

        if function_sigs != [""]:
            function_sigs = [HexBytes(x) for x in function_sigs]
            res["functions"] = get_abi_data_pseudo_batch(
                "function",
                function_sigs,
            )

        if event_sigs != [""]:
            event_sigs = [HexBytes(x) for x in event_sigs]
            res["events"] = get_abi_data_pseudo_batch(
                "event",
                event_sigs,
            )

        # TODO: Attempt to resolve missing signatures.

        return Response.make_response(res)

    return Response.make_bad_request("no data provided")
