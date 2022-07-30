#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, Set, Tuple
import re

from eth_abi.grammar import normalize
from web3 import Web3

from .aws import (
    get_abi_data,
    get_abi_data_contract,
    upload_abi_data,
    upload_abi_data_contract,
)


FUNCTION_RE = re.compile(r"function (\w*)\(([^)]*)\)")
EVENTS_RE = re.compile(r"event (\w*)\(([^)]*)\)")

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


def handle_source_code(
    chain: str, address: str, source: str
) -> Dict[str, Set[Tuple[str, str]]]:
    res = {}

    for regex, _type in zip([FUNCTION_RE, EVENTS_RE], ["function", "event"]):
        ret = _handle_source_code(chain, address, source, regex, _type)
        res[_type] = ret

    return res


def _handle_source_code(
    chain: str, address: str, source: str, regex: re.Pattern, __type: str
) -> Set[Tuple[str, str]]:
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
        sig = Web3.keccak(text=abi)

        if __type == "function":
            # Only store the function selector (first 4).
            sig = sig[:4]

        # Read then write rather than write only to save useless writes.
        if not get_abi_data(__type, sig):
            upload_abi_data(__type, sig, abi)

        if not get_abi_data_contract(__type, sig, chain, address):
            upload_abi_data_contract(__type, sig, verbose_abi, chain, address)

    return abi_methods
