import cpu as cpu_module
import readline
import operators

class Debugger(object):
	HISTORY_FILE = '.decompvm_history'
	def __init__(self, cpu):
		self.cpu = cpu 
		self.breakpoints = set()
		self.last_cmd = 'NONE'
	
	def interactive(self):
		try:
			readline.read_history_file(Debugger.HISTORY_FILE)
		except IOError:
			pass
		cpu = self.cpu
		try:
			while True:
				cmd,args = self.prompt()
				if cmd in 'xq':
					return
				elif cmd == 's':
					cpu.step()
				elif cmd == 'k':
					self.stack(args)
				elif cmd == 'b':
					self.breakpoint(args)
				elif cmd == 'r':
					self.run()
				elif cmd == 'ret':
					self.runUntilRet()
				elif cmd == '?':
					self.evalPrint(args)
				elif cmd == 'l':
					self.listSource(args)
				else:
					print 'Unknown command! (%s)' % cmd
		finally:
			readline.write_history_file(Debugger.HISTORY_FILE)
	

	def listSource(self, args):
		cpu = self.cpu
		eip = cpu.regs.EIP.get()
		if args:
			start = self.eval(args)
			before,after=0,10
		else:
			before,after=5,5
			start=eip

		lines=cpu.findSource(start,before,after)

		for key,instruction in sorted(list(lines.items())):
			print ('%s%08x:' % ('>' if key==eip else ' ',key)),
			instruction.dump()


	def run(self):
		end_on=set([0]) | self.breakpoints
		cpu=self.cpu
		EIP = cpu.regs.EIP
		while EIP.get() not in end_on:
			try:
				cpu.step()
			except cpu_module.InvalidEIPError:
				print 'EIP invalid! aborting run'
				break

	def runUntilRet(self):
		cpu=self.cpu
		while True:
			_,ci = cpu.currentInstruction()
			if ci is not None and isinstance(ci.opcode,operators.opRET):
				break
			try:
				cpu.step()
			except cpu_module.InvalidEIPError:
				print 'EIP invalid! aborting run'
				break

	def breakpoint(self, args):
		if len(args)==0:
			print 'Breakpoints:'
			for b in sorted(list(self.breakpoints)):
				print '*',b
		elif len(args)==1:
			b=int(args[0],16)
			if b in self.breakpoints:
				self.breakpoints.discard(b)
				print 'Breakpoint removed'
			else:
				self.breakpoints.add(b)
				print 'Breakpoint added'
		else:
			print 'Invalid arguments.'


	def prompt(self):
		self.dump()
		eip, _ = self.cpu.currentInstruction()
		cmd = raw_input('%08X> ' % eip)
		if cmd == '':
			cmd = self.last_cmd
		else:
			self.last_cmd = cmd

		if cmd.startswith('?'):
			cmd='? '+cmd[1:]
		parts = cmd.split()
		return parts[0], parts[1:]

	def dump(self):
		regs= self.cpu.regs
		parts=[]
		for flag in cpu_module.FLAGS:
			v=getattr(regs,flag).get()
			parts.append('%s=%d' % (flag,v))
		print 'FLAGS:',' '.join(parts)

		for reg in 'EAX,ECX,EDX,EBX,ESP,EBP,ESI,EDI,,EIP'.split(','):
			if reg=='':
				print
			else:
				v=getattr(regs,reg).get()
				s= '%s %08x (%d)' % (reg, v, v)
				if reg !='EIP':
					print s
				else:
					eip, ci = self.cpu.currentInstruction()
					if ci is not None:
						print s,
						ci.dump()
					else:
						print '%s (invalid)' % s

	def stack(self, args):
		cpu = self.cpu
		if args:
			stack_top = self.eval(args)
		else:
			stack_top = cpu.regs.ESP.get()
		mem = self.cpu.ram
		for i in range(8):
			offset=stack_top+(i*4)
			data = mem.read32(offset)
			print '%s%08x: %08x (%d)' % ('>' if i==0 else ' ',offset,data, data)
		print


	def evalPrint(self, args):
		v = self.eval(args)
		pretty_v = repr(v)

		if isinstance(v, int):
			pretty_v = '%08x (%d)' % (v,v)

		print ' '.join(args),'=',pretty_v

	def eval(self, args):
		cpu=self.cpu
		regs=cpu.regs
		s = ' '.join(args)
		
		local={'cpu':cpu}
		for reg in 'EAX,ECX,EDX,EBX,ESP,EBP,ESI,EDI,EIP'.split(','):
			local[reg]=local[reg.lower()]=getattr(regs,reg).get()
		_,local['ci'] = cpu.currentInstruction()

		v = eval(s,{},local)
		if isinstance(v,list) and len(v)==1:
			v=cpu.ram.read32(v[0])
		return v
