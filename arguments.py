import re
HEX_VALUE_RE=re.compile('^0x([0-9A-F]+)$',re.IGNORECASE)
DECIMAL_VALUE_RE=re.compile('^([0-9]+)$')
POINTER_RE = re.compile('^(BYTE|WORD|DWORD) PTR (?:[ed]s:)?\[([^]]+)\]$')
ADDRESS_REFERENCE_RE = re.compile('^\[([^]]+)\]$')
ADDRESS_REFERENCE_MATH_RE = re.compile(r'^(e\w\w)(?:[+-](e\w\w)\*(\d+))?(?:[+-]((?:0x)?[0-9a-fA-F]+))?$',re.IGNORECASE)

TYPE_TO_SIZE={'BYTE':1,'WORD':2,'DWORD':4}

def resolveArgument(val, cpu):
	reg = cpu.regs.resolve(val.upper())
	if reg:
		return RegisterReference(val.upper(), reg)
	hm=HEX_VALUE_RE.match(val)
	if hm:
		return LiteralReference(int(hm.group(1),16))
	dm=DECIMAL_VALUE_RE.match(val)
	if dm:
		return LiteralReference(int(dm.group(1),10))
	pm=POINTER_RE.match(val)
	if pm:
		return PointerReference(TYPE_TO_SIZE[pm.group(1)], resolveAddressReference(pm.group(2),cpu))
	am=ADDRESS_REFERENCE_RE.match(val)
	if am:
		return resolveAddressReference(am.group(1),cpu)
	
	print 'UNRESOLVED', val

def resolveAddressReference(arg, cpu):
	arm = ADDRESS_REFERENCE_MATH_RE.match(arg)
	args = []
	for arg in arm.groups():
		if arg is not None:
			args.append(resolveArgument(arg, cpu))
		else:
			args.append(arg)
	return AddressReference(*args)

class ArgumentReference(object):
	def __init__(self, value = None):
		self.value = value
	
	def get(self, cpu):
		raise NotImplementedError('called Reference.get!')
	
	def set(self, cpu, value):
		raise NotImplementedError('called Reference.set!')

	@property
	def size(self):
		raise NotImplementedError('called Reference.size!')

	def __repr__(self):
		return '%s(%s)' % (type(self).__name__,self.value)

class UnresolvedArgument(ArgumentReference):
	def __init__(self,value):
		self.value = value.strip()


	def get(self, cpu):
		raise ValueError('called get on unresolved argument!')

	def set(self, cpu, value):
		raise ValueError('called set on unresolved argument!')

class LiteralReference(ArgumentReference):
	def __init__(self, value):
		self.value = value

	def get(self, cpu):
		return self.value

	def set(self, cpu, value):
		raise ValueError('Tried to set a LiteralReference')

	@property
	def size(self):
		v = self.value
		adj = 1 
		if v<0:
			v=math.abs(v)
			adj = 2
		elif v==0:
			v = 1

		return int(math.ceil((int(math.log(v,2))+adj)/8.0))

class RegisterReference(ArgumentReference):
	def __init__(self, name, reg):
		self.name = name 
		self.reg = reg
	
	def get(self, cpu):
		return self.reg.get()
	
	def set(self, cpu, value):
		self.reg.set(value)

	@property
	def size(self):
		n=self.name
		if n.startswith('E') and len(n)==3:
			return 4
		elif n.endswith(('L','H')):
			return 1
		else:
			return 2


	def __repr__(self):
		return 'RegisterReference(%s, value=%s)' % (self.name,self.reg.get())



class AddressReference(ArgumentReference):
	def __init__(self, base=None, mult_reg = None, k = 0, adjust = 0):
		self.base = base
		self.mult_reg = mult_reg
		self.k = k
		self.adjust = adjust

	def get(self, cpu):
		address = 0 
		if self.base is not None:
			address += self.base.get(cpu)
		if self.mult_reg is not None:
			address += (self.mult_reg.get(cpu) * self.k.get(cpu))
		if self.adjust is not None:
			address += self.adjust.get(cpu)
		return address

	def set(self, cpu, value):
		raise ValueError('AddressReferences cannot be set')

	def __repr__(self):
		return 'AddressReference(base=%s + mult_reg=%s * k=%s + adjust=%s)' % (self.base, self.mult_reg, self.k, self.adjust)

class PointerReference(ArgumentReference):
	def __init__(self, width, value):
		ArgumentReference.__init__(self, value)
		self.width = width

	def __repr__(self):
		return 'PointerReference(width=%s, value=%s)' % (self.width,self.value)

	def get(self, cpu):
		address = self.value.get(cpu)
		if self.width == 4: 
			return cpu.ram.read32(address)
		elif self.width == 2:
			return cpu.ram.read16(address)
		else:
			return cpu.ram.read8(address)
	
	def set(self, cpu, value):
		address = self.value.get(cpu)
		if self.width == 4: 
			return cpu.ram.write32(address, value)
		elif self.width == 2:
			return cpu.ram.write16(address, value)
		else:
			return cpu.ram.write8(address, value)
		

	@property
	def size(self):
		return self.width
