#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from eth_typing.evm import ChecksumAddress
from web3.contract import Contract
from etherscan import Etherscan
from web3 import Web3

from lib.helpers.data import ETHERSCAN_APIKEY

eth = Etherscan(ETHERSCAN_APIKEY)

# TODO: make a cache.
def create_contract(w3: Web3, addr: ChecksumAddress) -> Contract:
    # First check if address is a proxy.
    code = eth.get_contract_source_code(addr)[0]  # type: ignore
    if code["Proxy"] == "1":
        addr = code["Implementation"]

    abi = eth.get_contract_abi(addr)  # type: ignore

    return w3.eth.contract(addr, abi=abi)  # type: ignore
