# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
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
		self.namespace = namespace
		self.name = desc.name
		if namespace != "":
			self.fullname = self.namespace + "." + self.name
		else:
			self.fullname = self.name

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		return self.fullname

class Message:
	def __init__(self, desc, namespace):
		self.namespace = namespace
		self.name = desc.name
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
	namespace = fdesc.package
	process_messages(fdesc.message_type, result, namespace)
	process_enums(fdesc.enum_type, result, namespace)

def process_messages(descriptors, result, namespace):
	for desc in descriptors:
		if not desc.options.map_entry:
			result.add_message(desc, namespace)
			process_messages(desc.nested_type, result, namespace)
			process_enums(desc.enum_type, result, namespace)

def process_enums(descriptors, result, namespace):
	for desc in descriptors:
		result.add_enum(desc, namespace)

#
# Create result
#
def generate_response(result):
	response = plugin_pb2.CodeGeneratorResponse()
	f = response.file.add()
	f.name = "protobuf_generated.ex"

	for enum in result.enums:
		dbg(enum)

	return response

#
# Helpers
#
def dbg(*objs):
    print(*objs, file=sys.stderr)

def to_str(msg):
    return text_format.MessageToString(msg, as_utf8=True, as_one_line=True)

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
