ROOT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_DIR := $(strip $(ROOT_DIR))

export PYTHONPATH := $(ROOT_DIR)/../src:$(PYTHONPATH)

.PHONY: all

all:
	uv run python src/writeTxt.py input output

%:
	uv run python src/writeTxt.py input/$@.pdf output/$@.pdf.doc.json
