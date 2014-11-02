import array,struct, sys
from source import Line 
from ram import Memory, MB
from binascii import hexlify
import operators,arguments

REGISTERS=(
	('EAX', 'AX', 'AH', 'AL'),
	('EBX', 'BX', 'BH', 'BL'),
	('ECX', 'CX', 'CH', 'CL'),
	('EDX', 'DX', 'DH', 'DL'),
	('ESI', 'SI'),
	('EDI', 'DI'),
	('EBP', 'BP'),
	('ESP', 'SP'),
	('EIP',),
	('FLAGS',),
)

FLAGS=(
	'CF',
	'ZF',
	'SF',
	'OF'
)

class InvalidEIPError(Exception):
	pass

class RegisterFile(object):
	def __init__(self):

		regs=[]

		size = len(REGISTERS)*4

		self.memory=Memory(size)

		for i,reg_def in enumerate(REGISTERS):
			self.setupRegister32(i*4, *reg_def)
			regs.append(reg_def[0])

		for i, flag in enumerate(FLAGS):
			self.subregister(self.FLAGS, flag, i, Register1)
			regs.append(flag)

		self.all_regs = regs

	def setupRegister32(self, offset, name32, name16 = None, name8upper = None, name8lower = None):
		mem=self.memory
		setattr(self, name32, Register32(self.memory, offset))
		if name16 is not None:
			setattr(self, name16, Register16(self.memory, offset))
		if name8upper:
			setattr(self, name8upper, Register8(self.memory, offset+1))
		if name8lower:
			setattr(self, name8lower, Register8(self.memory, offset))

	def subregister(self, parent, name, offset, typeKlass):
		setattr(self, name, typeKlass(parent.memory, parent.offset + offset))

	def dump(self):
		for reg in self.all_regs:
			print '  {:<6} {}'.format(reg+':',getattr(self,reg))

	def resolve(self, name):
		try:
			r = getattr(self, name)
			if isinstance(r, Register):
				return r
		except AttributeError:
			return

class Register(object):
	def __init__(self, memory, offset, width):
		self.memory = memory
		self.offset = offset
		self.width = width 

	def hex(self):
		return hexlify(self.memory.read(self.offset,self.width))
	
	def adjust(self, delta):
		self.set(self.get()+delta)

	def __repr__(self):
		return 'Register(width=%d, data=%s, value=%s)' % (self.width,self.hex(),self.get())

class Register32(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 4)

	def get(self):
		return self.memory.read32(self.offset)

	def set(self, value):
		self.memory.write32(self.offset, value)

class Register16(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 2)
	
	def get(self):
		return self.memory.read16(self.offset)

	def set(self, value):
		self.memory.write16(self.offset, value)


class Register8(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 1)

	def get(self):
		return self.memory.read8(self.offset)
	def set(self, value):
		self.memory.write8(self.offset, value)

class Register1(Register8):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 1)

	def set(self, value):
		if value!=0:
			value = 1 
		Register8.set(self,value)


class CPU(object):
	def __init__(self, ram_size = 1*MB):
		self.regs = RegisterFile()
		self.ram = Memory(ram_size)
		self.regs.ESP.set(ram_size - 4)
		self.source = {}

	def loadSource(self, file):
		source = self.source
		first = True 
		first_address = None
		with open(file, 'r') as f:
			for line in f:
				line = Line.parse(line.strip())
				source[line.address] = line
				if first:
					first = False
					first_address = line.address
		self.resolveReferences()
		return first_address

	def resolveReferences(self):
		for addy, line in self.source.items():
			line.resolveReferences(self)

	def jump_to(self, address):
		self.regs.EIP.set(address)

	def currentInstruction(self):
		eip = self.regs.EIP.get()
		return eip, self.source.get(eip, None)

	def dump(self):
		print 'CPU STATUS:'
		self.regs.dump()
		
		eip, ci = self.currentInstruction()
		if ci is not None:
			ci.dump()
		else:
			print 'EIP is invalid!'

	def walkSource(self):
		print 'CPU Source: '
		source = self.source
		seen = 0 
		current = sorted(source.keys())[0]
		while current in source:
			ci = source[current]
			print '  %08x: %s' % (ci.address,ci)
			current += ci.size
			seen += 1

		if len(source)!=seen:
			print 'Warning! Unseen lines: %d' % (len(source)-seen)

	def step(self):
		regEIP = self.regs.EIP
		eip, ci = self.currentInstruction()
		if ci is None:
			raise InvalidEIPError()
		ci.opcode.execute(self, ci.args)
		if eip == regEIP.get(): # the instruction didn't set EIP, so we need to calculate it
			regEIP.set(eip+ci.size)


	def setFlags(self, **flags):
		for k,v in flags.items():
			getattr(self.regs,k).set(v)


	def loadFileIntoRAM(self, path):
		with open(path,'rb') as f:
			f.seek(0, 2)
			size = f.tell()
			f.seek(0)
			return self.ram.allocate(size, f), size
	
	def allocate(self, size):
		return self.ram.allocate(size)

	def push(self, value, size = 4):
		arg = arguments.LiteralReference(value, size)
		operators.opPUSH().execute(self, (arg,))

	def findSource(self,target, before=0, after=0):
		source = self.source

		results={}
		if target in source:
			ci=results[target]=source[target]
			if after:
				c=ci
				for i in range(after):
					nextaddress = c.address + c.size
					if nextaddress in source:
						c=results[nextaddress] = source[nextaddress]
					else:
						break
			if before:
				predecessors = self.buildPredecessorMap()
				c=ci
				for i in range(before):
					if c.address in predecessors:
						c = predecessors[c.address]
						results[c.address] = c 
					else:
						break
		return results

	def buildPredecessorMap(self):
		predecessors={}
		for ci in self.source.values():
			predecessors[ci.address+ci.size] = ci
		return predecessors

if __name__ == '__main__':
	import pdb

	cpu=CPU()
	first_address = cpu.loadSource(sys.argv[1])
	cpu.jump_to(first_address)

	data_offset, size = cpu.loadFileIntoRAM(sys.argv[2])
	print data_offset, size 

	decompressed_size = struct.unpack('>L', cpu.ram.read(data_offset + 4, 4))[0]
	print decompressed_size

	out_buffer = cpu.allocate(decompressed_size)
	print out_buffer

	out_sizebuffer = cpu.allocate(4)

	print out_sizebuffer

	cpu.push(out_sizebuffer)
	cpu.push(decompressed_size)
	cpu.push(out_buffer)
	cpu.push(size-8)
	cpu.push(data_offset+8)

	cpu.push(0) # fake return address

	cpu.dump()
	while cpu.regs.EIP.get()!=0:
		cpu.step()
		cpu.dump()

	print 'RETURNED TO 0'

