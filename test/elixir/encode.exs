# [
#   {17, :map_string_msg,         :map,       {{:string,  nil},   {:message,  Proto.MsgEnumWrapper}},},
#   {16, :map_string_enum,        :map,       {{:string,  nil},   {:enum,     Proto.MsgEnumWrapper.Enum}}},
#   {15, :map_int32_int32,        :map,       {{:int32,   nil},   {:int32,    nil}}},

#   {14, :repeated_wrapped_enum,  :repeated,  {:enum,             Proto.MsgEnumWrapper.Enum}},
#   {13, :optional_wrapped_enum,  :optional,  {:enum,             Proto.MsgEnumWrapper.Enum}},

#   {12, :repeated_nested_enum,   :repeated,  {:enum,             Proto.Msg.NestedEnum}},
#   {11, :optional_nested_enum,   :optional,  {:enum,             Proto.Msg.NestedEnum}},

#   {10, :repeated_enum,          :repeated,  {:enum,             Proto.Enum}},
#   {9, :optional_enum,           :optional,  {:enum,             Proto.Enum}},

#   {8, :repeated_nested_msg,     :repeated,  {:message,          Proto.Msg.NestedMsg}},
#   {7, :optional_nested_msg,     :optional,  {:message,          Proto.Msg.NestedMsg}},

#   {6, :repeated_external_msg,   :repeated,  {:message,          Proto.ExternalMsg}},
#   {5, :optional_external_msg,   :optional,  {:message,          Proto.ExternalMsg}},

#   {4, :repeated_string,         :repeated,  {:string,           nil}},
#   {3, :optional_string,         :optional,  {:string,           nil}},

#   {2, :repeated_int32,          :repeated,  {:int32,            nil}},
#   {1, :optional_int32,          :optional,  {:int32,            nil}},
# ]

