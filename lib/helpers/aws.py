#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from boto3.dynamodb.conditions import Key
from hexbytes import HexBytes
import boto3

from lib.helpers.data import (
    AWS_DDB_ABI_DECODER_REGION,
    AWS_SECRET_ACCESS_KEY,
    AWS_DDB_ABI_DECODER,
    AWS_TXDATA_BUCKET,
    AWS_KEY_ID,
)


tx_bucket = boto3.resource(
    "s3", aws_secret_access_key=AWS_SECRET_ACCESS_KEY, aws_access_key_id=AWS_KEY_ID
).Bucket(AWS_TXDATA_BUCKET)


abi_table = boto3.resource(
    "dynamodb",
    region_name=AWS_DDB_ABI_DECODER_REGION,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    aws_access_key_id=AWS_KEY_ID,
).Table(AWS_DDB_ABI_DECODER)


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


def get_abi_data(_type: str, signature: HexBytes) -> Optional[List[Dict[str, str]]]:
    assert _type in ["function", "event"]

    ret = abi_table.query(
        KeyConditionExpression=Key("type").eq(_type)
        & Key("signature").begins_with(signature.hex())
    )

    if ret["Count"] != 0:
        return [{x["signature"]: x["abi"]} for x in ret["Items"]]  # type: ignore
