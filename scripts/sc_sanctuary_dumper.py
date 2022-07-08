#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gevent.monkey import patch_all

patch_all()

from typing import List
import sys
import os
import re

from eth_abi.grammar import normalize
from gevent.greenlet import Greenlet
from gevent.pool import Pool
from web3 import Web3
import gevent

# Assume user is invoking this script at root folder.
# `$ python3 scripts/sc_sanctuary_dumper.py <chain>`
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from lib.helpers.aws import (
    get_abi_data,
    get_abi_data_contract,
    upload_abi_data,
    upload_abi_data_contract,
)


FUNCTION_RE = re.compile(r"function (\w*)\(([^)]*)\)")
EVENTS_RE = re.compile(r"event (\w*)\(([^)]*)\)")

pool = Pool(size=128)

SCS_PATH = os.path.join(_root, "smart-contract-sanctuary")
CHAINS = [
    "arbitrum",
    "avalanche",
    "bsc",
    "celo",
    "ethereum",
    "fantom",
    "optimism",
    "polygon",
    "tron",
]
TYPES = {
    "address",
    "bool",
    "function",
    "bytes",
    "string",
}


def _is_valid_type(var: str) -> bool:
    if var.endswith("[]"):
        var = var[: len(var) - 2]

    if var in TYPES:
        return True

    if var.startswith("uint"):
        return int(var[4:]) % 8 == 0
    elif var.startswith("int"):
        return int(var[3:]) % 8 == 0
    elif var.startswith("bytes"):
        return 0 < int(var[5:]) <= 32

    return False


def _get_argtypes(x):
    _s = x.split(" ")
    s = set(_s)

    assert len(s) == len(_s)
    assert "=>" not in _s

    if z := {"memory", "calldata", "storage", "payable"}.intersection(s):
        for e in z:
            s.remove(e)

    if len(s) in [2, 3]:
        assert " " not in _s[0], _s[0]

        if len(s) == 3:
            assert "indexed" == _s[1], _s

        _type = normalize(_s[0])

        if _is_valid_type(_type):
            return _type

    raise ValueError(f"failed to get type {x!r}")


def _handle_source_code(
    chain: str, address: str, path: str, regex: re.Pattern, __type: str
) -> None:
    with open(path) as f:
        source = f.read()

    threads: List[Greenlet] = []
    ret = regex.findall(source)
    abi_methods = set()

    for name, args in ret:
        args = (
            args.replace("\n", "").replace("\t", "").replace("\r", "").strip().lstrip()
        )
        _verbose_args = []
        _argtypes = []

        assert " " not in name, name

        if not args:
            abi = f"{name}()"
            abi_methods.add((abi, abi))
            continue
        elif not name:
            continue
        elif type(args) == str and args.count(" ") == 0:
            # Interface ex: withdraw(uint);
            args = [normalize(x) for x in args.split(",")]

            if len(args) == 1:
                abi = f"{name}({args[0]}"
                abi_methods.add((abi, abi))
            else:
                abi = f"{name}({','.join(args)})"
                abi_methods.add((abi, abi))

            continue

        # assert " " in args, args
        args = args.split(",")
        for x in args:
            x = x.strip().lstrip()

            try:
                _argtypes.append(_get_argtypes(x))
                _verbose_args.append(x)
            except (ValueError, AssertionError):
                continue

        abi_methods.add(
            (
                f"{name}({','.join(_verbose_args)})",
                f"{name}({','.join(_argtypes)})",
            )
        )

    for verbose_abi, abi in abi_methods:
        # print(method)
        sig = Web3.keccak(text=abi)

        if __type == "function":
            # Only store the function selector (first 4).
            sig = sig[:4]

        # Read then write rather than write only to save useless writes.
        if not get_abi_data(__type, sig):
            upload_abi_data(__type, sig, abi)
        #  t = pool.spawn(upload_abi_data, __type, sig, abi)
        # threads.append(t)

        if not get_abi_data_contract(__type, sig, chain, address):
            upload_abi_data_contract(__type, sig, verbose_abi, chain, address)
        #  t = pool.spawn(
        #      upload_abi_data_contract, __type, sig, verbose_abi, chain, address
        #  )
        #  threads.append(t)

    gevent.joinall(threads)


def handle_source_code(chain: str, address: str, path: str) -> None:
    print(path)

    for regex, _type in zip([FUNCTION_RE, EVENTS_RE], ["function", "event"]):
        _handle_source_code(chain, address, path, regex, _type)


def run_chain(chain: str) -> None:
    _path = os.path.join(SCS_PATH, chain, "contracts", "mainnet")

    for dir, _, files in os.walk(_path):
        for file in files:
            if file.endswith(".sol"):
                # <addr>_<filename>.sol
                address = file.split("_")[0]
                # handle_source_code(chain, address, os.path.join(dir, file))
                pool.spawn(
                    handle_source_code,
                    chain,
                    address,
                    os.path.join(dir, file),
                )

    pool.join()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # User provided what chain to start dumping.
        # `$ python3 scripts/sc_sanctuary_dumper.py <CHAIN>`
        _, chain = sys.argv

        assert chain in CHAINS, f"invalid chain {chain}"
    else:
        # Dump every chain.
        chain = None

    if chain is not None:
        run_chain(chain)
    else:
        for chain in CHAINS:
            run_chain(chain)
