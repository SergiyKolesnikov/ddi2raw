#!/usr/bin/python3

# ddi2raw.py
#
# Copyright 2017 Sergiy Kolesnikov
# https://github.com/SergiyKolesnikov/ddi2raw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import collections

HeaderInfo = collections.namedtuple('HeaderInfo', 'version payload_offset')
KNOWN_HEADERS = {
    b'IM\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00':HeaderInfo(version='7', payload_offset=0x2400),
    b'MSD Image Version 1 ':HeaderInfo(version='5', payload_offset=0x500)
    }
MAGIC_LENGTH = 20

# https://en.wikipedia.org/wiki/Design_of_the_FAT_file_system#Bootsector
# Possible first bytes at 0x000 (not present on DOS 1.x and Atari ST before TOS 1.4):
#   - DOS (since 2.0), MSX-DOS: 0xEB 0x?? 0x90
#   - Also accepted by MS-DOS, PC DOS and DR-DOS for backward compatability: 0x69
#   - Atari TOS (since 1.4): 0xE9
JUMP_INSTRUCTIONS = [b'\xEB', b'\x69', b'\xE9']

# Boot sector signature at 0x1FE (not present on DOS 1.x and non-x86-bootable FAT volumes): 0x55 0xAA
BootSectorSign = collections.namedtuple('BootSectorSign', 'offset value')
BOOT_SECTOR_SIGN = BootSectorSign(offset=0x1FE, value=b'\x55\xAA')

def guess_payload_offset(ddi_file):
    byte = ddi_file.read(1)
    while byte:
        if byte in JUMP_INSTRUCTIONS:
            jump_position = ddi_file.tell()
            ddi_file.seek(BOOT_SECTOR_SIGN.offset - 1, 1)
            byte = ddi_file.read(len(BOOT_SECTOR_SIGN.value))
            if byte == BOOT_SECTOR_SIGN.value:
                return jump_position - 1
            else:
                ddi_file.seek(jump_position + 1)
        byte = ddi_file.read(1)
    raise EOFError('No data found!')

def get_header_info(ddi_file):
    magic = ddi_file.read(MAGIC_LENGTH)
    header_info = KNOWN_HEADERS[magic]
    ddi_file.seek(header_info.payload_offset)
    if ddi_file.read(1) not in JUMP_INSTRUCTIONS:
        raise ValueError('The data after the header is in a wrong format!')
    return header_info

def copy_data(ddi_file, dsk_file, payload_offset):
    ddi_file.seek(payload_offset)
    data = ddi_file.read()
    dsk_file.write(data)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Error: Wrong number of arguments!', file=sys.stderr)
        print('Usage: ddi2raw.py <input.ddi> <output.dsk>')
    else:
        ddi_pathname = sys.argv[1]
        dsk_pathname = sys.argv[2]
        with open(ddi_pathname, 'rb') as ddi_file:
            payload_offset = 0
            try:
                header_info = get_header_info(ddi_file)
                payload_offset = header_info.payload_offset
                print('DiskDupe v' + header_info.version + ' image format detected.')
            except KeyError as err:
                print('Error: Unknown disk image header: ' + str(err), file=sys.stderr)
                print('Trying to guess where the data is...')
                try:
                    payload_offset = guess_payload_offset(ddi_file)
                except EOFError as err:
                    print('Error: ' + str(err), file=sys.stderr)
                    sys.exit(1)
            except ValueError as err:
                print('Error: ' + str(err), file=sys.stderr)
            with open(dsk_pathname, 'wb') as dsk_file:
                copy_data(ddi_file, dsk_file, payload_offset)
                print("Disk image converted successfully.")
                print("On GNU/Linux, use '/sbin/fsck.fat -v " + dsk_pathname + "' to check the image.")
