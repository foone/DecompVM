#!/usr/bin/python
from subprocess import check_output
import re,os,sys

END_OF_FUNC_RE = re.compile('^\s+([0-9a-f]+):\s*(?:cc)?\s+int3$',re.I)
EXES={
	'3dmovie.exe':[
		{'start':'0x0434C00','name':'Decompress1'},
		{'start':'0x0438910','name':'Decompress2'},
	],
	'3DMTRIAL.EXE':[
		{'start':'0x0434C30','name':'Decompress1'},
		{'start':'0x0438940','name':'Decompress2'},
	]
}

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
	found_path = None
	for exe_path in EXES:
		if os.path.exists(exe_path):
			found_path = exe_path
			break
	if found_path is None:
		print 'No acceptable EXE files found'
		sys.exit()

	for func in EXES[found_path]:
		with open(func['name']+'.s','w') as f:
			for line in extractFunction(found_path, func['start']):
				print >>f, line
