#! /usr/bin/python

import copy
import codegen

class Context(dict):
	pass

class Datum:
	def __init__(self, types=None, values=None):
		if types == None:
			types = []
		if values == None:
			values = []
		self.types = types
		self.values = values

	def copy(self):
		return Datum( copy.copy(self.types), copy.deepcopy(self.values) )

	def __str__(self):
		if not self.types:
			return "Nil"
		return "{ %s }" % ( " | ".join( "(%s) %s" % (" ".join(type_set), value) for type_set, value in zip(self.types, self.values) ) )

class Integer:
	def __init__(self, value):
		self.value = value

	def produce_code( self, output, stack, context ):
		output.append("  pushq %s\n" % self.value)
		return "success"

	def __str__(self):
		return str(self.value)

class Reference(Datum):
	pass

def type_reduce( d, desired, output, stack, context ):
	for type_set, val in zip(d.types, d.values):
		if desired in type_set:
			result = val.produce_code( output, stack, context )
			if result != "success":
				return "pass"
			return "success"
	return "pass"

always_horrible = lambda *args, **kwargs : "horrible"

call_handlers = {
					"Integer" : always_horrible,
					"ExtCall" : codegen.external_call,
				}

def ExtCall(name, arguments, retval):
	d = Datum( [["ExtCall"]], [{"name":name, "args":arguments, "ret":retval}] )
	return d

def load_standard_context():
	con = Context()

	openfile = open("libelegans/stdlib.elgdecl")
	for line in openfile:
		line = line.split("#")[0].strip()
		if not line: continue

		name, form, arguments, retval = line.split("::")
		name, form, arguments, retval = name.strip(), form.strip(), arguments.strip(), retval.strip()

		if form == "ext_call":
			con[name] = ExtCall(name, arguments, retval)

	return con

