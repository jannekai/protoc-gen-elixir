import sys
from proto.types_pb2 import Types
from google.protobuf import text_format

# Min, Max, other test values where applicaple
test_values = {
	"int32": 		[ -2**31, 	2**31-1, 	0, -1, 1],
	"sint32": 		[ -2**31,	2**31-1, 	0, -1, 1],
	"uint32": 		[ 0, 		2**32-1,	1],
	"int64": 		[ -2**63, 	2**63-1,	0, -1, 1],
	"sint64": 		[ -2**63, 	2**63-1, 	0, -1, 1],
	"uint64":		[ 0, 		2**64-1,  	1],
	"nested_enum":	[ 0, 1, 2, -1],
	"foreign_enum":	[ 0, 4, 5, -2],
	"bool":			[ True, False],
	"fixed64": 		[ -2**63, 	2**63-1, 	0, -1, 1],
	"sfixed64": 	[ -2**63, 	2**63-1, 	0, -1, 1],
	"double":		[ -1.0, 	1.0,		0.0],
	"fixed32": 		[ -2**31, 	2**31-1, 	0, -1, 1],
	"sfixed32": 	[ -2**31, 	2**31-1, 	0, -1, 1],
	"float":		[ -1.0, 	1.0,		0.0]
}

fields_varint 			= ["int32", "sint32", "uint32", "int64", "sint64", "uint64", "bool", "nested_enum", "foreign_enum"]
fields_64bit 			= ["fixed64", "sfixed64", "double"]
fields_length_prefixed	= ["string", "bytes", "NestedMsg", "ForeignMsg"]
fields_32bit			= ["fixed32", "sfixed32", "float"]

def asHex(message):
	byteStr = message.SerializeToString()
	return ''.join(["%02X" % ord(x) for x in byteStr])

def main():
	for type in fields_varint:
		index = 0
		field = "f_" + type
		for value in test_values[type]:
			m = Types()
			setattr(m, field, value)
			out_file = field + "_" + str(value) + ".bin"
			print out_file + " : " + asHex(m)
			index += 1

if __name__ == '__main__':
	main()

