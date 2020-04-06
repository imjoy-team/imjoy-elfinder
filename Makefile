.PHONY: help all clean clean-build clean-pyc coverage test

help:
	@echo "clean - run both clean-build and clean-pyc"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "test - run tests quickly with the default Python"

all: test

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

coverage:
	pytest --cov-report term-missing --cov=imjoy_elfinder tests/

test:
	pytest tests/
