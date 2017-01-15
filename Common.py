# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals

import binascii
import codecs
import struct
import sys

if sys.version_info[0] >= 3:
    xrange = range


# Build CRC32 table.
DATEL_CRC32_TABLE = [0] * 256
for x in xrange(256):
    value = x
    for y in xrange(8):
        value = (value >> 1) ^ (0xEDB88320 if value & 1 else 0x00000000)
    DATEL_CRC32_TABLE[x] = value


# Slightly strange Datel CRC32 means we can't use binascii.crc32.
def datel_crc32(data, crc = 0):
    for x in xrange(len(data)):
        crc = DATEL_CRC32_TABLE[(crc & 0xFF) ^ ord(data[x:x + 1])] ^ (crc >> 8)
    return crc


def encode_dword(x):
    return struct.pack(b"<I", x)

def decode_dword(x):
    return struct.unpack(b"<I", x)