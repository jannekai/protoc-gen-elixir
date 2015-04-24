defmodule Exprotoc.Protocol do
  use Bitwise

  @type wire_type :: 0 | 1 | 2 | 5
  @type value :: integer | float | binary

  def encode_message(message) do
    message = message |> List.keysort(1) |> Enum.reverse
    encode_message message, []
  end

  defp encode_message([], acc), do: acc
  defp encode_message([ { field_num, { type, { :repeated, values } } } | rest ], acc) do
    payload = Enum.map values, &encode_value(field_num, type, &1)
    encode_message rest, [ payload | acc ]
  end
  defp encode_message([ { field_num, { type, value } } | rest ], acc) do
    payload = encode_value field_num, type, value
    encode_message rest, [ payload | acc ]
  end

  defp encode_value(_, _, :undefined), do: []
  defp encode_value(field_num, { :enum, enum }, value) do
    varint = enum.to_i value
    [ encode_varint(field_num <<< 3), encode_varint(varint) ]
  end
  defp encode_value(field_num, { :message, module }, message) do
    payload = module.encode message
    size = iolist_size payload
    [ encode_varint((field_num <<< 3) ||| 2), encode_varint(size) , payload ]
  end
  defp encode_value(field_num, type, data) do
    key = (field_num <<< 3) ||| wire_type(type)
    [ key, encode_value(type, data) ]
  end

  defp encode_value(:int32, data) when data < 0 do
    encode_varint(data + (1 <<< 32))
  end
  defp encode_value(:int32, data) do
    encode_varint data
  end
  defp encode_value(:int64, data) when data < 0 do
    encode_varint(data + (1 <<< 64))
  end
  defp encode_value(:int64, data) do
    encode_varint data
  end
  defp encode_value(:uint32, data), do: encode_varint(data)
  defp encode_value(:uint64, data), do: encode_varint(data)
  defp encode_value(:sint32, data) when data <= 0x80000000 when data >= -0x7fffffff do
    int = bxor (data <<< 1), (data >>> 31)
    encode_varint int
  end
  defp encode_value(:sint64, data) when data <= 0x8000000000000000 when data >= -0x7fffffffffffffff do
    int = bxor (data <<< 1), (data >>> 63)
    encode_varint int
  end
  defp encode_value(:bool, true), do: encode_varint(1)
  defp encode_value(:bool, false), do: encode_varint(0)
  defp encode_value(:string, data), do: encode_value(:bytes, data)
  defp encode_value(:bytes, data) do
    len = byte_size data
    [ encode_varint(len), data ]
  end
  defp encode_value(:float, data) do
    << data :: [ size(32), float, little ] >>
  end

  defp encode_varint(data) when data >= 0 do
    data |> encode_varint([]) |> Enum.reverse
  end
  defp encode_varint(true, acc), do: [1|acc]
  defp encode_varint(false, acc), do: [0|acc]
  defp encode_varint(int, acc) when int <= 127, do: [int|acc]
  defp encode_varint(int, acc) do
    next = int >>> 7
    last_seven = int - (next <<< 7)
    acc = [ (1 <<< 7) + last_seven | acc ]
    encode_varint next, acc
  end

  def wire_type(:int32), do: 0
  def wire_type(:int64), do: 0
  def wire_type(:uint32), do: 0
  def wire_type(:uint64), do: 0
  def wire_type(:sint32), do: 0
  def wire_type(:sint64), do: 0
  def wire_type(:bool), do: 0
  def wire_type(:enum), do: 0
  def wire_type(:fixed64), do: 1
  def wire_type(:sfixed64), do: 1
  def wire_type(:double), do: 1
  def wire_type(:string), do: 2
  def wire_type(:bytes), do: 2
  def wire_type(:embedded), do: 2
  def wire_type(:repeated), do: 2
  def wire_type(:fixed32), do: 5
  def wire_type(:sfixed32), do: 5
  def wire_type(:float), do: 5
  def wire_type(_), do: :custom
end
