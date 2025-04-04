# justfile

# load environment variables
set dotenv-load

# variables

# aliases
alias fmt:=format
alias install:=sync

# list justfile recipes
default:
    just --list

# python things
setup:
    @uv venv --python=3.13 --allow-existing
    just sync

sync:
    @uv sync --all-extras --upgrade

build-python:
    @rm -r dist || true
    @uv build

format:
    @ruff format .

# publish-test
release-test:
    just build-python
    @uv publish --publish-url https://test.pypi.org/legacy/ --token ${PYPI_TEST_TOKEN}

# publish
release:
    just build-python
    @uv publish --token ${PYPI_TOKEN}

# open
open:
    @open https://pypi.org/project/otto-shell
