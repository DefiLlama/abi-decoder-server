#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Tuple, cast

from boto3.dynamodb.conditions import Key
from hexbytes import HexBytes
from gevent import Greenlet
import gevent
import boto3

from lib.helpers.data import AWS_DDB_ABI_DECODER


abi_table = boto3.resource("dynamodb").Table(AWS_DDB_ABI_DECODER)


def upload_abi_data(_type: str, signature: HexBytes, abi_method: str) -> None:
    assert _type in ["function", "event"]

    assert (
        abi_table.put_item(
            Item={
                "type": _type,
                "signature": signature.hex(),
                "abi": abi_method,
            },
        )
    )["ResponseMetadata"]["HTTPStatusCode"] == 200, "put_item failed"


def get_abi_data(_type: str, signature: HexBytes) -> Optional[Dict[str, str]]:
    assert _type in ["function", "event"]

    res: Dict[str, str] = {}

    ret = abi_table.query(
        KeyConditionExpression=Key("type").eq(_type)
        & Key("signature").begins_with(signature.hex())
    )

    if ret["Count"] != 0:
        for item in ret["Items"]:
            sig = cast(str, item["signature"])
            res[sig] = cast(str, item["abi"])

    return res


def get_abi_data_pseudo_batch(_type: str, _signatures: List[HexBytes]):
    assert _type in ["function", "event"]

    ret: Dict[str, Optional[List[Dict[str, str]]]] = {}
    threads: List[Tuple[HexBytes, Greenlet]] = []
    signatures = set(_signatures)

    for signature in signatures:
        t = gevent.spawn(get_abi_data, _type, signature)
        threads.append((signature, t))

    gevent.joinall([t[1] for t in threads])

    for sig, thread in threads:
        ret[sig.hex()] = thread.get()

    return ret
