# ProseGuard Makefile — cross-platform where it matters (each target is plain
# Python, so the commands also run verbatim on Windows PowerShell/cmd).

.PHONY: help install test lint build clean demo fix

help:
	@echo "make install   Install in editable mode (pip install -e .)"
	@echo "make test      Run the full unittest suite (no third-party deps)"
	@echo "make lint      Byte-compile every module as a syntax check"
	@echo "make build     Build sdist/wheel into dist/"
	@echo "make demo      Lint the bundled example document"
	@echo "make fix       Auto-fix the bundled example document in place"

install:
	python -m pip install -e .

test:
	PYTHONPATH=src python -m unittest discover -s tests -v

lint:
	PYTHONPATH=src python -m compileall -q src tests

build:
	python -m pip install --quiet build && python -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

demo:
	PYTHONPATH=src python -m proseguard --stats examples/bad_writing.md

fix:
	PYTHONPATH=src python -m proseguard --fix examples/bad_writing.md
