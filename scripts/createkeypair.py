#!/usr/bin/env python3

import argparse
from typing import Optional
import sys

from UM.Trust import TrustBasics

DEFAULT_PRIVATE_KEY_PATH = "./private_key.pem"
DEFAULT_PUBLIC_KEY_PATH = "./public_key.pem"
DEFAULT_PASSWORD = ""


def createAndStoreNewKeyPair(private_filename: str, public_filename: str, optional_password: Optional[str]) -> None:
    password = None if optional_password == "" else optional_password
    private_key, public_key = TrustBasics.generateNewKeyPair()
    TrustBasics.saveKeyPair(private_key, private_filename, public_filename, password)


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-p", "--public", type = str, default = DEFAULT_PUBLIC_KEY_PATH)
    parser.add_argument("-w", "--password", type = str, default = DEFAULT_PASSWORD)
    args = parser.parse_args()
    createAndStoreNewKeyPair(args.private, args.public, args.password)


if __name__ == "__main__":
    sys.exit(mainfunc())
