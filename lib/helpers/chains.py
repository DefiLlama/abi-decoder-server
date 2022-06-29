#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import cast, List
from enum import Enum


class Chains(Enum):
    ETHEREUM = "ethereum"
    AVAX = "avax"
    BSC = "bsc"
    POLYGON = "polygon"
    ARBITRUM = "arbitrum"
    FANTOM = "fantom"
    HARMONY = "harmony"
    BOBA = "boba"
    OPTIMISM = "optimism"
    MOONRIVER = "moonriver"
    AURORA = "aurora"
    MOONBEAM = "moonbeam"
    CRONOS = "cronos"
    METIS = "metis"
    DFK = "dfk"
    XDAI = "xdai"

    @classmethod
    def values(cls) -> List[str]:
        return list(cls._value2member_map_.keys())

    @staticmethod
    def from_value(val: str) -> "Chains":
        return cast(Chains, Chains._value2member_map_[val])
