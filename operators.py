from arguments import RegisterReference
import operator as op
class Operator(object):
	def execute(self, cpu, args):
		raise NotImplementedError('called abstract Operator.execute!')


class UnresolvedOperator(Operator):
	def __init__(self, code):
		self.code = code

	def __repr__(self):
		return 'UnresolvedOperator<%s>' % self.code

class opMOV(Operator):
	def execute(self, cpu, args):
		aTo,aFrom = args
		aTo.set(cpu,aFrom.get(cpu))

class opINCDEC(Operator):
	def __init__(self, delta):
		self.delta = delta 

	def execute(self, cpu, args):
		(aTarget,) = args
		v = aTarget.get(cpu) + self.delta
		aTarget.set(cpu, v)

class opSUB(Operator):
	def execute(self, cpu, args):
		aTarget,aAmount = args
		v = aTarget.get(cpu) - aAmount.get(cpu)
		aTarget.set(cpu, v)

class opADD(Operator):
	def execute(self, cpu, args):
		aTarget,aAmount = args
		v = aTarget.get(cpu) + aAmount.get(cpu)
		aTarget.set(cpu, v)

class opPUSH(Operator):
	def execute(self, cpu, args):
		(aValue,) = args
		ESP = cpu.regs.ESP
		sz = aValue.size
		ESP.adjust(-4 if sz == 4 else -2)
		(cpu.ram.write32 if sz == 4 else cpu.ram.write16)(ESP.get(), aValue.get(cpu))

class opPOP(Operator):
	def execute(self, cpu, args):
		(aDest,) = args
		ESP = cpu.regs.ESP
		sz = aDest.size
		value = (cpu.ram.read32 if sz == 4 else cpu.ram.read16)(ESP.get())
		ESP.adjust(4 if sz == 4 else 2)
		aDest.set(cpu, value)

class opRET(opPOP):
	def execute(self, cpu, args):
		eip = RegisterReference('EIP',cpu.regs.EIP)
		opPOP.execute(self,cpu,[eip])
		if args:
			(aBytesToPop,) = args
			cpu.regs.ESP.adjust(aBytesToPop.get(cpu))

class opBITWISE(Operator):
	def __init__(self, op):
		self.op = op 

	def execute(self, cpu, args):
		(aTarget,aOther) = args
		v = self.op(aTarget.get(cpu), aOther.get(cpu))
		aTarget.set(cpu, v)

class opNEG(Operator):
	def execute(self, cpu, args):
		(aDest,) = args
		aDest.set(cpu, -aDest.get(cpu))

class opTEST(Operator):
	def execute(self, cpu, args):
		(aFirst, aSecond) = args
		value = aFirst.get(cpu) & aSecond.get(cpu)
		self.setFlags(value, aFirst.size)

	def setFlags(self, value, size, cf = 0, of = 0 ):
		cpu.setFlags(CF = cf, OF = of, ZF = int(value == 0), SF = int(bool(value & (2<<(size*8-1)-1))))

class opLEA(Operator):
	def execute(self, cpu, args):
		(aDest, aAddress) = args
		aDest.set(cpu, aAddress.get(cpu))
		
class opCMP(opTEST):
	def execute(self, cpu, args):
		(aSource, aAdjust) = args
		asrc = aSource.get(cpu) 
		ret = asrc - aAddress.get(cpu)

		cf= int(asrc < aAddress.get(cpu))
		self.setFlags(ret, aSource.size, cf)


class opJMP(Operator):
	def execute(self, cpu, args):
		(aDestination,) = args
		cpu.regs.EIP.set(aDestination)


class opJCC(opJMP):
	@staticmethod
	def evalConditional(code, regs):
		if code=='JA':
			return regs.CF==0 and regs.ZF == 0
		elif code=='JAE':
			return regs.CF==0
		elif code=='JB':
			return regs.CF==1
		elif code=='JE':
			return regs.ZF==1
		elif code=='JG':
			return regs.ZF and regs.CF==regs.OF
		elif code=='JGE':
			return regs.SF==regs.OF

	def __init__(self, code):
		self.code = code
	def execute(self, cpu, args):
		code = self.code
		regs = cpu.regs
		if opJCC.evalConditional(code, regs):
			opJMP.execute(self, cpu, args)


def resolveOpcode(opcode, args): 
	code = opcode.code
	if code == 'MOV':
		return opMOV()
	elif code == 'INC':
		return opINCDEC(+1)
	elif code == 'DEC':
		return opINCDEC(-1)
	elif code == 'SUB':
		return opSUB()
	elif code == 'ADD':
		return opADD()
	elif code == 'JMP':
		return opJMP()
	elif code == 'PUSH':
		return opPUSH()
	elif code == 'POP':
		return opPOP()
	elif code == 'RET':
		return opRET()
	elif code == 'AND':
		return opBITWISE(op.__and__)
	elif code == 'OR':
		return opBITWISE(op.__or__)
	elif code == 'SHR':
		return opBITWISE(op.__rshift__)
	elif code == 'SHL':
		return opBITWISE(op.__lshift__)
	elif code == 'XOR':
		return opBITWISE(op.__xor__)
	elif code == 'NEG':
		return opNEG()
	elif code == 'TEST':
		return opTEST()
	elif code == 'LEA':
		return opLEA()
	elif code == 'CMP':
		return opCMP()
	elif code in ('JA', 'JAE', 'JB', 'JE', 'JG', 'JGE'):
		return opJCC(code)