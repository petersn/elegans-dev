#! /usr/bin/python

import assembler

def ProduceInstructionCode( instr ):
	instr, args = instr[0], instr[1:]

	if instr == "NOP":
		return " ; NOP\n"
	elif instr == "LOOKUP":
		return "  pushd %s\n" % args[0]
	elif instr == "DEREF":
		return "  popd eax\n  mov eax, [eax]\n  pushd eax\n"
	elif instr == "CALL":
		return "  popd eax\n  call eax\n"
	elif instr == "INT":
		return "  pushd %s\n" % args[0]

	print "Unknown instruction:", instr
	raise Exception

def ProduceCode( code ):
	output = ""
	for instruction in code:
		output += ProduceInstructionCode( instruction )
	return output

if __name__ == "__main__":
	import sys
	for path in sys.argv[1:]:
		openfile = open(path)
		data = openfile.read()
		openfile.close()

		code = assembler.disassemble( assembler.assemble( data ) )

		print code

		asm = ProduceCode( code )

		print asm

