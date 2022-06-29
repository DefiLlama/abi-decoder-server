#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Callable, TypeVar
import traceback

import logging
import gevent

T = TypeVar("T")


def retry(func: Callable[..., T], *args, **kwargs) -> T:
    attempts: int = kwargs.pop("attempts", 5)

    for i in range(attempts):
        try:
            return func(*args, **kwargs)
        except Exception:
            print(f"retry attempt {i}, args: {args}")
            traceback.print_exc()
            gevent.sleep(3**i)

    logging.critical(f"maximum retries ({attempts}) reached")
    raise
