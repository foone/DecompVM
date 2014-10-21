from subprocess import check_output

EXE_PATH='3dmovie.exe'

functions=[
        {'start':'0x0434C00','stop':'0x043852C','name':'Decompress1'},
        {'start':'0x0438910','stop':'0x043AE87','name':'Decompress2'},
]
for func in functions:
    objdump=['objdump','-Mintel','-b','pe-i386','-d',EXE_PATH,
            '--start-address='+func['start'],
            '--stop-address='+func['stop'],
            '-wz']
    ret=check_output(objdump)
    seen_header = -1
    f = open(func['name']+'.s','w')
    for line in ret.splitlines():
        line=line.rstrip()
        if 'Disassembly of section .text' in line:
            seen_header = 2
            continue
        if seen_header>0:
            seen_header-=1
        elif seen_header==0:
            print >>f,line
    f.close()
            
            
