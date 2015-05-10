
PROTO_FILES := $(wildcard proto/*.proto)
PYTHON_FILES := $(patsubst proto/%.proto, python/%_pb2.py, $(PROTO_FILES))

all: $(PYTHON_FILES) fixtures

clean:
	@rm fixtures/*

python/%_pb2.py: proto/%.proto
	@mkdir -p $(@D)
	@protoc --proto_path=proto --python_out=python/proto $<

fixtures:
	@python python/fixtures.py --dir fixtures generate

verify:
	@python python/fixtures.py --dir fixtures verify

elixir:
	protoc --proto_path=proto --plugin=protoc-gen-elixir=../plugin/protoc-gen-elixir --elixir_out=elixir proto/types.proto proto/another.proto

.PHONY: clean fixtures elixir
