from __future__ import print_function

import sys
import plugin_pb2
import elixir_pb2

def log(msg):
	print(msg, file=sys.stderr)

def parse_file(fd):
	log("")
	log("fd.name: " + fd.name)
	log("fd.package: " + fd.package)
	log("fd.dependency: " + ("".join(fd.dependency)))

def main():
	data = sys.stdin.read()
	request = plugin_pb2.CodeGeneratorRequest.FromString(data)
	response = plugin_pb2.CodeGeneratorResponse()

	for fdesc in request.proto_file:
		file = parse_file(fdesc)

if __name__ == '__main__':
	main()
