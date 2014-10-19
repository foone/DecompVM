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
	def __init__(self, size):
		self.mem = array('B',[0]*size)

	def read8(self, offset):
		return M8.unpack_from(self.mem, offset)[0]

	def read16(self, offset):
		return M16.unpack_from(self.mem, offset)[0]

	def read32(self, offset):
		return M32.unpack_from(self.mem, offset)[0]

	def write8(self,offset, value):
		M8.pack_into(self.mem, offset, value)

	def write16(self,offset, value):
		M16.pack_into(self.mem, offset, value)

	def write32(self,offset, value):
		M32.pack_into(self.mem, offset, value)

	def write(self, offset, s):
		self.mem[offset:offset+len(s)]=array('B', [ord(c) for c in s])

	def dump(self):
		CHUNK=16
		for i in range(0,len(self.mem),CHUNK):
			print '%08x: %s' % (i,hexlify(self.mem[i:i+CHUNK]))


if __name__=='__main__':
	mem = Memory(32)

	#mem.write(0,'hello world')
	mem.write16(0,512)
	
	print mem.read32(0)
	mem.dump()