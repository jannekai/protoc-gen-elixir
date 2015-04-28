import json
from google.protobuf.descriptor import FieldDescriptor as FD

def to_json(msg):
    js = {}
    for field, value in msg.ListFields():
        if field.type == FD.TYPE_MESSAGE:
            cast_fun = to_json
        elif field.type == FD.TYPE_BOOL:
            cast_fun = bool
        elif field.type == FD.TYPE_STRING:
            cast_fun = unicode
        elif field.type == FD.TYPE_BYTES:
            cast_fun = lambda x: x.encode('string_escape')
        elif field.type == FD.TYPE_DOUBLE or field.type == FD.TYPE_FLOAT or field.type == FD.TYPE_FIXED32 or field.type == FD.TYPE_FIXED64 or field.type == FD.TYPE_SFIXED32 or field.type == FD.TYPE_SFIXED64:
            cast_fun = float
        elif field.type == FD.TYPE_INT64 or field.type == FD.TYPE_UINT64 or field.type == FD.TYPE_SINT64:
            cast_fun = long
        elif field.type == FD.TYPE_INT32 or field.type == FD.TYPE_UINT32 or field.type == FD.TYPE_SINT32 or field.type == FD.TYPE_ENUM:
            cast_fun = int
        else:
            raise Error("Unknow field type %s", field.type)

        if field.label == FD.LABEL_REPEATED:
            js_value = []
            for v in value:
                js_value.append(cast_fun(v))
        else:
            js_value = cast_fun(value)

        js[field.name] = js_value

    return json.dumps(js)
