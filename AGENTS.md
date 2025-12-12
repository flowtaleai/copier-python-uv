# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Copier template for generating opinionated Python projects using uv as the package manager. The template itself is recursively based on its own output - changes should primarily go in `template/` directory.

## Commands

```bash
# Setup
just setup                    # Install deps + standard pre-commit
just setup-strict             # Setup + strict linting rules

# Testing
just test                     # Run unit tests (tests/unit/)
just test-integration         # Run integration tests via tox
just test-all                 # Run all tests via tox

# Run single test
uv run pytest tests/unit/test_file.py::test_name -q --tb=short

# Linting
just lint                     # Run all pre-commit checks

# Template testing
just test-template            # Generate test project in /tmp/
just test-template validate   # Generate + setup + lint + test
just test-template interactive # Manual prompts for all values

# Version bump
just bump patch|minor|major
```

## Architecture

### Directory Structure
- `template/` - Jinja2 template files copied to generated projects
- `copier.yml` - Template configuration and user prompts
- `tests/unit/` - Fast tests for template generation
- `tests/integration/` - Tests requiring tox isolation (marked `@pytest.mark.venv`)

### Template Files
- Static files: standard extensions (`.py`, `.md`)
- Template files with Jinja2: `.jinja` suffix (removed during generation)
- Conditional files: Jinja2 in filename (e.g., `{% if condition %}file{% endif %}.jinja`)

### Test Fixtures
Uses pytest-copier plugin. Key fixtures in `tests/conftest.py`:
- `copier_template_paths` - paths to template source
- `copier_defaults` - default answers for template generation

### Recursive Structure
The outer project is generated from its own template. After tagging a version, run `copier update` on the outer project to apply template changes to itself.

## Testing Notes

- Tests marked `@pytest.mark.venv` are skipped by default (modify venv)
- Use `--include-venv` flag to force run them, or use tox
- Integration tests should use the `venv` marker when they install packages
