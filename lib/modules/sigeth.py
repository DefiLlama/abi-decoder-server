#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, List

from hexbytes import HexBytes
import requests

from lib.helpers.retry import retry

BASE_URL = "https://sig.eth.samczsun.com/api/v1/signatures?{search}={sig}"


def _fetch(signature: HexBytes, search: str) -> Optional[List[str]]:
    key = signature.hex()

    ret = retry(requests.get, BASE_URL.format(search=search, sig=key)).json()

    f = ret["result"][search][key]

    if not f:
        return None

    return [x["name"] for x in f]


def fetch_function(signature: HexBytes) -> Optional[List[str]]:
    return _fetch(signature, "function")


def fetch_event(signature: HexBytes) -> Optional[List[str]]:
    return _fetch(signature, "event")
