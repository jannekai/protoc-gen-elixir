
PROTO_FILES := $(wildcard proto/*.proto)
PYTHON_FILES := $(patsubst proto/%.proto, python/%_pb2.py, $(PROTO_FILES))

all: $(PYTHON_FILES) fixtures

clean:
	@rm fixtures/*

python/%_pb2.py: proto/%.proto
	@mkdir -p $(@D)
	@protoc --proto_path=proto --python_out=python/proto $<

fixtures:
	@python python/generate_fixtures.py --dir fixtures generate

verify:
	@python python/generate_fixtures.py --dir fixtures verify

#generate-elixir:
#protoc --proto_path=data --plugin=protoc-gen-elixir=../plugin/protoc-gen-elixir --elixir_out=elixir data/proto3.proto

.PHONY: clean fixtures
