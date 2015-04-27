# -*- coding: utf-8 -*-
import sys
import os
import base64
from proto.types_pb2 import Types
from google.protobuf import text_format

# Min, Max, other test values where applicaple
test_values = {
    "int32":         [ -2**31,   2**31-1,   0, -1, 1],
    "sint32":        [ -2**31,   2**31-1,   0, -1, 1],
    "uint32":        [ 0,        2**32-1,   1],
    "int64":         [ -2**63L,  2**63-1,   0, -1, 1],
    "sint64":        [ -2**63L,  2**63-1,   0, -1, 1],
    "uint64":        [ 0,        2**64-1,   1],
    "bool":          [ True, False],
    "nested_enum":   [ 0, 1, 2, -1],
    "foreign_enum":  [ 0, 4, 5, -2],
    "fixed64":       [ 0,        2**64-1,   1],
    "sfixed64":      [ -2**63,   2**63-1,   0, -1, 1],
    "double":        [ -1.0,     1.0,       0.0],
    "fixed32":       [ 0,        2**32-1,   1],
    "string":        [ "", "foo", "ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ"],
    "bytes":         [ bytes([0x01,0x02,0x03,0x04])],
    "sfixed32":      [ -2**31,   2**31-1,   0, -1, 1],
    "float":         [ -1.0,     1.0,       0.0]
}

fields_varint           = ["int32", "sint32", "uint32", "int64", "sint64", "uint64", "bool", "nested_enum", "foreign_enum"]
fields_64bit            = ["fixed64", "sfixed64", "double"]
fields_length_prefixed  = ["string", "bytes"]
fields_32bit            = ["fixed32", "sfixed32", "float"]

def as_hex(message):
    return ''.join(["%02X" % ord(x) for x in message.SerializeToString()])

def save_file(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)

def encode_value(value):
    if type(value) != bool:
        return base64.b64encode(str(value))
    if value:
        return base64.b64encode("1")
    else:
        return base64.b64encode("0")

def generate_single_value_fixtures(directory):
    for type in fields_varint + fields_64bit + fields_32bit + fields_length_prefixed:
        field = "f_" + type
        for value in test_values[type]:
            filename = directory + "/" + type + "_" + encode_value(value) + ".bin"
            m = Types()
            setattr(m, field, value)
            save_file(filename, m.SerializeToString())

def generate_fixtures(directory):
    generate_single_value_fixtures(directory)

def verify_fixtures(directory):
    print "Not implemented " + directory

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate test fixtures encoding and decoding proto file')
    parser.add_argument('-d', '--dir', dest='dir', metavar='DIR', required=True, help='Directory where to write generated binary data for test fixtures.')
    parser.add_argument(choices=['generate', 'verify'], dest='task', help="Generate test fixtures or verify generated test fixtures")

    args = parser.parse_args()

    if args.task == 'generate':
        generate_fixtures(os.getcwd() + "/" + args.dir)
    else:
        verify_fixtures(os.getcwd() + "/" + args.dir)
