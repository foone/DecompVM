import re,sys

META_PATTERN = r'^([0-9A-F]+):\t([A-F0-9 ]+)\t({}) (.+)$'

REP_MOVS_RE=re.compile(META_PATTERN.format('REP MOVS'), re.IGNORECASE)
OTHER_OPS_RE=re.compile(META_PATTERN.format('[a-z]+'), re.IGNORECASE)
HEX_VALUE_RE=re.compile('^0x([0-9A-F])+$',re.IGNORECASE)

class Line(object):
	@staticmethod
	def parse(line):
		def attemptMatch(regex):
			m=regex.match(line)
			if m:
				addy = int(m.group(1),16)
				size = len(m.group(2).replace(' ',''))//2
				return Line(addy, m.group(3).upper(), size, [UnresolvedReference(x) for x in m.group(4).split(',')])
		for regex in (REP_MOVS_RE, OTHER_OPS_RE):
			obj = attemptMatch(regex)
			if obj:
				return obj
		return None

	def __init__(self, address, opcode, size, args = None):
		self.address = address
		self.opcode = opcode
		self.size = size
		self.args = args

	def __repr__(self):
		return 'Line(address=%d, opcode=%s, size=%d, args=%r)' % (self.address, self.opcode, self.size, self.args)

	def hasUnresolvedReferences(self):
		return any(isinstance(x, UnresolvedReference) for x in self.args)

	def resolveReferences(self, cpu):
		for i,arg in enumerate(self.args):
			if isinstance(arg, UnresolvedReference):
				ret = self.resolveArgument(arg,cpu)
				if ret is not None:
					self.args[i] = ret

	def resolveArgument(self, arg, cpu):
		val = arg.value
		reg = cpu.regs.resolve(val.upper())
		if reg:
			return RegisterReference(val.upper(), reg)
		hm=HEX_VALUE_RE.match(val)
		if hm:
			return LiteralReference(int(hm.group(1),16))


class Reference(object):
	def __init__(self):
		self.value = None
	
	def get(self, cpu):
		raise NotImplemented('called Reference.get!')
	
	def set(self, cpu, value):
		raise NotImplemented('called Reference.set!')


	def __repr__(self):
		return '%s(%s)' % (type(self).__name__,self.value)

class UnresolvedReference(Reference):
	def __init__(self,value):
		self.value = value.strip()


	def get(self, cpu):
		raise ValueError('Unresolved reference!')

	def set(self, cpu, value):
		raise ValueError('Unresolved reference!')

class LiteralReference(Reference):
	def __init__(self, value):
		self.value = value

	def get(self, cpu):
		return self.value

	def set(self, cpu, value):
		raise ValueError('Tried to set a LiteralReference')

class RegisterReference(Reference):
	def __init__(self, name, reg):
		self.name = name 
		self.reg = reg
	
	def get(self, cpu):
		self.reg.get()
	
	def set(self, cpu, value):
		self.reg.set(value)

	def __repr__(self):
		return 'RegisterReference(%s, value=%s)' % (self.name,self.reg.get())

if __name__ == '__main__':
	vargs=set()
	with open(sys.argv[1],'r') as f:
		for line in f:

			cmd = Line.parse(line.strip())
			#print line.strip()
			#print cmd
			for arg in cmd.args:
				vargs.add(arg)

	for arg in sorted(list(vargs)):
		print repr(arg)