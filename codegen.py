#! /usr/bin/python
"""
Elegans type system runtime implementation
"""

tag_number = 0
def Tag():
	global tag_number
	tag_number += 1
	return "tag%s" % tag_number

def runtime_enumeration(options, context):
	output = []
	con = context.copy()
	for option in options:
		jump_over = Tag()
		context.hidden["type_failure_continuation"] = lambda context : ["  jmp %s\n" % jump_over]
		output.extend( option( con ) )
	return output

def runtime_type_error(context):
	return context.hidden["type_failure_continuation"]()

