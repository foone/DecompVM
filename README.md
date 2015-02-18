DecompVM
========

An x86 emulator in python for running 3D Movie Maker decompression functions.

This is the replacement for DecompProxy, which is Windows-only. DecompVM runs anywhere Python does.

Steps to use:
==========

1. Get the 3DMOVIE.EXE file from a copy of Microsoft 3D Movie Maker, or 3DMTRIAL.EXE from [the demo](ftp://ftp.microsoft.com/deskapps/kids/3dmm.exe).
2. Get objdump(/.exe) from GNU bintools.
3. Run extract.py to generate Decompress(1/2).s
4. Run python decompress.py input.bin output.bin

Getting objtool for Windows
===========================
1. Get the [objtool binary](http://sourceforge.net/projects/mingw/files/MinGW/Base/binutils/binutils-2.24/binutils-2.24-1-mingw32-bin.tar.xz/download)
2. Get [GCC-core DLLs](http://sourceforge.net/projects/mingw/files/MinGW/Base/gcc/Version4/gcc-4.8.1-4/gcc-core-4.8.1-4-mingw32-dll.tar.lzma/download)
3. Get [libiconv DLLs](http://sourceforge.net/projects/mingw/files/MinGW/Base/libiconv/libiconv-1.14-3/libiconv-1.14-3-mingw32-dll.tar.lzma/download)
4. Get [libintl DLLs](http://sourceforge.net/projects/mingw/files/MinGW/Base/gettext/gettext-0.18.3.2-1/libintl-0.18.3.2-1-mingw32-dll-8.tar.xz/download)
5. Use 7zip to uncompress all files, and then do extract-here. go into the bin subdirectory and copy objdump.exe & all the DLLs into the DecompVM directory. 

TODO: 
=========

* Document what tiny subset of x86 this VM supports.
* Optimize the VM. Large decompressions are slow (300k=5s)
* ~~Test if the free demo has the decompression functions and make extract.py support them if so~~ **Done!**
* ~~Confirm that objdump can actually be used on windows (ie figure out the mingw dependencies mess).~~ **Done!**
* Write an automated way to grab the mingw files and auto-extract them.
* Add an automated way to get [the trial installer](ftp://ftp.microsoft.com/deskapps/kids/3DMM.EXE), extract it, and run extract.py on it. 

Credits & License:
==================

All code by Foone Turing, 2014.
Licensed under the GPL, v3.
