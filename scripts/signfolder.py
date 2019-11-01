#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import List

from UM.Logger import Logger
from UM.Trust import TrustBasics

default_private_key_path = "../private_key.pem"
default_to_sign_folder = "."
default_ignore_subfolders = ["__pycache__"]


def signFolder(private_key_filename: str, path: str, ignore_folders: List[str]) -> bool:
    private_key = TrustBasics.loadPrivateKey(private_key_filename)

    try:
        signatures = {}  # Dict[str, str]

        for root, dirnames, filenames in os.walk(path):
            if os.path.basename(root) in ignore_folders:
                continue
            for filename in filenames:
                if filename == TrustBasics.getSignaturesLocalFilename() and root == path:
                    continue

                name_on_disk = os.path.join(root, filename)
                name_in_data = name_on_disk.replace(path, "").replace("\\", "/")
                signature = TrustBasics.getFileSignature(name_on_disk, private_key)
                if signature == "":
                    Logger.logException("e", "Couldn't sign file '{0}'.".format(name_on_disk))
                    return False
                signatures[name_in_data] = signature

        json_filename = os.path.join(path, TrustBasics.getSignaturesLocalFilename())
        with open(json_filename, "w", encoding="utf-8") as data_file:
            json.dump(signatures, data_file, indent=2)

        Logger.log("i", "Signed folder '{0}'.".format(path))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign folder '{0}'.".format(path))
    return False


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type=str, default=default_private_key_path)
    parser.add_argument("-f", "--folder", type=str, default=default_to_sign_folder)
    parser.add_argument("-i", "--ignore", type=str, nargs='+', default=default_ignore_subfolders)
    args = parser.parse_args()
    signFolder(args.private, args.folder, args.ignore)


if __name__ == "__main__":
    sys.exit(mainfunc())
