# Default recipe to display help
_default:
    @just --list

# Bump the project version and create a tag
bump VERSION_PART:
    uv run bump-my-version bump {{VERSION_PART}}

# Setup the development environment
setup:
    uv sync
    cp .pre-commit-config.standard.yaml .pre-commit-config.yaml
    uv run pre-commit install

# Setup the development environment with strict pre-commit rules
setup-strict: setup
    @echo "Appending strict pre-commit rules..."
    cat .pre-commit-config.addon.strict.yaml >> .pre-commit-config.yaml

# Runs linting on all project files
lint:
    #!/usr/bin/env bash
    tempfile=$(mktemp)
    trap 'rm -f $tempfile' EXIT
    cat .pre-commit-config.standard.yaml .pre-commit-config.addon.strict.yaml > $tempfile
    uv run pre-commit run --all-files -c $tempfile

# Shorthand for running unit tests
test: test-unit

# Run unit tests only
test-unit:
    uv run pytest tests/unit/

# Run integration tests only
test-integration:
    uv run tox -re integration

# Run all tests
test-all:
    uv run tox -re all

# Test the copier template by creating a new project in temporary directory
testproject:
    #!/usr/bin/env bash
    mkdir -p testprojects
    tempdir=$(mktemp -p testprojects -d testproject.XXX)
    copier copy --vcs-ref=HEAD . $tempdir
    echo "Created project in $tempdir"
