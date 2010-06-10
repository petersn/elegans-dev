
format ELF64

macro ELG name
{
	public _#name
	#name:
	_#name:
}

section '.code' executable

ELG elegans_exit

	xor edi, edi
	mov eax, 60
	syscall

