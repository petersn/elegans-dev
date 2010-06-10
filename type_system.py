#! /usr/bin/python
"""
Elegans type system JIT-side implementation
"""

import copy
import codegen

@apply
class Yes:
	def __imul__(self, other):
		return other
	def __iadd__(self, other):
		return Yes

@apply
class No:
	def __imul__(self, other):
		return No
	def __iadd__(self, other):
		return other

@apply
class Maybe:
	def __imul__(self, other):
		if other == No:
			return No
		return Maybe
	def __iadd__(self, other):
		if other == Yes:
			return Yes
		return Maybe

class Context:
	def __init__(self):
		self.symbols  = { }
		self.hidden   = {
							"type_failure_continuation" : lambda context : ["  jmp rt_type_error\n"],
						}
		self.stack    = [ ]

	def copy(self):
		con = Context()
		con.symbols = copy.deepcopy(self.symbols)
		con.hidden  = copy.deepcopy(self.hidden)
		con.stack   = copy.deepcopy(self.stack)
		return con

class Datum:
	def __init__(self, types=None):
		if types == None:
			types = []
		self.types = types

	def typestring(self):
		if not self.types:
			return ""
		else:
			return "(%s) " % (" ".join(t in self.types))

	def extend_definition(self, obj):
		return DatumUnion([self, obj])

	def __str__(self):
		if not self.types:
			return "Nil"
		return " ".join(self.types)

class DatumUnion(Datum):
	def __init__(self, objs=None):
		if objs == None:
			objs = []
		self.objs = objs

	def extend_definition(self, obj):
		return DatumUnion( self.objs + [obj] )

	def __str__(self):
		return "{ %s }" % (", ".join( str(obj) for obj in self.objs ) )

	def ask_callable(self, context):
		answer = No
		for obj in self.objs:
			answer += obj.ask_callable(context)
		return answer

	def ask_is_of_type(self, t):
		answer = No
		for obj in self.objs:
			answer += obj.ask_is_of_type( t )
		return answer

	def copy(self):
		return copy.deepcopy(self)

	def call(self, context):
		maybe_code = []
		for obj in self.objs:
			result = obj.ask_callable(context)
			if result == Yes:
				return codegen.runtime_enumeration( maybe_code, context ) + obj.call(context)
			elif result == Maybe:
				maybe_code.append( obj.call )
		return codegen.runtime_enumeration( maybe_code, context ) + codegen.runtime_type_error(context)

	def production_code(self, context):
		output = []
		for obj in self.objs:
			output.extend( obj.production_code(context) )
		return output

class Uncallable:
	def ask_callable(self, context):
		return No

def IsOfType(type_name):
	class _IsOfType:
		def ask_is_of_type( self, t ):
			if t == type_name:
				return Yes
			return No
	return _IsOfType

class Integer(Datum, Uncallable, IsOfType("Integer")):
	def __init__(self, value=0):
		Datum.__init__(self, ["Integer"])
		self.value = value

	def copy(self):
		return Integer(self.value)

	def production_code(self, context):
		return ["  pushd %s\n" % self.value]

	def __str__(self):
		return "%s%s" % (self.typestring(), self.value)

primitive_name_lookup = {
							"Integer" : Integer,
						}

class ExternalFunctionHandle(Datum, IsOfType("External")):
	def __init__(self, name, arguments, retval):
		Datum.__init__(self, ["External"])
		self.name = name
		self.arguments = arguments
		self.retval = retval

	def production_code(self, context):
		return ["  push %s\n" % self.name]

	def ask_callable(self, context):
		answer = Yes
		if self.arguments != "Nil":
			arguments = self.arguments.split(" ")
			stack_collect = context.stack[-len(arguments):]
			for arg, desired in zip(stack_collect, arguments):
				answer *= arg.ask_is_of_type( desired )
		return answer

	def call(self, context):
		output = []
		for i in self.arguments.split(" "):
			output.extend( context.stack.pop().production_code( context ) )
		output.append( "  call %s\n" % self.name )
		if self.retval != "Nil":
			retval = self.retval.split(" ")
			for val in retval:
				context.stack.append( primitive_name_lookup[val]( None ) )
		return output

	def copy(self):
		return ExternalFunctionHandle(self.name, self.arguments, self.retval)

def load_standard_context():
	con = Context()

	openfile = open("libelegans/stdlib.elgdecl")
	for line in openfile:
		line = line.split("#")[0].strip()
		if not line: continue

		name, form, arguments, retval = line.split("::")
		name, form, arguments, retval = name.strip(), form.strip(), arguments.strip(), retval.strip()

		if form == "ext_call":
			obj = ExternalFunctionHandle(name, arguments, retval)
			if name in con.symbols:
				con.symbols[name] = con.symbols[name].extend_definition( obj )
			else:
				con.symbols[name] = obj

	return con

