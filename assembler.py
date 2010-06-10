#! /usr/bin/python

magic_number = '\xf2\xef-\x7f\xdbeP.'

functions = list(enumerate((

# General
	("NOP"),

# Memory access
	("LOOKUP", "SYMBOL"),
	("ADDR", "SYMBOL"),
	("DEREF"),
	("STORE"),

# Numeric
	("INT", "INTEGER"),
	("FLOAT", "FLOAT"),
	("DUP"),
	("DROP"),
	("SWAP"),
	("ROT"),

# Type operations
	("CAST="),
	("CAST+"),
	("CAST-"),
	("ASSERT="),
	("ASSERT+"),
	("ASSERT-"),
	("NONCE"),
	("JOIN"),

# Branching
	("JUMP"),
	("BRANCH"),

# Function calling
	("ENTRY", "SYMBOL"),
	("CALL"),
	("FAIL"),
	("RETURN"),

)))

def serialize( data ):
	output = ""
	for datum, format in data:
		if format == "SYMBOL":
			output += chr(len(datum)) + datum
		elif format == "INTEGER":
			try:
				datum = str(int(datum))
				output += chr(len(datum)) + datum
			except ValueError:
				print "Invalid INTEGER field for instruction:"
				print repr(datum)
				raise Exception
		elif format == "FLOAT":
			try:
				datum = str(float(datum))
				output += chr(len(datum)) + datum
			except ValueError:
				print "Invalid INTEGER field for instruction:"
				print repr(datum)
				raise Exception
	return output

def consume( code, desc ):
	output = []
	for format in desc:
		if format == "SYMBOL":
			length, code = ord(code[0]), code[1:]
			output.append( code[:length] )
			code = code[length:]
		if format == "INTEGER":
			length, code = ord(code[0]), code[1:]
			output.append( int(code[:length]) )
			code = code[length:]
		if format == "FLOAT":
			length, code = ord(code[0]), code[1:]
			output.append( float(code[:length]) )
			code = code[length:]
	return code, output

def assemble( code ):
	output = ""
	for rawline in code.split("\n"):
		line = rawline.split("#")[0].strip()
		if not line: continue
		args = line.split(" ")
		f, args = args[0], args[1:]
		for opcode, desc in functions:
			if type(desc) == str and desc == f and not args:
				output += chr(opcode)
				break
			elif len(desc) == len(args)+1 and f == desc[0]:
				output += chr(opcode) + serialize( zip( args, desc[1:] ) )
				break
		else:
			print "Invalid instruction:"
			print repr(rawline)
			raise Exception
	return magic_number + output

def disassemble( code ):
	if code.startswith( magic_number ):
		code = code[len(magic_number):]
	output = []
	jumptable = { }
	addr = 0
	while code:
		for opcode, desc in functions:
			if ord(code[0]) == opcode:
				code = code[1:]
				if type(desc) == str:
					output.append( [ desc ] )
				else:
					code, results = consume( code, desc[1:] )
					# Special handling for co-routine entry points
					if desc[0] == "ENTRY":
						jumptable[ results[0] ] = addr
					else:
						output.append( [ desc[0] ] + results )
				addr += 1
				break
		else:
			print "Invalid opcode:", ord(code[0])
			raise Exception
	return output, jumptable

def pretty( code ):
	code, jumptable = code
	return "\n".join( " ".join( str(i) for i in instr ) for instr in code ) + "\n\nJump table:\n" + \
	       "\n".join( "%s : %s\n" % (name, addr) for name, addr in jumptable.iteritems() )

if __name__ == "__main__":
	import sys
	for path in sys.argv[1:]:
		openfile = open(path)
		data = openfile.read()
		openfile.close()

		code = assemble(data)

		if path.endswith(".easm"):
			path = path[:-5]

		openfile = open(path+".ebc", "w")
		openfile.write(code)
		openfile.close()

		print "Input size:  %.2f kbytes" % (len(data)/1024.0)
		print "Output size: %.2f kbytes" % (len(code)/1024.0)
		print "Compression: %.2f%%" % (float(len(code)) / len(data) * 100.0)
		print
		print repr(code)
		print
		print pretty( disassemble(code) )

