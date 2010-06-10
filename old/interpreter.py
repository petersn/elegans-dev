#! /usr/bin/python

import assembler
import sys

class Value:
	def __init__(self, types=None, value=None, ref=None):
		if types == None:
			types = []
		self.types = types[:]
		self.value = value
		self.ref   = ref

	def copy(self):
		return Value( self.types, self.value, self.ref )

def global_fail():
	print "Global failure continuation taken."
	raise SystemExit

namespace = {
				"print" : Value( types=["Lambda"], value=lambda fail=global_fail : sys.stdout.write( str(stack.pop().value)+"\n" ) ),
				"exit"  : Value( types=["Lambda"], value=lambda fail=global_fail : exit() )
			}

stack     = [ ]

constant_value = 0
def Constant():
	global constant_value
	constant_value += 1
	return constant_value

def interpret( code, ip=0, fail_continuation = global_fail ):
	while ip < len(code):
		inst = code[ip]
		if inst[0] == "NOP":
			pass
		elif inst[0] == "LOOKUP":
			stack.append( namespace[ inst[1] ].copy() )
		elif inst[0] == "ADDR":
			stack.append( Value( types=["Token"], ref=namespace[ inst[1] ] ) )
		elif inst[0] == "DEREF":
			stack.append( stack.pop().ref )
		elif inst[0] == "STORE":
			token = stack.pop().ref
			value = stack.pop()
			token.value = value
		elif inst[0] in ("INT", "FLOAT"):
			stack.append( Value( types=[inst[0]], value=inst[1] ) )
		elif inst[0] == "DUP":
			stack.append( stack[-1].copy() )
		elif inst[0] == "DROP":
			stack.pop()
		elif inst[0] == "SWAP":
			stack[-1], stack[-2] = stack[-2], stack[-1]
		elif inst[0] == "ROT":
			stack[-1], stack[-2], stack[-3] = stack[-3], stack[-1], stack[-2]
		elif inst[0] == "CAST=":
			stack[-1].types = stack.pop().value
		elif inst[0] == "CAST+":
			type_list = stack.pop().value
			for t in type_list:
				if t not in stack[-1].types:
					stack[-1].types.append( t )
		elif inst[0] == "CAST-":
			type_list = stack.pop().value
			for t in type_list:
				if t in stack[-1].types:
					stack[-1].types.remove( t )
		elif inst[0] == "ASSERT=":
			type_list = stack.pop().value
			if stack[-1].types != type_list:
				fail_continuation()
		elif inst[0] == "ASSERT-":
			type_list = stack.pop().value
			for t in type_list:
				if t in stack[-1].types:
					fail_continuation()
		elif inst[0] == "ASSERT+":
			type_list = stack.pop().value
			for t in type_list:
				if t not in stack[-1].types:
					fail_continuation()
		elif inst[0] == "NONCE":
			stack.append( Value( types=["Type"], value=[Constant()] ) )
		elif inst[0] == "JOIN":
			type_list = stack.pop().value
			stack[-1].value += type_list
		elif inst[0] == "JUMP":
			ip = stack.pop().value
			continue
		elif inst[0] == "BRANCH":
			test = stack.pop().value
			destination = stack.pop().value
			if test:
				ip = destination
				continue
		elif inst[0] == "CALL":
			next = stack.pop()
			if "Code" in next.types:
				interpret( code, next.value, fail=fail_continuation )
			elif "Lambda" in next.types:
				next.value( fail=fail_continuation )
			else:
				fail_continuation()
		elif inst[0] == "FAIL":
			fail_continuation()
		elif inst[0] == "RETURN":
			return
		ip += 1

if __name__ == "__main__":
	import sys
	for path in sys.argv[1:]:
		openfile = open(path)
		data = openfile.read()
		openfile.close()

		if not data.startswith( assembler.magic_number ):
			data = assembler.assemble( data )

		code, jumptable = assembler.disassemble( data )

		for name, addr in jumptable.iteritems():
			namespace[name] = Value( types=["Code"], value=addr )

		interpret( code, ip=jumptable["start"] )

