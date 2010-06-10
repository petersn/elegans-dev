#! /usr/bin/python
"""
Elegans code generator
"""

import type_system
import unfolding_tracer

def external_call( d, output, stack, context ):
	"""Produce code for a call to an externally linked function."""
	arguments = d["args"].split(" ")
	stack_collect = stack[-len(arguments):]
	for arg, desired in zip(stack_collect, arguments):
		result = type_system.type_reduce( arg, desired, output, stack, context )
		if result != "success":
			return "pass"
	output.append("  call %s\n" % d["name"])
	for i in arguments:
		stack.pop()
	retvals = d["ret"].split(" ")
	for val in retvals:
		stack.append( type_system.Datum( [[val]], [None] ) )
	return "success"