defmodule Protobuf do
  use Bitwise

  @min_int32  -0x8000_0000
  @max_int32   0x7FFF_FFFF
  @min_sint32 -0x8000_0000
  @max_sint32  0x7FFF_FFFF
  @min_uint32  0x0
  @max_uint32  0xFFFF_FFFF
  @min_int64  -0x8000_0000_0000_0000
  @max_int64   0x7FFF_FFFF_FFFF_FFFF
  @min_uint64  0x0
  @max_uint64  0xFFFF_FFFF_FFFF_FFFF

  @packed_types [:int32, :int64, :uint32, :uint64, :sint32, :sint64, :bool, :enum, :fixed64, :sfixed64, :double, :fixed32, :sfixed32, :float]

  def encode(msg, fields) when is_list(fields) do
    encode_field fields, msg, []
  end

  defp encode_field([], msg, acc), do: acc
  defp encode_field([{tag, key, :map, {{key_type, nil}, {value_type, value_module}}} | rest], msg, acc) do
    value = Map.fetch! msg, key
    acc = case map_size value do
      0 -> acc
      _ -> [encode_field_map(tag, key, key_type, value_type, value_module, msg) | acc]
    end
    encode_field rest, msg, acc
  end
  defp encode_field([{tag, key, :repeated, {type, module}} | rest], msg, acc) do
    acc = case Map.fetch!(msg, key) do
      []      -> acc
      values  -> [encode_field_repeated(values, tag, key, type, module, msg) | acc]
    end
    encode_field rest, msg, acc

    # Pack all repeated fields assuming packed=true is set
    data = Map.fetch!(msg, field) |> Enum.map(fn(value) -> encode_value(value, type, module) end)
    value = [encode_varint(byte_size(data), data]
    encode_field rest, msg, encode_field_value(tag, :packed, value, acc)
  end
  defp encode_field([{tag, field, :optional, {type, module}, options} | fields], msg, acc) do
    value = Map.fetch!(msg, field)
    acc = case is_default value do
      true -> acc
      false ->
        value =
    end
     |> encode_value(type, module)
    encode_field rest, msg, encode_field_value(tag, type, value, acc)
  end

  # Maps
  def encode_field_map(tag, key, key_type, value_type, value_module, msg) do

  end

  def encode_field_repeated(values, tag, key, type, module, msg) when type in @packed_types do
    values = Enum.map values, fn value -> encode_value(value, type, module) end
  end
  def encode_field_repeated(values, tag, key, type, module, msg) do
    Enum.map values, fn value ->
      encode_field_value()
    end
  end

  # Encode field with tag, wire type and value, skip if default value for a type
  def encode_field_header(tag, type, value) do
    [<<(tag <<< 3) ||| wire_type(type)>>, value]
  end

  # Wire type 1
  def encode_value(v, :int32, nil) when v >= 0 when v <= @max_int32, do: encode_varint(v)
  def encode_value(v, :int32, nil) when v >= @min_int32 do
    <<u :: unsigned-integer-32>> = <<v :: signed-integer-32>>
    encode_varint u
  end
  def encode_value(v, :int64, nil) when v >= 0 when v <= @max_int64, do: encode_varint(v)
  def encode_value(v, :int64, nil) do
    <<u :: unsigned-integer-64>> = <<v :: signed-integer-64>>
    encode_varint u
  end
  def encode_value(v, :sint32, nil) when v >= @min_int32 when v <= @max_int32, do: encode_varint(encode_zigzag(v))
  def encode_value(v, :sint64, nil) when v >= @min_int64 when v <= @max_int64, do: encode_varint(encode_zigzag(v))
  def encode_value(v, :uint32, nil) when v <= @max_uint32, do: encode_varint(v)
  def encode_value(v, :uint64, nil) when v <= @max_uint64, do: encode_varint(v)
  def encode_value(v, :bool, nil) when v, do: encode_varint(1)
  def encode_value(v, :bool, nil), do: encode_varint(0)
  def encode_value(v, :enum, module), do: encode_varint(module.value(v))

  # Wire type 1
  def encode_value(v, :fixed64, nil), do: <<v :: little-64>>
  def encode_value(v, :sfixed64, nil), do: <<v :: signed-little-64>>
  def encode_value(v, :double, nil), do: <<v :: float-little-64>>

  # Wire type 2
  def encode_value(v, :message, module) do
    data = Protobuf.encode(v, module.fields)
    [encode_varint(byte_size(data), data]
  end
  def encode_value(v, :string, nil), do: [encode_varint(byte_size(v)), v]
  def encode_value(v, :bytes, nil), do: [encode_varint(byte_size(v)), v]
  def encode_value(v, :embedded, nil), do: [encode_varint(byte_size(v)), v]

  # Wire type 3
  def encode_value(v, :fixed32, nil) when v >= @min_int32 when v <= @max_int32, do: <<v :: little-32>>
  def encode_value(v, :sfixed32, nil) when v >= @min_int32 when v <= @max_int32, do: <<v :: signed-little-32>>
  def encode_value(v, :float, nil), do: <<v :: float-little-32>>

  # Varint, msb of each byte means that next byte belongs to this value, rest 7 bits are part of value
  def encode_varint(v) when v <= 127 when v >= 0, do: <<v>>
  def encode_varint(v) when v >= 128, do: <<1 :: 1, (v &&& 127) :: 7, encode_varint(v >>> 7) :: binary>>

  def decode_varint(b), do: decode_varint(b, 0, 0)
  def decode_varint(<<1 :: 1, v :: 7, rest :: binary>>, n, acc), do: decode_varint(rest, n + 7, acc + (v <<< n))
  def decode_varint(<<0 :: 1, v :: 7, rest :: binary>>, n, acc), do: {(v <<< n) + acc, rest}

  # ZigZag encoding is used for signed int types, makes negative values encode in smaller space in varint
  def encode_zigzag(v) when v >= 0, do: v * 2
  def encode_zigzag(v), do: v * -2 - 1

  def decode_zigzag(v) when v &&& 1 == 0, do: v >>> 1
  def decode_zigzag(v), do: (-(v+1)) >>> 1

  # Wire types
  def wire_type(:int32),    do: 0
  def wire_type(:int64),    do: 0
  def wire_type(:sint32),   do: 0
  def wire_type(:sint64),   do: 0
  def wire_type(:uint32),   do: 0
  def wire_type(:uint64),   do: 0
  def wire_type(:bool),     do: 0
  def wire_type(:enum),     do: 0

  def wire_type(:fixed64),  do: 1
  def wire_type(:sfixed64), do: 1
  def wire_type(:double),   do: 1

  def wire_type(:message),  do: 2
  def wire_type(:string),   do: 2
  def wire_type(:bytes),    do: 2
  def wire_type(:embedded), do: 2
  def wire_type(:packed),   do: 2

  def wire_type(:fixed32),  do: 5
  def wire_type(:sfixed32), do: 5
  def wire_type(:float),    do: 5
end
