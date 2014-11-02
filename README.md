DecompVM
========

An x86 emulator in python for running 3D Movie Maker decompression functions.

This is the replacement for DecompProxy, which is Windows-only. DecompVM runs anywhere Python does.

Steps to use:
==========

1. Get the 3DMOVIE.EXE file from a copy of Microsoft 3D Movie Maker 
2. Get objdump(/.exe) from GNU bintools.
3. Run extract.py to generate Decompress(1/2).s
4. Run python decompress.py input.bin output.bin

TODO: 
=========

* Document what tiny subset of x86 this VM supports
* Optimize the VM. Large decompressions are slow (300k=5s)
* Test if the free demo has the decompression functions and make extract.py support them if so.

Credits & License:
==================

All code by Foone Turing, 2014.
Licensed under the GPL, v3.
