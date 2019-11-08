#!/usr/bin/env python3

import argparse
import sys

from UM.Logger import Logger
from UM.Trust import TrustBasics

DEFAULT_PRIVATE_KEY_PATH = "private_key.pem"
DEFAULT_TO_SIGN_FILE = "material.fdm_material.json"


def signFile(private_key_filename: str, filename: str) -> bool:
    private_key = TrustBasics.loadPrivateKey(private_key_filename)
    if private_key is None:
        return False

    try:
        signature = TrustBasics.getFileSignature(filename, private_key)
        if signature is None:
            Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
            return False

        signature_filename = TrustBasics.getSignaturePathForFile(filename)
        with open(signature_filename, "w", encoding = "utf-8") as data_file:
            data_file.write(signature)

        Logger.log("i", "Signed file '{0}'.".format(filename))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
    return False


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-f", "--file", type = str, default = DEFAULT_TO_SIGN_FILE)
    args = parser.parse_args()
    signFile(args.private, args.file)


if __name__ == "__main__":
    sys.exit(mainfunc())
