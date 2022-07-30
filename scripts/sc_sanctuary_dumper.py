#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gevent.monkey import patch_all

patch_all()

import sys
import os
import re

from gevent.pool import Pool

# Assume user is invoking this script at root folder.
# `$ python3 scripts/sc_sanctuary_dumper.py <chain>`
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from src.lib.helpers import parser

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


def handle_source_code(chain: str, address: str, path: str) -> None:
    print(path)

    with open(path) as f:
        source = f.read()

    parser.handle_source_code(chain, address, source)


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
