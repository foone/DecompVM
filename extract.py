#!/usr/bin/python
from subprocess import check_output
import re

END_OF_FUNC_RE = re.compile('^\s+([0-9a-f]+):\s*(?:cc)?\s+int3$',re.I)
EXE_PATH='3dmovie.exe'
FUNCTIONS=[
        {'start':'0x0434C00','name':'Decompress1'},
        {'start':'0x0438910','name':'Decompress2'},
]

def extractFunction(exe_path, offset):
    objdump=['objdump','-Mintel','-b','pe-i386','-d',exe_path,
            '--start-address={}'.format(offset),
            '-wz']
    ret=check_output(objdump)
    seen_header = -1
    for line in ret.splitlines():
        line=line.rstrip()
        if 'Disassembly of section .text' in line:
            seen_header = 2 # skip two lines
            continue
        if seen_header > 0:
            seen_header-=1
        elif seen_header==0:
            if END_OF_FUNC_RE.match(line):
                return # we ran into the end of the function
            yield line


if __name__=='__main__':
    for func in FUNCTIONS:
        with open(func['name']+'.s','w') as f:
            for line in extractFunction(EXE_PATH, func['start']):
                print >>f, line
