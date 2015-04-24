encode_msg(Msg, MsgDefs) ->
    MsgName = element(1, Msg),
    MsgDef = keyfetch({msg, MsgName}, MsgDefs),
    encode_2(MsgDef, Msg, MsgDefs, <<>>).

encode_2([#?gpb_field{occurrence=Occurrence}=Field | Rest], Msg, MsgDefs, Acc) ->
    EncodedField =
        case {Occurrence, is_packed(Field)} of
            {repeated, true} ->
                *
            _ ->
                encode_field(Field, Msg, MsgDefs)
        end,
    encode_2(Rest, Msg, MsgDefs, <<Acc/binary, EncodedField/binary>>);
encode_2([#gpb_oneof{fields=Fields, rnum=RNum} | Rest], Msg, MsgDefs, Acc) ->
    case element(RNum, Msg) of
        {Name, Value} ->
            Field = lists:keyfind(Name, #?gpb_field.name, Fields),
            NewAcc = encode_2([Field], setelement(RNum, Msg, Value), MsgDefs, Acc),
            encode_2(Rest, Msg, MsgDefs, NewAcc);
        undefined ->
            encode_2(Rest, Msg, MsgDefs, Acc)
    end;
encode_2([], _Msg, _MsgDefs, Acc) ->
    Acc.

encode_packed(#?gpb_field{rnum=RNum, fnum=FNum, type=Type}, Msg, MsgDefs) ->
    case element(RNum, Msg) of
        []    ->
            <<>>;
        Elems ->
            PackedFields = encode_packed_2(Elems, Type, MsgDefs, <<>>),
            <<(encode_fnum_type(FNum, bytes))/binary,
              (encode_varint(byte_size(PackedFields)))/binary,
              PackedFields/binary>>
    end.

encode_packed_2([Elem | Rest], Type, MsgDefs, Acc) ->
    NewAcc = <<Acc/binary, (encode_value(Elem, Type, MsgDefs))/binary>>,
    encode_packed_2(Rest, Type, MsgDefs, NewAcc);
encode_packed_2([], _Type, _MsgDefs, Acc) ->
    Acc.

encode_field(#?gpb_field{rnum=RNum, fnum=FNum, type=Type, occurrence=required}, Msg, MsgDefs) ->
    encode_field_value(element(RNum, Msg), FNum, Type, MsgDefs);
encode_field(#?gpb_field{rnum=RNum, fnum=FNum, type=Type, occurrence=optional}, Msg, MsgDefs) ->
    case element(RNum, Msg) of
        undefined -> <<>>;
        Value     -> encode_field_value(Value, FNum, Type, MsgDefs)
    end;
encode_field(#?gpb_field{rnum=RNum, fnum=FNum, type=Type, occurrence=repeated}, Msg, MsgDefs) ->
    encode_repeated(element(RNum, Msg), FNum, Type, MsgDefs, <<>>).

encode_repeated([Elem | Rest], FNum, Type, MsgDefs, Acc) ->
    EncodedValue = encode_field_value(Elem, FNum, Type, MsgDefs),
    NewAcc = <<Acc/binary, EncodedValue/binary>>,
    encode_repeated(Rest, FNum, Type, MsgDefs, NewAcc);
encode_repeated([], _FNum, _Type, _MsgDefs, Acc) ->
    Acc.

encode_field_value(Value, FNum, Type, MsgDefs) ->
    <<(encode_fnum_type(FNum, Type))/binary, (encode_value(Value, Type, MsgDefs))/binary>>.

encode_fnum_type(FNum, Type) ->
    encode_varint((FNum bsl 3) bor encode_wiretype(Type)).

encode_value(Value, Type, MsgDefs) ->
    case Type of
        sint32 ->
            encode_varint(encode_zigzag(Value));
        sint64 ->
            encode_varint(encode_zigzag(Value));
        int32 ->
            if Value >= 0 ->
                    encode_varint(Value);
               true ->
                    <<N:32/unsigned-native>> = <<Value:32/signed-native>>,
                    encode_varint(N)
            end;
        int64 ->
            if Value >= 0 ->
                    encode_varint(Value);
               true ->
                    <<N:64/unsigned-native>> = <<Value:64/signed-native>>,
                    encode_varint(N)
            end;
        uint32 ->
            encode_varint(Value);
        uint64 ->
            encode_varint(Value);
        bool ->
            if Value     -> encode_varint(1);
               not Value -> encode_varint(0)
            end;
        {enum, _EnumName}=Key ->
            {value, {Key, EnumValues}} = lists:keysearch(Key, 1, MsgDefs),
            {value, {Value, N}} = lists:keysearch(Value, 1, EnumValues),
            encode_value(N, int32, MsgDefs);
        fixed64 ->
            <<Value:64/little>>;
        sfixed64 ->
            <<Value:64/signed-little>>;
        double ->
            <<Value:64/float-little>>;
        string ->
            Utf8 = unicode:characters_to_binary(Value),
            <<(encode_varint(byte_size(Utf8)))/binary, Utf8/binary>>;
        bytes ->
            <<(encode_varint(byte_size(Value)))/binary, Value/binary>>;
        {msg,_MsgName} ->
            SubMsg = encode_msg(Value, MsgDefs),
            <<(encode_varint(byte_size(SubMsg)))/binary, SubMsg/binary>>;
        fixed32 ->
            <<Value:32/little>>;
        sfixed32 ->
            <<Value:32/signed-little>>;
        float ->
            <<Value:32/float-little>>
    end.

encode_wiretype(sint32)            -> 0;
encode_wiretype(sint64)            -> 0;
encode_wiretype(int32)             -> 0;
encode_wiretype(int64)             -> 0;
encode_wiretype(uint32)            -> 0;
encode_wiretype(uint64)            -> 0;
encode_wiretype(bool)              -> 0;
encode_wiretype({enum, _EnumName}) -> 0;
encode_wiretype(fixed64)           -> 1;
encode_wiretype(sfixed64)          -> 1;
encode_wiretype(double)            -> 1;
encode_wiretype(string)            -> 2;
encode_wiretype(bytes)             -> 2;
encode_wiretype({msg,_MsgName})    -> 2;
encode_wiretype(fixed32)           -> 5;
encode_wiretype(sfixed32)          -> 5;
encode_wiretype(float)             -> 5.


encode_varint(N) -> en_vi(N).
en_vi(N) when N =< 127 -> <<N>>;
en_vi(N) when N >= 128 -> <<1:1, (N band 127):7, (en_vi(N bsr 7))/binary>>.

encode_zigzag(N) when N >= 0 -> N * 2;
encode_zigzag(N) when N <  0 -> N * -2 - 1.
