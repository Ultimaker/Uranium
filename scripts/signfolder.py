#!/usr/bin/env python3

import argparse
import json
import os
import sys
from typing import Optional, List

from UM.Logger import Logger
from UM.Trust import TrustBasics

DEFAULT_PRIVATE_KEY_PATH = "../private_key.pem"
DEFAULT_TO_SIGN_FOLDER = "."
DEFAULT_IGNORE_SUBFOLDERS = ["__pycache__"]
DEFAULT_PASSWORD = ""


def signFolder(private_key_path: str, path: str, ignore_folders: List[str], optional_password: Optional[str]) -> bool:
    password = None if optional_password == "" else optional_password
    private_key = TrustBasics.loadPrivateKey(private_key_path, password)
    if private_key is None:
        return False

    try:
        signatures = {}  # Dict[str, str]

        for root, dirnames, filenames in os.walk(path, followlinks = True):
            if os.path.basename(root) in ignore_folders:
                continue
            for filename in filenames:
                if filename == TrustBasics.getSignaturesLocalFilename() and root == path:
                    continue

                name_on_disk, name_in_data = TrustBasics.getFilePathInfo(path, root, filename)
                signature = TrustBasics.getFileSignature(name_on_disk, private_key)
                if signature is None:
                    Logger.logException("e", "Couldn't sign file '{0}'.".format(name_on_disk))
                    return False
                signatures[name_in_data] = signature

        wrapped_signatures = {TrustBasics.getRootSignatureCategory(): signatures}

        json_filename = os.path.join(path, TrustBasics.getSignaturesLocalFilename())
        with open(json_filename, "w", encoding = "utf-8") as data_file:
            json.dump(wrapped_signatures, data_file, indent = 2)

        Logger.log("i", "Signed folder '{0}'.".format(path))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign folder '{0}'.".format(path))
    return False


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-f", "--folder", type = str, default = DEFAULT_TO_SIGN_FOLDER)
    parser.add_argument("-i", "--ignore", type = str, nargs = '+', default = DEFAULT_IGNORE_SUBFOLDERS)
    parser.add_argument("-w", "--password", type = str, default = DEFAULT_PASSWORD)
    args = parser.parse_args()
    signFolder(args.private, args.folder, args.ignore, args.password)


if __name__ == "__main__":
    sys.exit(mainfunc())
