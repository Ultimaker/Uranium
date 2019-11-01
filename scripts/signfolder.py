#!/usr/bin/env python3

import argparse
import sys

from UM.Trust import Trust

default_private_key_path = "../private_key.pem"
default_to_sign_folder = "."
default_ignore_subfolders = ["__pycache__"]


def signFolder(private_key_filename: str, to_sign_folder: str, ignore_subfolders: str) -> None:
    trust = Trust(None)
    private_key = trust.loadPrivateKey(private_key_filename)
    trust.signFolder(private_key, to_sign_folder, ignore_subfolders)


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type=str, default=default_private_key_path)
    parser.add_argument("-f", "--folder", type=str, default=default_to_sign_folder)
    parser.add_argument("-i", "--ignore", type=str, nargs='+', default=default_ignore_subfolders)
    args = parser.parse_args()
    signFolder(args.private, args.folder, args.ignore)


if __name__ == "__main__":
    sys.exit(mainfunc())
