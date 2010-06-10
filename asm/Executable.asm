
format ELF64

include 'elegans.inc'

section '.code' executable

public _start
	_start:

include 'temp/code.asm'

	call elegans_exit

section '.data' writeable

include 'temp/data.asm'

