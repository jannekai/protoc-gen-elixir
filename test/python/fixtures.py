# -*- coding: utf-8 -*-
from __future__ import print_function
import sys, os, base64, json, io
from proto2dict import *
from proto.types_pb2 import TypesMsg, EmptyMsg, ForeignMsg, RecursiveMsg
from google.protobuf import text_format
from google.protobuf.descriptor import FieldDescriptor as FD

#
# Test data
#

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
    "int32":            [ -2**31,   2**31-1,    0, -1, 1 ],
    "sint32":           [ -2**31,   2**31-1,    0, -1, 1 ],
    "uint32":           [ 0,        2**32-1,    1 ],
    "int64":            [ -2**63L,  2**63-1,    0, -1, 1 ],
    "sint64":           [ -2**63L,  2**63-1,    0, -1, 1 ],
    "uint64":           [ 0,        2**64-1,    1 ],
    "bool":             [ True,     False ],
    "nested_enum":      [ 0, 1, 2, -1 ],
    "foreign_enum":     [ 0, 4, 5, -2 ],

    "fixed64":          [ 0,        2**64-1,    1 ],
    "sfixed64":         [ -2**63,   2**63-1,    0, -1, 1 ],
    "double":           [ -1.0,     1.0,        0.0 ],

    "string":           [ "",       "foo",      u"ᚠᛇᚻ᛫ᛒᛦᚦ᛫ᚠᚱᚩᚠᚢᚱ᛫ᚠᛁᚱᚪ᛫ᚷᛖᚻᚹᛦᛚᚳᚢᛗ" ],
    "bytes":            [ str(bytearray([65,66,67,68])), str(bytearray([255,128,64,32,16,8,4,2,1,0])) ],
    "nested_msg":       [ nestedMsgDefault,     nestedMsgOne ],
    "foreign_msg":      [ foreignMsgDefault,    foreignMsgOne ],
    "empty_msg":        [ emptyMsg,             emptyMsg ],

    "fixed32":          [ 0,        2**32-1,    1 ],
    "sfixed32":         [ -2**31,   2**31-1,    0, -1, 1 ],
    "float":            [ -1.0,     1.0,        0.0 ],

    "m_int32_int32":    [ (-2**31,-2**31), (2**31-1,2**31-1), (0,0), (-1,-1), (1,1) ],
    "m_int64_int32":    [ (-2**31,-2**31), (2**31-1,2**31-1), (0,0), (-1,-1), (1,1) ],
}

fields_varint           = [ "int32", "sint32", "uint32", "int64", "sint64", "uint64", "bool", "nested_enum", "foreign_enum" ]
fields_64bit            = [ "fixed64", "sfixed64", "double" ]
fields_length_prefixed  = [ "string", "bytes", "nested_msg", "foreign_msg", "empty_msg" ]
fields_32bit            = [ "fixed32", "sfixed32", "float" ]

fields_single_types     = fields_varint + fields_64bit + fields_length_prefixed + fields_32bit;
fields_repeated_types   = fields_varint + fields_64bit + fields_length_prefixed + fields_32bit;
fields_packed_types     = fields_varint + fields_64bit + fields_32bit
fields_maps             = [ "m_int32_int32", "m_int64_int64", "m_uint32_uint32", "m_uint64_uint64", "m_sint32_sint32", "m_sint64_sint64",
                            "m_fixed32_fixed32", "m_fixed64_fixed64", "m_sfixed32_sfixed32", "m_sfixed64_sfixed64", "m_int32_float", "m_int32_double", "m_bool_bool",
                            "m_string_string", "m_int32_bytes", "m_int32_foreign_enum", "m_int32_foreign_msg" ]

#
# Generate test fixtures
#

def save_proto_fixture_binary(msg, filename):
    with open(filename, 'wb') as f:
        f.write(msg.SerializeToString())

def save_proto_fixture_json(msg, filename):
    with io.open(filename, 'w', encoding='utf-8') as f:
        data = json.dumps(proto_to_dict(msg), ensure_ascii=False)
        f.write(unicode(data))

def save_proto_fixture(msg, basename):
    save_proto_fixture_binary(msg, basename + ".bin")
    save_proto_fixture_json(msg, basename + ".json")

def set_field(msg, field, value):
    if msg.DESCRIPTOR.fields_by_name[field].type == FD.TYPE_MESSAGE:
        getattr(msg, field).CopyFrom(value)
    else:
        setattr(msg, field, value)

def set_repeated_field(msg, field, value):
    getattr(msg, field).extend(value)

def generate_single_field_fixtures(directory):
    for type in fields_single_types:
        field = "f_" + type
        for index, value in enumerate(test_values[type]):
            msg = TypesMsg()
            set_field(msg, field, value)
            save_proto_fixture(msg, directory + "/" + field + "_" + str(index))

def generate_repeated_field_fixtures(directory):
    for type in fields_repeated_types:
        field = "r_" + type
        msg = TypesMsg()
        set_repeated_field(msg, field, test_values[type])
        save_proto_fixture(msg, directory + "/" + field + "_0")

        msg = TypesMsg()
        set_repeated_field(msg, field, [])
        save_proto_fixture(msg, directory + "/" + field + "_1")

    for type in fields_packed_types:
        field = "p_" + type
        msg = TypesMsg()
        set_repeated_field(msg, field, test_values[type])
        save_proto_fixture(msg, directory + "/" + field + "_0")

        msg = TypesMsg()
        set_repeated_field(msg, field, [])
        save_proto_fixture(msg, directory + "/" + field + "_1")

def generate_map_fixtures(directory):
    for field in fields_maps:
        msg = TypesMsg()

def generate_fixtures(directory):
    generate_single_field_fixtures(directory)
    generate_repeated_field_fixtures(directory)
    generate_map_fixtures(directory)


#
# Verify generated fixtures
#

def load_proto_fixture(basename):
    with open(basename + ".bin", "rb") as f:
        decoded = TypesMsg()
        decoded.ParseFromString(f.read())
    with open(basename + ".json", "r") as f:
        expected = dict_to_proto(json.load(f), TypesMsg())
    return (decoded, expected)

def verify_fixture(testname, decoded, expected):
    if decoded.SerializeToString() != expected.SerializeToString():
        err("Test " + testname + " failed")
        err("Decoded msg:  " + text_format.MessageToString(decoded, as_utf8=True, as_one_line=True))
        err("Expected msg: " + text_format.MessageToString(expected, as_utf8=True, as_one_line=True))

def verify_fixtures(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".bin"):
            (basename, ext) = os.path.splitext(filename)
            (decoded, expected) = load_proto_fixture(directory + "/" + basename)
            verify_fixture(basename, decoded, expected)

#
# Error reporting
#

def err(*objs):
    print("Error: ", *objs, file=sys.stderr)

#
# Main
#

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
