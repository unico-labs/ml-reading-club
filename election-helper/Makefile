create_venv:
	python3.8 -m venv .venv

install_deps: create_venv
	.venv/bin/pip install pip --upgrade && \
	.venv/bin/pip install -r requirements.txt

create_exec:
	mkdir -p bin && \
	printf "#!/bin/bash\n\n" > bin/helper && \
	printf "$$PWD/.venv/bin/python $$PWD/src/main.py $$" >> bin/helper && \
	printf "@\n" >> bin/helper && \
	chmod a+x bin/helper

build: install_deps create_exec

help: build
	bin/helper --help

all: help
