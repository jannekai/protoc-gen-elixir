# -*- coding: utf-8 -*-
import sys
import os
import base64
import codecs
import json
from proto2dict import to_dict
from proto.types_pb2 import TypesMsg, EmptyMsg, ForeignMsg, RecursiveMsg
from google.protobuf import text_format
from google.protobuf.descriptor import FieldDescriptor as FD

nestedMsgDefault = TypesMsg.NestedMsg()
nestedMsgOne = TypesMsg.NestedMsg()
nestedMsgOne.value = 1

emptyMsg = EmptyMsg()

foreignMsgDefault = ForeignMsg()
foreignMsgOne = ForeignMsg()
foreignMsgOne.value = 1

recursiveMsg = RecursiveMsg()
recursiveMsg.value = 1
recursiveMsg.child.value = 2
recursiveMsg.child.child.value = 3

# Min, Max, other test values where applicaple
test_values = {
    "int32":        [ -2**31,   2**31-1,    0, -1, 1],
    "sint32":       [ -2**31,   2**31-1,    0, -1, 1],
    "uint32":       [ 0,        2**32-1,    1],
    "int64":        [ -2**63L,  2**63-1,    0, -1, 1],
    "sint64":       [ -2**63L,  2**63-1,    0, -1, 1],
    "uint64":       [ 0,        2**64-1,    1],
    "bool":         [ True,     False],
    "nested_enum":  [ 0, 1, 2, -1],
    "foreign_enum": [ 0, 4, 5, -2],
    "fixed64":      [ 0,        2**64-1,    1],
    "sfixed64":     [ -2**63,   2**63-1,    0, -1, 1],
    "double":       [ -1.0,     1.0,        0.0],
    "fixed32":      [ 0,        2**32-1,    1],
    "string":       [ "",       "foo",      "ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ"],
    "bytes":        [ str(bytearray([1,2,3,4,0,255]))],
    "nested_msg":   [ nestedMsgDefault,     nestedMsgOne],
    "foreign_msg":  [ foreignMsgDefault,    foreignMsgOne],
    "empty_msg":    [ emptyMsg,             emptyMsg ],
    "sfixed32":     [ -2**31,   2**31-1,    0, -1, 1],
    "float":        [ -1.0,     1.0,        0.0]
}

fields_varint           = ["int32", "sint32", "uint32", "int64", "sint64", "uint64", "bool", "nested_enum", "foreign_enum"]
fields_64bit            = ["fixed64", "sfixed64", "double"]
fields_length_prefixed  = ["string", "bytes", "nested_msg", "foreign_msg", "empty_msg"]
fields_32bit            = ["fixed32", "sfixed32", "float"]
fields_all              = fields_varint + fields_64bit + fields_length_prefixed + fields_32bit;

def to_json(m):
    return json.dumps(to_dict(m))

def save_proto_data(filename, data):
    with open(filename, 'wb') as f:
        f.write(data)

def save_json_data(filename, data):
    with open(filename, 'w') as f:
        f.write(data)

def generate_single_field_fixtures(directory):
    for type in fields_all:
        field = "f_" + type
        for index, value in enumerate(test_values[type]):
            m = TypesMsg()
            if m.DESCRIPTOR.fields_by_name[field].type == FD.TYPE_MESSAGE:
                getattr(m, field).CopyFrom(value)
            else:
                setattr(m, field, value)

            basename = directory + "/" + type + "_test_" + str(index)
            save_proto_data(basename + ".bin", m.SerializeToString())
            save_json_data(basename + ".json", to_json(m))
            print to_json(m)

def generate_repeated_field_fixtures(directory):
    for type in fields_all:
        field = "r_" + type
        m = TypesMsg()
        getattr(m, field).extend(test_values[type])
        print to_json(m)

def generate_fixtures(directory):
    generate_single_field_fixtures(directory)
    generate_repeated_field_fixtures(directory)

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
