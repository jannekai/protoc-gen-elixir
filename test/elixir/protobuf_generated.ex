defmodule Test.Types.ForeignEnum do
  def type, do: :enum
  def module, do: Test.Types.ForeignEnum
  
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

defmodule Test.Types.Outer.Inner.InnerEnum do
  def type, do: :enum
  def module, do: Test.Types.Outer.Inner.InnerEnum
  
  def value(:zero), do: 0
  def value(:one), do: 1
  
  def key(0), do: :zero
  def key(1), do: :one
  
  def values, do: [0, 1]
  def keys, do: [:zero, :one]
end

defmodule Test.Types.Outer.OuterEnum do
  def type, do: :enum
  def module, do: Test.Types.Outer.OuterEnum
  
  def value(:zero), do: 0
  def value(:one), do: 1
  
  def key(0), do: :zero
  def key(1), do: :one
  
  def values, do: [0, 1]
  def keys, do: [:zero, :one]
end

defmodule Test.Types.TypesMsg.NestedEnum do
  def type, do: :enum
  def module, do: Test.Types.TypesMsg.NestedEnum
  
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

