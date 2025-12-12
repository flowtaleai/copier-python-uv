# Contributing to Copier Python UV

This document provides guidelines for contributing to the Copier Python UV project. Since this is a template generator, there are two distinct contexts to consider: the template itself and the projects generated from it.

## Template Development

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.7.13
- [Copier](https://copier.readthedocs.io/) (suggested install method: uvx)
- [just](https://github.com/casey/just) (installed via `uv sync` or system package manager)
- [direnv](https://direnv.net/) (recommended for environment management)
- Git

### Development Environment Setup

#### Setting up direnv (recommended)

direnv automatically loads and unloads directory-specific environment variables. To use it:

1. [Install direnv](https://direnv.net/docs/installation.html)
2. At the project root (where `.envrc` is located), run:
   ```bash
   direnv allow
   ```

### Testing the Template

There are multiple approaches for testing the template to ensure it works correctly. A comprehensive testing strategy involves testing both the template itself and the projects it generates.

#### Running Template Tests

To run the automated test suite for the template, you have several options:

```bash
# Run unit tests only (fast feedback for development)
just test

# Run integration tests only (isolated environment using tox)
just test-integration

# Run all tests with unified pytest report
just test-all
```

The template tests are organized into:
- **Unit tests** (`tests/unit/`) - Fast tests for template generation logic and validation
- **Integration tests** (`tests/integration/`) - Tests that run external tools and modify environments

#### Pytest Markers

The test suite uses specific pytest markers to categorize tests by their environmental impact:

- **`@pytest.mark.venv`** - Applied to tests that install project dependencies or modify the virtual environment. These tests require isolated execution via tox to prevent interference with the development environment. Without the `--include-venv` flag, these tests are automatically skipped with a clear explanation.

All integration tests that perform `uv sync`, `pip install`, or similar package management operations should use this marker to ensure proper test isolation and prevent conflicts with the active development environment.

For development, use `just test` for quick feedback. Use `just test-integration` or `just test-all` for comprehensive testing before submitting changes.

#### Generating Test Projects

1. **Using just (Recommended Method)**:
   ```bash
   # Test from HEAD commit (default) - uses test answers file
   just test-template

   # Test interactively (prompts for all values)
   just test-template interactive

   # Test from specific commit/tag/branch with test answers
   just test-template REF=abc1234
   just test-template REF=v1.2.3
   just test-template REF=feature-branch

   # Test from specific ref interactively
   just test-template interactive abc1234
   just test-template interactive main
   ```

   This creates a project in a temporary directory under `testprojects/` using the specified template version.

   > **Note:** The `just test-template` command uses `--vcs-ref=HEAD` by default, which includes uncommitted changes in your working directory (requires Copier 9.4.0+). Use the `interactive` mode when you need to manually verify all prompts or test specific configurations.

#### Verifying Generated Projects

After generating a test project, verify it works correctly:

1. Install dependencies (adjust command based on generated task runner):
   ```bash
   cd /tmp/test-project

   # If justfile was generated (default)
   just setup-strict

   # If Makefile was generated
   make setup-strict
   ```

2. Run tests and linting:
   ```bash
   # With justfile
   just test
   just lint

   # With Makefile
   make test
   make lint
   ```

3. Check other features based on your configuration:
   ```bash
   # For projects with documentation
   just docs        # or: make docs
   just serve-docs  # or: make serve-docs

   # For CLI projects
   uv run your-package-name --help
   ```

#### Using a Default Answers File

The template includes `.copier-answers.test.yml` with fun, cat-themed test values that exercise most template features. You can also create your own answers file for different testing scenarios:

```yaml
# ~/copier-default-answers.yml
author_name: "Test Author"
author_email: "test@example.com"
package_name: "testpackage"
distribution_name: "test-package"
project_name: "Test Project"
repository_name: "test-project"
project_short_description: "A project for testing the template"
version: "0.1.0"
license: "MIT"
package_type: "cli"
python_version: "3.10"
testing_framework: "pytest"
max_line_length: 88
type_checker: "mypy"
type_checker_strictness: "strict"
use_lint_strict_rules: true
ide: "vscode"
git_hosting: "gitlab"
use_jupyter_notebooks: true
generate_example_code: true
strip_jupyter_outputs: true
generate_docs: "mkdocs"
task_runner: just
```

Adjust these values to match your testing preferences.

### Available Commands

The template project uses `just` as the task runner. To see all available commands:

```bash
just
```

Key commands include:

- `just setup`: Set up the development environment
- `just setup-strict`: Set up the development environment with strict pre-commit rules
- `just lint`: Run linting on all project files
- `just test`: Run unit tests
- `just test-integration`: Run integration tests
- `just test-all`: Run all tests
- `just test-template`: Generate a test project in a temporary directory (recommended)
- `just bump`: Bump the project version

**Note**: The template supports both `just` and `make` as task runners. Use `just test-template` for testing the template, and set `task_runner=make` when generating projects from this template if you prefer Make.

### Template Structure

The template follows this structure:

```
copier-python-uv/
├── template/                  # Template files that will be copied
├── tests/                     # Template tests
├── copier.yml                 # Copier configuration
├── justfile                   # Task runner for the outer project
└── ...                        # Other repository files
```

When modifying template files:
- Use Jinja2 syntax for dynamic content: `{{ variable_name }}`
- Use conditional blocks when appropriate: `{% if condition %}...{% endif %}`
- Test thoroughly after changes

### Template File Naming Convention

Template files follow these naming conventions:

- **Static files** (copied as-is): Use standard extensions (e.g., `.py`, `.md`, `.toml`)
- **Template files** (containing Jinja2 logic): Add `.jinja` suffix (e.g., `pyproject.toml.jinja`, `__init__.py.jinja`)
- **Conditional files**: Use Jinja2 in filename (e.g., `{% if task_runner == "just" %}justfile{% endif %}.jinja`)

When creating or modifying template files:

1. If a file contains any Jinja2 templating syntax (`{{ }}`, `{% %}`, etc.), use the `.jinja` suffix
2. The `.jinja` suffix is automatically removed during project generation
3. Use conditional filenames when a file should only be generated under certain conditions

### Task Runner Choice (justfile vs Makefile)

The template supports both `just` and `make` as task runners:

- **justfile** (default, `task_runner=just`):
  - Modern, user-friendly syntax
  - Built-in command listing with `just`
  - Better error messages and cross-platform support
  - Requires `rust-just` dependency

- **Makefile** (`task_runner=make`):
  - Traditional, ubiquitous tool
  - Pre-installed on most systems (Needs to be installed on Windows)
  - No additional dependencies

`just` is a superior choice if all is needed is a command runner, for building large projects it is better to chose the tool which was created for this - `make`.

### Recursive Template Structure

Importantly, the outer project itself is based on its own template. This creates a recursive structure:

1. The `template/` directory contains files that will be copied to generated projects
2. The outer project structure mirrors what a generated project would look like

After tagging a new version, we run `copier update` on the outer project to apply the template changes to itself. This means:

- **New features should primarily be implemented in the inner `template/` directory**
- These changes will be automatically applied (except for merge conflicts) the next time the outer project template is updated
- Some changes might specifically target only the outer template (e.g., updates to the outer README.md and CONTRIBUTING.md, or other infrastructure changes that don't get copied to generated projects)

This recursive approach ensures that the template itself follows the best practices it promotes for generated projects.

## Contribution Guidelines

Before contributing to this project, please review the following internal resources:

- **Copier Guidelines** - Internal Google Drive document with detailed guidelines for running the project
- **GitLab Organization** - Internal Google Drive document with information on our GitLab workflow and organization

### Pull Request Management

Please follow the Pull Request Management Best Practices outlined in our internal GitLab Organization document, with one project-specific modification:

**Review order**: First request review from another sprint team member, then notify the product owner for final review after initial approval.

### Code Style

- Follow the style conventions evident in the existing template files
- Use consistent indentation and formatting
- Document any non-obvious template variables or logic
- Docstrings convention is `google` without types (types are specified using standard python typing)
- Use `pathlib.Path` instead of `str` for file names
- Use `pathlib.Path` to process files instead of `os`

### Python Dependencies

- Do not manually change the dependency specifications in template files without testing
- When updating dependencies in the template, ensure they are compatible across supported Python versions
- Consider the impact on generated projects when updating dependencies

#### Dependency Version Management

The template's dependencies in `template/pyproject.toml` need to be periodically updated to maintain security and incorporate new features. However, these updates require careful consideration:

- Each version update must be taken seriously as it affects all projects generated from the template
- Major version updates of formatters (like black) or linters may require reformatting entire codebases
- Test updates thoroughly across different Python versions and configurations
- Document any breaking changes or required manual steps in the release notes
- Consider creating a major template version when introducing potentially disruptive dependency updates

For example:
- Updating the formatter major version might require reformatting all code in existing projects
- Updating linter plugins might introduce new rules that existing projects need to address
- Updating type checkers might enforce stricter rules requiring code modifications

### Versioning

This project follows [Semantic Versioning](https://semver.org/).

- **MAJOR**: Breaking changes to the template structure or generated projects
  - Example: Updating to a new major version of Black that reformats code differently
  - Example: Adding required linters that may cause failures in existing projects

- **MINOR**: New features or enhancements that are backward compatible
  - Example: Adding support for new documentation generators
  - Example: New optional template features (like `task_runner` option)

- **PATCH**: Bug fixes that don't affect compatibility
  - Example: Fixing template syntax errors
  - Example: Correcting documentation

To bump the project version:

```bash
# Interactive prompt
just bump

# Or specify version part directly
just bump patch
just bump minor
just bump major
```

### VSCode

- Add new extensions and settings in `template/.vscode/{extensions.json,settings.json}` not in devcontainer
  - In this way they are available both in the devcontainer and in a vscode instance not run using devcontainer
- Ensure that the tools used by the extensions are loaded from the environment (e.g. black, ruff) and avoid using the bundled versions
  - In this way we ensure that the same version of the tool is used in all the places (e.g. vscode, just/make, and pre-commit)

### pre-commit

- For tools that are run in multiple places, not just pre-commit (e.g. black, ruff) use `language: system` instead of pulling a pre-commit repo, and add the dependency in `pyproject.toml`
  - In this way we ensure that the same version of the tool is used in all the places (e.g. vscode, just/make, and pre-commit)

## Template Rationale Documentation

When making significant changes or adding new features to the template, add an entry to the [Rationale](README.md#rationale) section of the README with:

1. Date in [YYYY-MM-DD] format
2. Clear explanation of the change and why it was made
3. Examples if applicable

This helps future contributors understand the reasoning behind design decisions.

## Release Process

1. Bump the version using `just bump` and select the appropriate version part (or use `just bump [patch|minor|major]`)
2. Push the changes and new tag to the repository
3. Create a release on GitHub/GitLab with release notes
4. Run `copier update` on the outer project to apply template changes to itself
5. Resolve any merge conflicts that arise from the update
6. Commit the applied changes with a message describing the update

Thank you for contributing to Copier Python UV!
