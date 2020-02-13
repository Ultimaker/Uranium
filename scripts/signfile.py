#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Optional

from UM.Logger import Logger
from UM.Trust import TrustBasics

# Default arguments, if arguments to the script are omitted, these values are used:
DEFAULT_PRIVATE_KEY_PATH = "private_key.pem"
DEFAULT_TO_SIGN_FILE = "material.fdm_material.json"
DEFAULT_PASSWORD = ""


def signFile(private_key_path: str, filename: str, optional_password: Optional[str]) -> bool:
    """Generate a signature for a file (given a private key) and save it to a json signature file.

    A json signature file for a single file looks like this:
    {
      "root_signature": "...<key in base-64>..."
    }

    :param private_key_path: Path to the file containing the private key.
    :param filename: The file to be signed.
    :param optional_password: If the private key has a password, it should be provided here.
    :return: Whether a valid signature file has been generated and saved.
    """

    password = None if optional_password == "" else optional_password
    private_key = TrustBasics.loadPrivateKey(private_key_path, password)
    if private_key is None:
        return False

    try:
        signature = TrustBasics.getFileSignature(filename, private_key)
        if signature is None:
            Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
            return False

        wrapped_signature = {TrustBasics.getRootSignatureEntry(): signature}

        signature_filename = TrustBasics.getSignaturePathForFile(filename)
        with open(signature_filename, "w", encoding = "utf-8") as data_file:
            json.dump(wrapped_signature, data_file, indent = 2)

        Logger.log("i", "Signed file '{0}'.".format(filename))
        return True

    except:  # Yes, we  do really want this on _every_ exception that might occur.
        Logger.logException("e", "Couldn't sign file '{0}'.".format(filename))
    return False


def mainfunc():
    """Arguments:

    `-k <filename>` or `--private <filename>` path to the private key
    `-f <filename>` or `--file <filename>` path to the file to be signed
    `-w <password>` or `--password <password>` if the private key file has a password, it should be specified like this
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--private", type = str, default = DEFAULT_PRIVATE_KEY_PATH)
    parser.add_argument("-f", "--file", type = str, default = DEFAULT_TO_SIGN_FILE)
    parser.add_argument("-w", "--password", type = str, default = DEFAULT_PASSWORD)
    args = parser.parse_args()
    signFile(args.private, args.file, args.password)


if __name__ == "__main__":
    sys.exit(mainfunc())
