all: plugin_pb2.py elixir_pb2.py

%_pb2.py: %.proto
	protoc --python_out=. $<

.PHONY: all