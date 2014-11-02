from struct import Struct
from array import array
from binascii import hexlify

KB = 1024
MB = KB**2
GB = KB**3

M8  = Struct('<B')
M16 = Struct('<H')
M32 = Struct('<L')

class Memory(object):
	page_size = 1 * KB
	def __init__(self, size):
		self.mem = array('B',[0]*size)

	def read(self, offset, width):
		return ''.join(chr(x) for x in self.mem[offset:offset+width])

	def read8(self, offset):
		return M8.unpack_from(self.mem, offset)[0]

	def read16(self, offset):
		return M16.unpack_from(self.mem, offset)[0]

	def read32(self, offset):
		return M32.unpack_from(self.mem, offset)[0]

	def write8(self,offset, value):
		M8.pack_into(self.mem, offset, value&0xFF)

	def write16(self,offset, value):
		M16.pack_into(self.mem, offset, value&0xFFFF)

	def write32(self,offset, value):
		M32.pack_into(self.mem, offset, value&0xFFFFFFFF)

	def write(self, offset, s):
		self.mem[offset:offset+len(s)]=array('B', [ord(c) for c in s])

	def copy(self, source, dest, size):
		data = self.mem[source:source + size]
		self.mem[dest:dest + size] = data

	def dump(self):
		CHUNK=16
		for i in range(0,len(self.mem),CHUNK):
			print '%08x: %s' % (i,hexlify(self.mem[i:i+CHUNK]))

	def allocate(self, size, f = None):
		m = size % Memory.page_size
		if m != 0:
			allocated_size = size + (Memory.page_size - m)
		else:
			allocated_size = size

		p = len(self.mem)

		if f is not None:
			self.mem.fromfile(f, size)
			if size < allocated_size:
				self.mem.extend(0 for r in range(allocated_size - size))
		else:
			self.mem.extend(0 for r in range(allocated_size))

		return p


if __name__=='__main__':
	mem = Memory(32)

	#mem.write(0,'hello world')
	mem.write16(0,512)
	
	print mem.read32(0)
	mem.dump()