#!/usr/bin/env python3

import argparse
import sys

from UM.Trust import TrustBasics

DEFAULT_PRIVATE_KEY_PATH = "./private_key.pem"
DEFAULT_PUBLIC_KEY_PATH = "./public_key.pem"


def createAndStoreNewKeyPair(private_filename: str, public_filename: str) -> None:
    private_key, public_key = TrustBasics.generateNewKeyPair()
    TrustBasics.saveKeyPair(private_key, private_filename, public_filename)


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-p", "--public", type = str, default = DEFAULT_PUBLIC_KEY_PATH)
    args = parser.parse_args()
    createAndStoreNewKeyPair(args.private, args.public)


if __name__ == "__main__":
    sys.exit(mainfunc())
