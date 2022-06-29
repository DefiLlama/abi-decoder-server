#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional

from hexbytes import HexBytes
import requests

from lib.helpers.retry import retry


BASE_URL = "https://www.4byte.directory/api/v1/{search}/?hex_signature={sig}"


def _fetch(signature: HexBytes, search: str) -> Optional[List[str]]:
    ret = retry(
        requests.get, BASE_URL.format(search=search, sig=signature.hex())
    ).json()

    if ret["count"] == 0:
        return None

    return [x["text_signature"] for x in ret["results"]]


def fetch_function(signature: HexBytes) -> Optional[List[str]]:
    return _fetch(signature, "signatures")


def fetch_event(signature: HexBytes) -> Optional[List[str]]:
    return _fetch(signature, "event-signatures")
