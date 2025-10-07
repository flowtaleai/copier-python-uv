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
# Usage:
#   just test-template              -> uses test answers file (default)
#   just test-template interactive  -> prompts for all values
#   just test-template HEAD         -> uses test answers file with specific ref
#   just test-template interactive main -> interactive with specific ref
test-template MODE='test' REF='HEAD':
    #!/usr/bin/env bash
    mkdir -p test_templates
    tempdir=$(mktemp -p test_templates -d test_template.XXX)
    echo "Installing from git ref: {{REF}}"
    if [ "{{MODE}}" = "interactive" ]; then
        echo "Running in interactive mode..."
        copier copy --vcs-ref={{REF}} . $tempdir
    else
        echo "Using test answers file..."
        copier copy --data-file .copier-answers.test.yml --vcs-ref={{REF}} . $tempdir
    fi
    echo "Created project in $tempdir"
    echo "To test the project: cd $tempdir && just setup"

# Test the copier template using current local version (uncommitted changes)
# Usage:
#   just test-template-local              -> uses test answers file (default)
#   just test-template-local interactive  -> prompts for all values
test-template-local MODE='test':
    #!/usr/bin/env bash
    mkdir -p test_templates
    tempdir=$(mktemp -p test_templates -d test_template.XXX)
    echo "Installing current local version..."
    if [ "{{MODE}}" = "interactive" ]; then
        echo "Running in interactive mode..."
        copier copy . $tempdir
    else
        echo "Using test answers file..."
        copier copy --data-file .copier-answers.test.yml . $tempdir
    fi
    echo "Created project in $tempdir"
    echo "To test the project: cd $tempdir && just setup"
