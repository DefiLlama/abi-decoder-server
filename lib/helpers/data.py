#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv(".env.sample"))
# If `.env` exists, let it override the sample env file.
load_dotenv(override=True)

ETHERSCAN_APIKEY = os.environ["ETHERSCAN_APIKEY"]

AWS_KEY_ID = os.environ["AWS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_TXDATA_BUCKET = os.environ["AWS_TXDATA_BUCKET"]
AWS_DDB_ABI_DECODER = os.environ["AWS_DDB_ABI_DECODER"]
AWS_DDB_ABI_DECODER_REGION = os.environ["AWS_DDB_ABI_DECODER_REGION"]

RPC_START_BLOCKS = {
    # 'ethereum': 13136427,  # 2021-09-01
    "ethereum": 13033669,
    "arbitrum": 657404,
    "avalanche": 3376709,
    "bsc": 10065475,
    "fantom": 18503502,
    "polygon": 18026806,
    "harmony": 18646320,
    "boba": 16188,
    "moonriver": 890949,
    "optimism": 30718,
    "aurora": 56092179,
    "moonbeam": 173355,
    "cronos": 1578335,
    "metis": 957508,
    "dfk": 0,  # Doesn't it feel great to be the first?
    "klaytn": 93622381,
}
