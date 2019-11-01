#!/usr/bin/env python3

import argparse
import sys

from UM.Trust import Trust

default_private_key_path = "private_key.pem"
default_to_sign_file = "material.fdm_material.json"


def signFile(private_key_filename: str, to_sign_file: str) -> None:
    trust = Trust(None)
    private_key = trust.loadPrivateKey(private_key_filename)
    trust.signFile(private_key, to_sign_file)


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type=str, default=default_private_key_path)
    parser.add_argument("-f", "--file", type=str, default=default_to_sign_file)
    args = parser.parse_args()
    signFile(args.private, args.file)


if __name__ == "__main__":
    sys.exit(mainfunc())
