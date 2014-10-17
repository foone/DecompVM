import array,struct, sys
from source import Line 
REGISTERS=(
	('EAX', 'AX', 'AH', 'AL'),
	('EBX', 'BX', 'BH', 'BL'),
	('ECX', 'CX', 'CH', 'CL'),
	('EDX', 'DX', 'DH', 'DL'),
	('ESI','SI'),
	('EDI','DI'),
	('EBP','BP'),
	('ESP','SP'),
	('EIP',),
	('FLAGS',),
)

FLAGS=(
	'CF',
	'ZF',
	'SF',
)

class RegisterFile(object):
	def __init__(self):

		regs=[]

		size = len(REGISTERS)*4

		self.memory=array.array('B',[0] * size)

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

	def set(self, value):
		type_code = self.format
		if value < 0:
			type_code = type_code.lower()
		
		s = struct.pack(type_code, value)
		arr = array.array('B',struct.unpack(str(len(s))+'B',s))
		self.memory[self.offset:self.offset+self.width] = arr

	def get(self):
		type_code = self.format
		return struct.unpack(type_code,self.rawGet())[0]

	def rawGet(self):
		return self.memory[self.offset:self.offset+self.width]
	
	def hex(self):
		return ''.join(('%02X' % c) for c in self.rawGet())
	
	def __repr__(self):
		return 'Register(width=%d, data=%s, value=%s)' % (self.width,self.hex(),self.get())

class Register32(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 4)
		self.format = '<L'

class Register16(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 2)
		self.format = '<H'

class Register8(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 1)
		self.format = 'B'

class Register1(Register):
	def __init__(self, memory, offset):
		Register.__init__(self, memory, offset, 1)
		self.format = 'B'

	def set(self, value):
		if value!=0:
			value = 1 
		Register.set(self,value)


class CPU(object):
	def __init__(self):
		self.regs = RegisterFile()
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
		return self.source.get(self.regs.EIP.get(), None)

	def dump(self):
		print 'CPU STATUS:'
		self.regs.dump()
		
		ci = self.currentInstruction()
		print 'EIP is {}: {}'.format('valid' if ci is not None else 'invalid', ci)

	def walkSource(self):
		print 'CPU Source: '
		source = self.source
		seen = 0 
		current = sorted(source.keys())[0]
		while current in source:
			ci = source[current]
			print '  ',ci
			current += ci.size
			seen += 1

		if len(source)!=seen:
			print 'Warning! Unseen lines: %d' % (len(source)-seen)

if __name__ == '__main__':

	cpu=CPU()
	first_address = cpu.loadSource(sys.argv[1])
	cpu.jump_to(first_address)
	cpu.dump()

	cpu.walkSource()
