# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Weizhao Ouyang

import argparse
import struct

# https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#firmware-performance-data-table-fpdt
FPDT_HEADER_FORMAT = "<4sIBB6s8sI4sI"
FPDT_HEADER_SIZE = 36

# https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#performance-record-format
FPDT_PERFORMANCE_RECORD_FORMAT = "<HBB"
FPDT_PERFORMANCE_RECORD_SIZE = 4


def parse_fpdt(data):
    if len(data) < FPDT_HEADER_SIZE:
        raise Exception("FPDT data too short")

    header_unpacked = struct.unpack(FPDT_HEADER_FORMAT, data[:FPDT_HEADER_SIZE])
    if header_unpacked[0] != b'FPDT':
        raise Exception("FPDT data invalid")

    offset = FPDT_HEADER_SIZE
    length = 0
    while offset < len(data):
        record_type = struct.unpack_from(FPDT_PERFORMANCE_RECORD_FORMAT, data, offset)[0]

        # https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#fpdt-performance-record-types
        if record_type == 0:
            print("FBPT")
            pointer_unpacked = struct.unpack_from("<IQ", data, offset + FPDT_PERFORMANCE_RECORD_SIZE)[1]
            print("Pointer:", hex(pointer_unpacked))
            length = FPDT_PERFORMANCE_RECORD_SIZE + 12
        elif record_type == 1:
            print("S3PT")
            pointer_unpacked = struct.unpack_from("<IQ", data, offset + FPDT_PERFORMANCE_RECORD_SIZE)[1]
            print("Pointer:", hex(pointer_unpacked))
            length = FPDT_PERFORMANCE_RECORD_SIZE + 12
        elif record_type == 2:
            print("MBPT")
            pointer_unpacked = struct.unpack_from("<IQ", data, offset + FPDT_PERFORMANCE_RECORD_SIZE)[1]
            print("Pointer:", hex(pointer_unpacked))
            length = FPDT_PERFORMANCE_RECORD_SIZE + 12
        elif record_type == 3:
            print("Timestamp")
            length = FPDT_PERFORMANCE_RECORD_SIZE + 28
        else:
            print(record_type)

        offset += length


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="fpdt.dat", help="FPDT file")

    fpdt_file = parser.parse_args().file
    with open(fpdt_file, "rb") as f:
        data = f.read()

    parse_fpdt(data)


if __name__ == "__main__":
    main()
