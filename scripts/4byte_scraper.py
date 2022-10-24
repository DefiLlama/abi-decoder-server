#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gevent.pool import Pool
from gevent import Greenlet
import grequests
import gevent

from typing import List, Tuple, cast
from urllib3.util.retry import Retry
import sys
import os

from requests.adapters import HTTPAdapter
from requests.sessions import Session
from requests.models import Response
from hexbytes import HexBytes
from tqdm import tqdm

# Assume user is invoking this script at root folder.
# `$ python3 scripts/4byte_scraper.py`
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from src.lib.helpers.aws import upload_abi_data, upload_abi_data

URL = "https://www.4byte.directory/api/v1/signatures"
MAX_PAGE = 8142

session = Session()
session.mount("https://", HTTPAdapter(max_retries=Retry(total=5)))

reqs = [grequests.get(URL)] + [
    grequests.get(URL, params={"page": i}, session=session)
    for i in range(8000, MAX_PAGE)
]
pool = Pool(size=256)


def batch_upload(data: List[Tuple[HexBytes, str]]) -> None:
    threads: List[Tuple[HexBytes, Greenlet]] = []

    for sig, method in data:
        threads.append(pool.spawn(upload_abi_data, "function", sig, method))

    gevent.joinall(threads)


with tqdm(total=len(reqs)) as pbar:
    for res in grequests.imap(reqs, size=10):
        res = cast(Response, res)

        if res.status_code == 200:
            res = res.json()
            data = res["results"]

            abis = [(HexBytes(x["hex_signature"]), x["text_signature"]) for x in data]
            pool.spawn(batch_upload, abis)
        else:
            print(res.url, res, res.text)

        pbar.update(1)

print("waiting for threads to join...")
pool.join()
