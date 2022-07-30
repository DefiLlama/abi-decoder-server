#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional, Tuple, cast
from collections import defaultdict

from boto3.dynamodb.conditions import Key
from hexbytes import HexBytes
from gevent import Greenlet
import gevent
import boto3

from .data import AWS_DDB_ABI_DECODER


abi_table = boto3.resource("dynamodb").Table(AWS_DDB_ABI_DECODER)


def upload_abi_data(_type: str, signature: HexBytes, abi_method: str) -> None:
    assert _type in ["function", "event"]

    assert (
        abi_table.put_item(
            Item={
                "PK": f"{_type}#{signature.hex()}",
                "SK": abi_method,
            }
        )["ResponseMetadata"]["HTTPStatusCode"]
        == 200
    ), "put_item failed"


def upload_abi_data_contract(
    _type: str,
    signature: HexBytes,
    verbose_abi: str,  # ABI with argument names.
    chain: str,
    address: str,
) -> None:
    assert _type in ["function", "event"]

    assert (
        abi_table.put_item(
            Item={
                "PK": f"contract#{chain.lower()}#{address.lower()}",
                "SK": f"{_type}#{signature.hex()}",
                "verbose_abi": verbose_abi,
            }
        )["ResponseMetadata"]["HTTPStatusCode"]
        == 200
    ), "put_item failed"


def get_abi_data(_type: str, signature: HexBytes):
    assert _type in ["function", "event"]

    if _type == "function":
        assert len(signature) == 4  # Function selector.
    elif _type == "event":
        assert len(signature) == 32  # Topic hash.

    res: Dict[str, List[str]] = defaultdict(list)

    ret = abi_table.query(
        KeyConditionExpression=Key("PK").eq(f"{_type}#{signature.hex()}")
    )

    if _type == "event":
        # If more than 1 then there is a colliso - uh oh.
        assert ret["Count"] <= 1

        if ret["Count"] != 0:
            item = ret["Items"][0]
            sig = cast(str, item["PK"]).split("#")[1]

            return {sig: item["SK"]}

        return {}
    elif _type == "function":
        if ret["Count"] != 0:
            for item in ret["Items"]:
                sig = cast(str, item["PK"]).split("#")[1]
                res[sig].append(cast(str, item["SK"]))

    return res


def get_abi_data_contract(
    _type: str, signature: HexBytes, chain: str, address: str
) -> Optional[Dict[str, str]]:
    assert _type in ["function", "event"]

    if _type == "function":
        assert len(signature) == 4  # Function selector.
    elif _type == "event":
        assert len(signature) == 32  # Topic hash.

    ret = abi_table.query(
        KeyConditionExpression=Key("PK").eq(
            f"contract#{chain.lower()}#{address.lower()}"
        )
        & Key("SK").eq(f"{_type}#{signature.hex()}")
    )

    # Should only be no more than 1 result for both functions and events.
    assert ret["Count"] <= 1

    if ret["Count"] != 0:
        item = ret["Items"][0]
        sig = cast(str, item["SK"]).split("#")[1]

        return {sig: cast(str, item["verbose_abi"])}


def get_abi_data_pseudo_batch(_type: str, _signatures: List[HexBytes]):
    assert _type in ["function", "event"]

    threads: List[Tuple[HexBytes, Greenlet]] = []
    signatures = set(_signatures)
    ret = defaultdict(list)

    for signature in signatures:
        t = gevent.spawn(get_abi_data, _type, signature)
        threads.append((signature, t))

    gevent.joinall([t[1] for t in threads])

    for sig, thread in threads:
        res = thread.get()

        if res:
            for _sig, _res in res.items():
                assert sig.hex() == _sig

                if _type == "function":
                    ret[_sig].extend(_res)
                elif _type == "event":
                    ret[_sig] = _res
        else:
            # `defaultdict(list)` will init an empty list.
            ret[sig.hex()]

    return ret


def get_abi_data_contract_pseudo_batch(
    _type: str, _signatures: List[HexBytes], chain: str, address: str
) -> Dict[str, Optional[str]]:
    assert _type in ["function", "event"]

    threads: List[Tuple[HexBytes, Greenlet]] = []
    signatures = set(_signatures)
    ret: Dict[str, Optional[str]] = {}

    for signature in signatures:
        t = gevent.spawn(
            get_abi_data_contract,
            _type,
            signature,
            chain,
            address,
        )
        threads.append((signature, t))

    gevent.joinall([t[1] for t in threads])

    for sig, thread in threads:
        res = thread.get()

        if res:
            for _sig, _res in res.items():
                assert sig.hex() == _sig
                ret[_sig] = _res
        else:
            ret[sig.hex()] = None

    return ret
