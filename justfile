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
# Note: With --vcs-ref=HEAD (default), copier includes uncommitted changes
# Usage:
#   just test-template              -> uses test answers file (default)
#   just test-template interactive  -> prompts for all values
#   just test-template validate     -> uses test answers file + runs setup/lint/test
#   just test-template REF=main     -> uses test answers file with specific ref
#   just test-template validate main -> validate with specific ref
test-template MODE='test' REF='HEAD':
    #!/usr/bin/env bash
    mkdir -p /tmp/copier-python-uv-test
    tempdir=$(mktemp -p /tmp/copier-python-uv-test -d test_template.XXX)
    echo "Installing from git ref: {{REF}}"
    if [ "{{MODE}}" = "interactive" ]; then
        echo "Running in interactive mode..."
        copier copy --vcs-ref={{REF}} . $tempdir
    else
        if [ -f .copier-answers.test.local.yml ]; then
            echo "Using local test answers file..."
            copier copy --data-file .copier-answers.test.local.yml --vcs-ref={{REF}} . $tempdir
        else
            echo "Using test answers file..."
            copier copy --data-file .copier-answers.test.yml --vcs-ref={{REF}} . $tempdir
        fi
    fi
    echo "Created project in $tempdir"
    if [ "{{MODE}}" = "validate" ]; then
        echo "Validating generated project..."
        cd $tempdir
        unset VIRTUAL_ENV
        git init && git add . && git commit -m "initial commit"
        just setup
        just lint
        just test
        echo "✓ Template validation passed"
    else
        cd $tempdir
        unset VIRTUAL_ENV
        git init && git add . && git commit -m "initial commit"
        echo "To test the project: cd $tempdir && just setup"
    fi
