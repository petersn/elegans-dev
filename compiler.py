#! /usr/bin/python

maximum_trace_depth = 8

import assembler
import type_system

def TypeFailure( msg ):
	print "Type Failure:", msg
	raise SystemExit

def Trace( code, ip, context, depth=0 ):
	"""
	Traces through the evaluation of the given code starting at ip.
	Trace will return an unfolded series of events in Elegans second level bytecode.
	When required, Trace will perform subtraces, up to a maximum depth set by maximum_trace_depth.
	"""
	output = []

	while ip < len(code):
		inst = code[ip]
		if inst[0] == "NOP": pass
		elif inst[0] == "LOOKUP":
			context.stack.append( context.symbols[inst[1]].copy() )
		elif inst[0] == "ADDR":
			pass
		elif inst[0] == "STORE":
			pass
		elif inst[0] == "INT":
			context.stack.append( type_system.Integer( inst[1] ) )
		elif inst[0] == "CALL":
			d = context.stack.pop()
			result = d.ask_callable( context )
			if result == type_system.No:
				TypeFailure("Uncallable object %s" % d)
			output.extend( d.call( context ) )
		ip += 1

	return output

if __name__ == "__main__":
	import sys
	for path in sys.argv[1:]:
		openfile = open(path)
		data = openfile.read()
		openfile.close()

		if not data.startswith( assembler.magic_number ):
			data = assembler.assemble( data )

		code, jumptable = assembler.disassemble( data )

		context = type_system.load_standard_context()

		output_code = Trace( code, jumptable["origin"], context )

		print "".join( output_code )

