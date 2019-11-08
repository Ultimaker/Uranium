#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Optional

from UM.Logger import Logger
from UM.Trust import TrustBasics

DEFAULT_PRIVATE_KEY_PATH = "private_key.pem"
DEFAULT_TO_SIGN_FILE = "material.fdm_material.json"
DEFAULT_PASSWORD = ""


def signFile(private_key_path: str, filename: str, optional_password: Optional[str]) -> bool:
    password = None if optional_password == "" else optional_password
    private_key = TrustBasics.loadPrivateKey(private_key_path, password)
    if private_key is None:
        return False

    try:
        signature = TrustBasics.getFileSignature(filename, private_key)
        if signature is None:
            Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
            return False

        wrapped_signature = {TrustBasics.__root_signature_entry, signature}

        signature_filename = TrustBasics.getSignaturePathForFile(filename)
        with open(signature_filename, "w", encoding = "utf-8") as data_file:
            json.dump(wrapped_signature, data_file, indent = 2)

        Logger.log("i", "Signed file '{0}'.".format(filename))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
    return False


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-f", "--file", type = str, default = DEFAULT_TO_SIGN_FILE)
    parser.add_argument("-w", "--password", type = str, default = DEFAULT_PASSWORD)
    args = parser.parse_args()
    signFile(args.private, args.file, args.password)


if __name__ == "__main__":
    sys.exit(mainfunc())
