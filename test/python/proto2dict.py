from base64 import b64encode
from google.protobuf.descriptor import FieldDescriptor as FD

def proto_to_dict(msg):
    result = {}
    for field, value in msg.ListFields():
        if field.type == FD.TYPE_MESSAGE:
            cast_fun = proto_to_dict
        elif field.type == FD.TYPE_BOOL:
            cast_fun = bool
        elif field.type == FD.TYPE_STRING:
            cast_fun = unicode
        elif field.type == FD.TYPE_BYTES:
            cast_fun = b64encode
        elif field.type == FD.TYPE_DOUBLE or field.type == FD.TYPE_FLOAT or field.type == FD.TYPE_FIXED32 or field.type == FD.TYPE_FIXED64 or field.type == FD.TYPE_SFIXED32 or field.type == FD.TYPE_SFIXED64:
            cast_fun = float
        elif field.type == FD.TYPE_INT64 or field.type == FD.TYPE_UINT64 or field.type == FD.TYPE_SINT64:
            cast_fun = long
        elif field.type == FD.TYPE_INT32 or field.type == FD.TYPE_UINT32 or field.type == FD.TYPE_SINT32 or field.type == FD.TYPE_ENUM:
            cast_fun = int
        else:
            raise Error("Unknow field type %s", field.type)

        result[field.name] = encode_value(field, value, cast_fun)
    return result

def encode_value(field, value, fun):
    if field.label == FD.LABEL_REPEATED:
        encoded_value = []
        for v in value:
            encoded_value.append(fun(v))
    else:
        encoded_value = fun(value)

    return encoded_value
