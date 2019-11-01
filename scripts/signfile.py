#!/usr/bin/env python3

import argparse
import sys

from UM.Logger import Logger
from UM.Trust import TrustBasics

default_private_key_path = "private_key.pem"
default_to_sign_file = "material.fdm_material.json"


def signFile(private_key_filename: str, filename: str) -> bool:
    private_key = TrustBasics.loadPrivateKey(private_key_filename)

    try:
        signature = TrustBasics.getFileSignature(filename, private_key)
        if signature == "":
            Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
            return False

        signature_filename = TrustBasics.getSignatureFilenameFor(filename)
        with open(signature_filename, "w", encoding="utf-8") as data_file:
            data_file.write(signature)

        Logger.log("i", "Signed file '{0}'.".format(filename))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
    return False


def mainfunc():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type=str, default=default_private_key_path)
    parser.add_argument("-f", "--file", type=str, default=default_to_sign_file)
    args = parser.parse_args()
    signFile(args.private, args.file)


if __name__ == "__main__":
    sys.exit(mainfunc())
