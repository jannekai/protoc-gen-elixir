defmodule Test.Msg.Foreignenum do
  def type, do: :enum
  def module, do: Test.Msg.Foreignenum
  
  def value(:foreign_zero), do: 0
  def value(:foreign_four), do: 4
  def value(:foreign_five), do: 5
  def value(:foreign_neg), do: -2
  
  def key(0), do: :foreign_zero
  def key(4), do: :foreign_four
  def key(5), do: :foreign_five
  def key(-2), do: :foreign_neg
  
  def values, do: [0, 4, 5, -2]
  def keys, do: [:foreign_zero, :foreign_four, :foreign_five, :foreign_neg]
end

defmodule Test.Msg.Outer.Inner.Innerenum do
  def type, do: :enum
  def module, do: Test.Msg.Outer.Inner.Innerenum
  
  def value(:zero), do: 0
  def value(:one), do: 1
  
  def key(0), do: :zero
  def key(1), do: :one
  
  def values, do: [0, 1]
  def keys, do: [:zero, :one]
end

defmodule Test.Msg.Outer.Outerenum do
  def type, do: :enum
  def module, do: Test.Msg.Outer.Outerenum
  
  def value(:zero), do: 0
  def value(:one), do: 1
  
  def key(0), do: :zero
  def key(1), do: :one
  
  def values, do: [0, 1]
  def keys, do: [:zero, :one]
end

defmodule Test.Msg.TypesMsg.Nestedenum do
  def type, do: :enum
  def module, do: Test.Msg.TypesMsg.Nestedenum
  
  def value(:zero), do: 0
  def value(:one), do: 1
  def value(:two), do: 2
  def value(:neg), do: -1
  
  def key(0), do: :zero
  def key(1), do: :one
  def key(2), do: :two
  def key(-1), do: :neg
  
  def values, do: [0, 1, 2, -1]
  def keys, do: [:zero, :one, :two, :neg]
end

