# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import binascii
import codecs
import struct
import sys
import Common


def syntax():
    print("Syntax: ExtractPowersave.py input.bin [-r rawdata.raw] [-n]")
    print("           input.bin : File from which to extract raw data")
    print("           -r rowdata.raw : File to write the raw data")
    print("           -n : Display the display name of the powersave")
    print("        At least one of the two options is required.")
    return 1


class ExtractPowersave:
    """
    This class permit the extraction of the row data from a Powersave
    file to a rowdata file.
    """

    def __init__(self, powersave_file, row_file=None):
        """
        Create a new Extract Powersave file utility instance.

        :param powersave_file:
            File from which to extract raw data.
        :type powersave_file: str
        :param row_file:
            File to write the raw data (Optionnal).
            If it's not defined, only the display name of the
            file are extract and return.
        :type row_file: str
        """
        self.powersave_file = powersave_file
        self.row_file = row_file

    def extract(self):
        """
        Extract the row data from powersave_file and return the display name
        of the powersave file.

        :return: The dysplay name of the powersave file.
        :rtype str

        :raises IOError:
        """

        with open(self.powersave_file, "rb") as infile:
            header = b""

            header += infile.read(0x14 - len(header))
            if len(header) != 0x14:
                raise IOError("Powersave format error : header size")

            computedHeaderCRC32 = Common.datel_crc32(header + Common.encode_dword(0))

            readHeaderCRC32 = infile.read(4)
            if len(readHeaderCRC32) != 4:
                raise IOError("Powersave format error : CRC32 size")

            readHeaderCRC32 =  Common.decode_dword(readHeaderCRC32)[0]

            if computedHeaderCRC32 != readHeaderCRC32:
                raise IOError('Unverified Header CRC32')

            readPayloadCRC32 = infile.read(4)
            if len(readPayloadCRC32) != 4:
                raise IOError("Powersave format error : Payload CRC32")
            readPayloadCRC32 = Common.decode_dword(readPayloadCRC32)[0]

            description = b""
            while len(description) != 0x40 * 2:
                readData = infile.read(0x40 * 2 - len(description))
                if readData == "":
                    break
                description += readData

            if len(description) != 0x40 * 2:
                raise IOError("Power save format error : display name invalid")

            # The description is little-endian UTF-16.
            description = codecs.decode(description, "utf-16le")

            try:
                index = description.index("\0")
                description = description[:index]
            except ValueError:
                pass

            if self.row_file is not None:
                computedPayloadCRC32 = b''
                with open(self.row_file, "wb") as outfile:
                    # Calculate Datel-CRC32 of payload.
                    computedPayloadCRC32 = Common.datel_crc32(b'')
                    while True:
                        data = infile.read(16384)
                        if len(data) == 0:
                            break
                        computedPayloadCRC32 = Common.datel_crc32(data, computedPayloadCRC32)
                        outfile.write(data)

                if computedPayloadCRC32 != readPayloadCRC32:
                    raise IOError('Power save format error : Unverified Payload CRC32')

            return description

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        syntax()
        sys.exit(1)

    powerSaveFile = sys.argv[1]
    index_option = 2
    powerSavename = False
    rawFile = None
    while index_option < len(sys.argv):
        option = sys.argv[index_option]
        if option == '-d':
            powerSavename = True
            index_option+=1
        elif option == '-r':
            if index_option + 1 < len(sys.argv):
                rawFile = sys.argv[index_option + 1]
                index_option += 2
            else:
                syntax()
                sys.exit(1)
        else:
            syntax()
            sys.exit(1)

    if not powerSavename and rawFile is None:
        syntax()
        sys.exit(1)

    extractor = ExtractPowersave(powerSaveFile, rawFile)
    description = extractor.extract()
    if powerSavename:
        print(description)
