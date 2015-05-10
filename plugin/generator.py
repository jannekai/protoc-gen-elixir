# -*- coding: utf-8 -*-
from __future__ import print_function
import sys, re
import plugin_pb2
import elixir_pb2
from google.protobuf import text_format
from google.protobuf.descriptor import FieldDescriptor as FD

class Result:
	def __init__(self):
		self.enums = []
		self.messages = []

	def add_enum(self, descriptor, namespace):
		self.enums.append(Enum(descriptor, namespace))

	def add_message(self, descriptor, namespace):
		self.messages.append(Message(descriptor, namespace))

class Enum:
	def __init__(self, desc, namespace):
		self.desc = desc
		self.namespace = namespace
		self.name = camel_case(desc.name)
		if namespace != "":
			self.fullname = self.namespace + "." + self.name
		else:
			self.fullname = self.name

	def __str__(self):
		o  = "defmodule %s do\n" % self.fullname
		o += "  def type, do: :enum\n"
		o += "  def module, do: %s\n" % self.fullname
		o += "  \n"
		o += "".join(["  def value(:%s), do: %s\n" %(snake_case(value.name), value.number) for value in self.desc.value])
		o += "  \n"
		o += "".join(["  def key(%s), do: :%s\n" %(value.number, snake_case(value.name)) for value in self.desc.value])
		o += "  \n"
		o += "  def values, do: [%s]\n" % ", ".join([str(value.number) for value in self.desc.value])
		o += "  def keys, do: [%s]\n" % ", ".join([":" + snake_case(value.name) for value in self.desc.value])
		o += "end\n\n"

		return o

class Message:
	def __init__(self, desc, namespace):
		self.namespace = namespace
		self.name = camel_case(desc.name)
		if namespace != "":
			self.fullname = self.namespace + "." + self.name
		else:
			self.fullname = self.name

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return self.fullname

#
# Process files
#
def process_file(fdesc, result):
	namespace = camel_case(fdesc.package)
	process_messages(fdesc.message_type, result, namespace)
	process_enums(fdesc.enum_type, result, namespace)

def process_messages(descriptors, result, namespace):
	for desc in descriptors:
		if not desc.options.map_entry:
			result.add_message(desc, namespace)
			process_messages(desc.nested_type, result, namespace + "." + desc.name)
			process_enums(desc.enum_type, result, namespace + "." + desc.name)

def process_enums(descriptors, result, namespace):
	for desc in descriptors:
		result.add_enum(desc, namespace)

#
# Create result
#
def generate_response(result):
	content = ""
	for enum in sorted(result.enums, key=lambda enum: enum.fullname):
		content += str(enum)
	dbg(content)

	# Create response message
	response = plugin_pb2.CodeGeneratorResponse()
	f = response.file.add()
	f.name = "protobuf_generated.ex"
	f.content = content

	return response

#
# Helpers
#
def dbg(*objs):
    print(*objs, file=sys.stderr)

def to_str(msg):
    return text_format.MessageToString(msg, as_utf8=True, as_one_line=True)

def snake_case(id):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', id)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def camel_case(id):
	parts = id.lower().split('_')
	return "".join(x.title() for x in parts)

#
# Main
#
def main():
	data = sys.stdin.read()
	request = plugin_pb2.CodeGeneratorRequest.FromString(data)

	result = Result()
	for filename in request.file_to_generate:
		for fdesc in request.proto_file:
			if filename == fdesc.name:
				process_file(fdesc, result)

	# Generated file
	response = generate_response(result)
	sys.stdout.write(response.SerializeToString())

if __name__ == '__main__':
	main()
