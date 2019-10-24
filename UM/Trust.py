# Copyright (c) 2019 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import json
import os

from UM.Logger import Logger


class Trust:

    # TODO: Load key from 'installed folder', use that to salt the checksums (this will not be a static class then...)

    @classmethod
    def SignedFolderCheck(cls, signature_filename: str, path: str) -> bool:
        try:
            json_filename = os.path.join(path, signature_filename)

            with open(json_filename, "r", encoding="utf-8") as data_file:
                signatures_json = json.load(data_file)

                file_count = 0
                for root, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        if filename == signature_filename:
                            continue
                        file_count += 1
                        name_on_disk = os.path.join(root, filename)
                        name_in_data = name_on_disk.replace(path, "").replace("\\", "/")

                        checksum_in_data = signatures_json.get(name_in_data, None)
                        if checksum_in_data is None:
                            Logger.logException("e", "File '{0}' was not signed with a checksum.".format(name_on_disk))
                            return False

                        # TODO: Actual checksum check!  ->  Just testing the structure of this method r.n. :-)
                        if checksum_in_data != "CHECKSUM":
                            Logger.logException("e", "File '{0}' didn't match with checksum.".format(name_on_disk))
                            return False

                if len(signatures_json.keys()) != file_count:
                    Logger.logException("e", "Mismatch: # entries in '{0}' vs. real files.".format(json_filename))
                    return False

        except:  # Yes, we  do really want this on _every_ exception that might occur.
            Logger.logException("e", "Can't find or parse signatures for unbundled folder '{0}'.".format(path))
            return False

        return True
