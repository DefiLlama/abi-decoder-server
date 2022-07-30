#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env.sample"))
# If `.env` exists, let it override the sample env file.
load_dotenv(override=True)

AWS_DDB_ABI_DECODER = os.environ["AWS_DDB_ABI_DECODER"]
