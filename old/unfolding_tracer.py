#! /usr/bin/python

maximum_trace_depth = 8

import assembler
from type_system import *

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

	stack = []

	while ip < len(code):
		inst = code[ip]
		if inst[0] == "NOP": pass
		elif inst[0] == "LOOKUP":
			stack.append( context[inst[1]].copy() )
		elif inst[0] == "ADDR":
			stack.append( Reference( [["Ref"]], [context[inst[1]]] ) )
		elif inst[0] == "STORE":
			context
		elif inst[0] == "INT":
			stack.append( Datum( [["Integer"]], [Integer(inst[1])] ) )
		elif inst[0] == "CALL":
			d = stack.pop()
			# Inspect the object's various types and values
			handled = False
			for type_set, val in zip( d.types, d.values ):
				for t in type_set:
					call_handler = call_handlers[ t ]
					result = call_handler( val, output, stack, context )
					if result == "horrible":
						TypeFailure("Uncallable subtype %s of datum %s" % (t, d))
					elif result == "pass":
						pass
					elif result == "maybe":
						handled = True
					elif result == "success":
						handled = True
						break
			if not handled:
				TypeFailure("No good subtypes of datum %s for call." % d)
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

		#for name, addr in jumptable.iteritems():
			#print name, addr

		context = load_standard_context()

		output_code = Trace( code, jumptable["origin"], context )

		print "".join( output_code )

