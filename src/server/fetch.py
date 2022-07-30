#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hexbytes import HexBytes

from src.lib.helpers.types import APIGatewayEvent, Context
from src.lib.helpers.serializer import Response
from src.lib.helpers.aws import (
    get_abi_data_contract_pseudo_batch,
    get_abi_data_pseudo_batch,
)


def fetch_signature(event: APIGatewayEvent, context: Context):
    if (ev := event.get("queryStringParameters")) is not None:
        function_sigs = ev.get("functions", "").split(",")
        event_sigs = ev.get("events", "").split(",")
        res = {}

        if function_sigs != [""]:
            function_sigs = [HexBytes(x) for x in function_sigs if len(x) == 10]
            res["functions"] = get_abi_data_pseudo_batch(
                "function",
                function_sigs,
            )

        if event_sigs != [""]:
            event_sigs = [HexBytes(x) for x in event_sigs if len(x) == 66]
            res["events"] = get_abi_data_pseudo_batch(
                "event",
                event_sigs,
            )

        # TODO: Attempt to resolve missing signatures.

        return Response.make_response(res)

    return Response.make_bad_request("no data provided")


def fetch_contract(event: APIGatewayEvent, context: Context):
    address = None
    chain = None

    if (ev := event.get("pathParameters")) is not None:
        address = ev.get("address")
        chain = ev.get("chain")

    if address is None or chain is None:
        return Response.make_bad_request("chain or address in null")

    if (ev := event.get("queryStringParameters")) is not None:
        function_sigs = ev.get("functions", "").split(",")
        event_sigs = ev.get("events", "").split(",")

        # Okay, I may be a *bit* stupid and forgot to include the `0x` prefix
        # in the database keys...
        address = HexBytes(address).hex()[2:]

        res = {}

        if function_sigs != [""]:
            function_sigs = [HexBytes(x) for x in function_sigs if len(x) == 10]
            res["functions"] = get_abi_data_contract_pseudo_batch(
                "function",
                function_sigs,
                chain,
                address,
            )

        if event_sigs != [""]:
            event_sigs = [HexBytes(x) for x in event_sigs if len(x) == 66]
            res["events"] = get_abi_data_contract_pseudo_batch(
                "event",
                event_sigs,
                chain,
                address,
            )

        # TODO: Attempt to resolve missing signatures.

        return Response.make_response(res)

    return Response.make_bad_request("no data provided")
