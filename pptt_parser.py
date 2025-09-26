# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025 Weizhao Ouyang

import argparse
import struct
from graphviz import Digraph

# https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#processor-properties-topology-table-pptt
PPTT_HEADER_FORMAT = "<4sIBB6s8sI4sI"
PPTT_HEADER_SIZE = 36

# https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#processor-hierarchy-node-structure-type-0
PPTT_STRUCTURE_PROCESSOR_FORMAT = "<BBHIIII"
PPTT_STRUCTURE_PROCESSOR_SIZE = 20

# https://uefi.org/specs/ACPI/6.6/05_ACPI_Software_Programming_Model.html#cache-type-structure-type-1
PPTT_STRUCTURE_CACHE_FORMAT = "<BBHIIIIBBHI"
PPTT_STRUCTURE_CACHE_SIZE = 28


def parse_pptt(data):
    dot = Digraph(comment='PPTT Topology')

    if len(data) < PPTT_HEADER_SIZE:
        raise Exception("PPTT data too short")

    header_unpacked = struct.unpack(PPTT_HEADER_FORMAT, data[:PPTT_HEADER_SIZE])
    if header_unpacked[0] != b'PPTT':
        raise Exception("PPTT data invalid")

    offset = PPTT_HEADER_SIZE
    length = 0
    while offset < len(data):
        node_type = struct.unpack_from("<B", data, offset)[0]

        if node_type == 0:
            if offset + PPTT_STRUCTURE_PROCESSOR_SIZE > len(data):
                break

            processor_unpacked = struct.unpack_from(PPTT_STRUCTURE_PROCESSOR_FORMAT, data, offset)
            length = processor_unpacked[1]

            if length == 0 or offset + length > len(data):
                break

            # The boundary of a physical package
            if (processor_unpacked[3] >> 0) & 1 == 1:
                dot.node(str(offset), 'Package')
            # ACPI Processor ID valid and Node is a Leaf
            elif (processor_unpacked[3] >> 1) & 1 == 1:
                if (processor_unpacked[3] >> 3) & 1 == 1:
                    dot.node(str(offset), 'cpu'+str(processor_unpacked[5]), style='filled')
                else:
                    dot.node(str(offset), 'cpu'+str(processor_unpacked[5]))
            else:
                dot.node(str(offset), 'Fake Cluster')

            if processor_unpacked[4] != 0:
                dot.edge(str(processor_unpacked[4]), str(offset))

            if processor_unpacked[6] != 0:
                fmt = "<" + "I" * processor_unpacked[6]
                private_unpacked = struct.unpack_from(fmt, data, offset + PPTT_STRUCTURE_PROCESSOR_SIZE)
                for index in range(processor_unpacked[6]):
                    dot.edge(str(offset), str(private_unpacked[index]))

        elif node_type == 1:
            if offset + PPTT_STRUCTURE_CACHE_SIZE > len(data):
                break

            cache_unpacked = struct.unpack_from(PPTT_STRUCTURE_CACHE_FORMAT, data, offset)
            length = cache_unpacked[1]

            if length == 0 or offset + length > len(data):
                break

            info_mask = 0b111001
            if cache_unpacked[3] & info_mask == info_mask:
                if (cache_unpacked[8] >> 2) & 3 == 0:
                    node_name = "DCache"
                elif (cache_unpacked[8] >> 2) & 3 == 1:
                    node_name = "ICache"
                else:
                    node_name = "Cache"

                if cache_unpacked[5] < 1024:
                    node_name += f"\n{cache_unpacked[5]} B"
                elif cache_unpacked[5] < 1024**2:
                    node_name += f"\n{cache_unpacked[5] // 1024} KB"
                else:
                    node_name += f"\n{cache_unpacked[5] // 1024**2} MB"

                if (cache_unpacked[8] >> 0) & 3 == 0:
                    node_name += "\nRA"
                elif (cache_unpacked[8] >> 0) & 3 == 1:
                    node_name += "\nWA"
                else:
                    node_name += "\nRWA"

                if (cache_unpacked[8] >> 4) & 1 == 0:
                    node_name += "-WB"
                elif (cache_unpacked[8] >> 4) & 1 == 1:
                    node_name += "-WT"

                if (cache_unpacked[3] >> 4) & 1 == 1:
                    dot.node(str(offset), node_name)
                if cache_unpacked[4] != 0:
                    dot.edge(str(offset), str(cache_unpacked[4]))
        else:
            raise Exception("PPTT invalid node type")
        offset += length

    dot.render("pptt_topology", format='svg', cleanup=True)
    print("PPTT topology is saved as 'pptt_topology.svg'")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="PPTT.aml", help="PPTT file")

    pptt_file = parser.parse_args().file
    with open(pptt_file, "rb") as f:
        data = f.read()

    parse_pptt(data)

if __name__ == "__main__":
    main()

