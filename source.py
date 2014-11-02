import re,sys
from operators import UnresolvedOperator, resolveOpcode
from arguments import UnresolvedArgument, resolveArgument
META_PATTERN = r'^([0-9A-F]+):\t([A-F0-9 ]+)\t({}) (.+)$'

REP_MOVS_RE=re.compile(META_PATTERN.format('REP MOVS'), re.IGNORECASE)
OTHER_OPS_RE=re.compile(META_PATTERN.format('[a-z]+'), re.IGNORECASE)

class Line(object):
	@staticmethod
	def parse(line):
		def attemptMatch(regex):
			m=regex.match(line)
			if m:
				addy = int(m.group(1),16)
				size = len(m.group(2).replace(' ',''))//2
				source =' ' .join((m.group(3), m.group(4)))
				return Line(addy, UnresolvedOperator(m.group(3).upper()), size, [UnresolvedArgument(x) for x in m.group(4).split(',')], source=source)
		for regex in (REP_MOVS_RE, OTHER_OPS_RE):
			obj = attemptMatch(regex)
			if obj:
				return obj
		return None

	def __init__(self, address, opcode, size, args = None, source = None):
		self.address = address
		self.opcode = opcode
		self.size = size
		self.args = args
		self.source = source

	def __repr__(self):
		return 'Line(address=%d, opcode=%s, size=%d, args=%r)' % (self.address, self.opcode, self.size, self.args)

	def hasUnresolvedReferences(self):
		return isinstance(self.opcode, UnresolvedOperator) or any(isinstance(x, UnresolvedArgument) for x in self.args)

	def resolveReferences(self, cpu):
		for i,arg in enumerate(self.args):
			if isinstance(arg, UnresolvedArgument):
				ret = resolveArgument(arg.value,cpu)
				if ret is not None:
					self.args[i] = ret
		if isinstance(self.opcode, UnresolvedOperator):
			ret = resolveOpcode(self.opcode, self.args)
			if ret is not None:
				self.opcode = ret

	def dump(self):
		if self.source is not None:
			print self.source
		else:
			print self

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