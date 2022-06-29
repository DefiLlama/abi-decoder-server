#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Optional

from eth_typing.evm import ChecksumAddress
from hexbytes import HexBytes
from web3 import Web3

from lib.helpers.aws import get_abi_data, upload_abi_data
from lib.modules.etherscan import create_contract
from lib.modules import sigeth
from lib.modules import _4byte


def decode_function_signature(
    signature: HexBytes,
    w3: Optional[Web3] = None,
    addr: Optional[ChecksumAddress] = None,
) -> Optional[List[str]]:
    if (ret := _4byte.fetch_function(signature)) is not None:
        return ret
    elif (ret := sigeth.fetch_function(signature)) is not None:
        return ret

    if addr is not None and w3 is not None:
        try:
            c = create_contract(w3, addr)
        except AssertionError:
            return

        if len(signature) == 4:
            return [c.get_function_by_selector(signature)]
        else:
            return [c.get_function_by_signature(signature)]


def decode_function_signature_ddb(
    signature: HexBytes,
    w3: Optional[Web3] = None,
    addr: Optional[ChecksumAddress] = None,
    only_cache: bool = False,
):
    if (ret := get_abi_data("function", signature)) is not None:
        return ret

    if not only_cache:
        # Miss from DynamoDB, so let's go the naive route.
        if (ret := decode_function_signature(signature, w3, addr)) is not None:
            # upload_abi_data("function", signature, ret)
            # Since `ret` is a list of functions starting with `signature`,
            # we recompute all the abi methods to then upload into the db.
            for abi in ret:
                upload_abi_data("function", Web3.keccak(text=abi), abi)

        return ret
