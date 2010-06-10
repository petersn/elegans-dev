/*
 * Standard Elegans Library
 * Compliant to the Elegans standard library specification
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

void* elegans_allocate( uint64_t bytes ) {
	void* buffer;
	buffer = malloc( (size_t) bytes );
	return buffer;
}

void elegans_free( void* buffer ) {
	free( buffer );
}

void elegans_print( const char* ptr ) {
	printf("%s", ptr);
}

void elegans_exit( void ) {
	exit(0);
}

