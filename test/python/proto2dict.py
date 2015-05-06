# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from google.protobuf.descriptor import FieldDescriptor as FD

def proto_to_dict(msg):
    result = {}
    for fd, value in msg.ListFields():
        result[fd.name] = encode_value(fd, value, encode_func(fd))
    return result

def encode_func(fd):
    if fd.type == FD.TYPE_MESSAGE:
        func = proto_to_dict
    elif fd.type == FD.TYPE_BOOL:
        func = bool
    elif fd.type == FD.TYPE_STRING:
        func = unicode
    elif fd.type == FD.TYPE_BYTES:
        func = b64encode
    elif fd.type == FD.TYPE_DOUBLE or fd.type == FD.TYPE_FLOAT:
        func = float
    elif fd.type == FD.TYPE_INT32 or fd.type == FD.TYPE_UINT32 or fd.type == FD.TYPE_SINT32 or fd.type == FD.TYPE_ENUM:
        func = int
    elif fd.type == FD.TYPE_INT64 or fd.type == FD.TYPE_UINT64 or fd.type == FD.TYPE_SINT64 or fd.type == FD.TYPE_FIXED32 or fd.type == FD.TYPE_FIXED64 or fd.type == FD.TYPE_SFIXED32 or fd.type == FD.TYPE_SFIXED64:
        func = long
    else:
        raise Error("Unknown field type %s", fd.type)
    return func

def encode_value(fd, value, encode_func):
    if fd.label == FD.LABEL_REPEATED:
        encoded_value = []
        for v in value:
            encoded_value.append(encode_func(v))
    else:
        encoded_value = encode_func(value)

    return encoded_value


def dict_to_proto(dictionary, msg):
    decode_msg(dictionary, msg)
    return msg

def decode_msg(dictionary, msg):
    msg.SetInParent()
    for key, value in dictionary.iteritems():
        if value is None:
            continue

        field = str(key)
        if isinstance(value, dict):
            decode_msg(value, getattr(msg, field))
        elif isinstance(value, list):
            decode_list(value, getattr(msg, field), msg.DESCRIPTOR.fields_by_name[field])
        else:
            setattr(msg, field, decode_value(value, msg.DESCRIPTOR.fields_by_name[field]))

def decode_list(values, field, fd):
    if isinstance(values[0], dict):
        for v in values:
            dict_to_proto(v, field.add())
    else:
        for v in values:
            field.append(decode_value(v, fd))

def decode_value(value, fd):
    if fd.type == FD.TYPE_BYTES:
        return b64decode(value)
    if fd.type == FD.TYPE_BOOL:
        return bool(value)
    if fd.type == FD.TYPE_INT32 or fd.type == FD.TYPE_UINT32 or fd.type == FD.TYPE_SINT32 or fd.type == FD.TYPE_ENUM:
        return int(value)
    if fd.type == FD.TYPE_INT64 or fd.type == FD.TYPE_UINT64 or fd.type == FD.TYPE_SINT64 or fd.type == FD.TYPE_FIXED32 or fd.type == FD.TYPE_FIXED64 or fd.type == FD.TYPE_SFIXED32 or fd.type == FD.TYPE_SFIXED64:
        return long(value)

    return value
