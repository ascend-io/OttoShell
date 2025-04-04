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

# setup
setup:
    @uv venv --python=3.13 --allow-existing
    just sync

# sync
sync:
    @uv sync --all-extras --upgrade

# build
build:
    @rm -r dist || true
    @uv build

# format
format:
    @ruff format .

# publish-test
release-test:
    just build
    @uv publish --publish-url https://test.pypi.org/legacy/ --token ${PYPI_TEST_TOKEN}

# publish
release:
    just build
    @uv publish --token ${PYPI_TOKEN}

# open
open:
    @open https://pypi.org/project/otto-shell
