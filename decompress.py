import sys,struct
from cpu import CPU
from debugger import Debugger
from ram import Memory, MB

class Decompressor(object):
	SOURCEFILES={
		'KCD2': 'Decompress2.s',
		'KCDC': 'Decompress1.s',
	}
	def __init__(self, datafile):
		
		cpu = self.cpu = CPU(4*MB)


		self.data_offset,self.size = data_offset, size = cpu.loadFileIntoRAM(datafile)
		

		self.decompressed_size = decompressed_size = struct.unpack('>L', cpu.ram.read(data_offset + 4, 4))[0]

		marker = cpu.ram.read(data_offset, 4)

		first_address = cpu.loadSource(Decompressor.SOURCEFILES[marker])
		cpu.jump_to(first_address)
	
		self.out_buffer = cpu.allocate(decompressed_size)

		self.out_sizebuffer = cpu.allocate(4)

	def call(self):
		cpu = self.cpu

		cpu.push(self.out_sizebuffer)
		cpu.push(self.decompressed_size)
		cpu.push(self.out_buffer)
		cpu.push(self.size-8)
		cpu.push(self.data_offset+8)

		cpu.push(0) # fake return address

	def callTest(self):
		cpu = self.cpu

		cpu.regs.ESP.set(0x0012FCBC + 4)

		self.out_sizebuffer = 0x0012FD24
		self.out_buffer     = 0x0015FEC0

		old_data = self.data_offset

		self.data_offset    = 0x0015D930 - 8 
		cpu.ram.copy(old_data, self.data_offset, self.size)

		cpu.push(self.out_sizebuffer)
		cpu.push(self.decompressed_size)
		cpu.push(self.out_buffer)
		cpu.push(self.size - 8)
		cpu.push(self.data_offset + 8)

		cpu.push(42) # fake return address

		regs = """EAX 0015D930
ECX 004D5238
EDX 00002570
EBX 004DEE88
#ESP 0012FCA8
EBP 0015D930
ESI 0015FEC0
EDI 0004BF1C
EIP 00438910"""
		for line in regs.splitlines():
			reg,value=line.split()
			if reg.startswith('#'): 
				continue
			getattr(cpu.regs,reg).set(int(value,16))

	def runUntilEIP0(self):
		cpu = self.cpu
		EIP = cpu.regs.EIP
		while EIP.get()!=0:
			cpu.step()

	def saveResults(self, path):
		data = self.cpu.ram.read(self.out_buffer, self.decompressed_size)
		with open (path,'wb') as f:
			f.write(data)
if __name__=='__main__':
	import sys
	decomp = Decompressor(sys.argv[1])
	decomp.call()
	decomp.runUntilEIP0()
	decomp.saveResults(sys.argv[2])