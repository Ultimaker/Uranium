#!/usr/bin/env python3

import argparse
import sys

from UM.Trust import TrustBasics

default_private_key_path = "./private_key.pem"
default_public_key_path = "./public_key.pem"


def createAndStoreNewKeyPair(private_filename: str, public_filename: str) -> None:
    private_key, public_key = TrustBasics.generateNewKeyPair()
    TrustBasics.saveKeyPair(private_key, private_filename, public_filename)


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type=str, default=default_private_key_path)
    parser.add_argument("-p", "--public", type=str, default=default_public_key_path)
    args = parser.parse_args()
    createAndStoreNewKeyPair(args.private, args.public)


if __name__ == "__main__":
    sys.exit(mainfunc())
