# ddi2raw

## Description

***ddi2raw*** converts a floppy disk image in a DDI (DiskDupe) format to a raw floppy disk image.

The program can convert images created with DiskDupe version 5 and 7 and probably with other versions too. It was tested on images of 1.44MB 3.5" floppies.

***ddi2raw*** requires Python 3.

## Usage

```
python3 ddi2raw.py <input.ddi> <output.img>
```

## Image Formats

### DDI Disk Image

DiskDupe by Micro System Designs is a DOS program that was used in 1990s to create images of floppy disks. A DiskDupe image consists of a *header* and a *raw disk image.* The header formats are different for versions 5 and 7 of DiskDupe: Version 7 header is 9216 bytes long and seems to be fixed (it was the same for all images I looked at); Version 5 header is 1280 bytes long and differs from image to image.

I don't know what is stored in the headers. I suppose, version 7 headers are just placeholders, because they are identical for all images. Version 5 headers might contain some metadata. By skipping the headers we get raw images of the disks.

***ddi2raw*** checks the first several bytes of the image to determine the version and, consequently, the length of the header. Then it stores the data after the header (which is the raw image) in the output file.

### Raw Disk Image

A raw disk image is a sector-by-sector copy of the original disk. Raw floppy disk images can be used as virtual floppy disks in virtualization applications, such as [QEMU](http://qemu.org/) and [VirtualBox](https://www.virtualbox.org/). A copy of the original floppy disk can be made by writing the image to a real floppy using, for example, [dd](https://en.wikipedia.org/wiki/Dd_%28Unix_software%29).

### Unknown Floppy Disk Image Formats

If the input image has an unknown format ***ddi2raw*** tries to find a raw disk image inside the input data. The program searches for *signature bytes,* that is, bytes that have known value and location for any floppy with an MS-DOS file system. Using the signature bytes, ***ddi2raw*** can locate and extract the raw disk image. This way, it should be possible to reliably extract raw disk images of floppies formatted in DOS (since version 2.0) and compatibles, such as MSX-DOS, PC DOS, and DR DOS, as well as floppies formatted in Atari TOS (since version 1.4).

If you encountered a DDI image that cannot be converted by ***ddi2raw*** you can open an issue on [the project page](https://github.com/SergiyKolesnikov/ddi2raw) and add a link to the image.

---

README.md

Copyright 2017 Sergiy Kolesnikov

Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
