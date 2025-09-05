"""Tests for pre-commit workflow functionality."""

import pytest

from .conftest import setup_git_repo, setup_precommit_strict


@pytest.mark.venv
def test_bake_defaults_and_run_pre_commit(tmp_path, copier):
    custom_answers = {"package_type": "cli"}
    project = copier.copy(tmp_path, **custom_answers)
    setup_git_repo(project)
    setup_precommit_strict(project)
    project.run("uv sync")

    project.run("uv run pre-commit run --all-files")


@pytest.mark.venv
def test_bake_with_many_and_run_pre_commit(tmp_path, copier):
    custom_answers = {
        "use_jupyter_notebooks": True,
        "strip_jupyter_outputs": True,
        "generate_example_code": True,
        "generate_dockerfile": True,
        "generate_docs": "mkdocs",
        "type_checker": "mypy",
        "type_checker_strictness": "strict",
        "ide": "vscode",
        "package_type": "cli",
    }
    project = copier.copy(tmp_path, **custom_answers)
    setup_git_repo(project)
    setup_precommit_strict(project)
    project.run("uv sync")

    project.run("uv run pre-commit run --all-files")


@pytest.mark.venv
def test_bake_namespaced_package_with_many_and_run_pre_commit(tmp_path, copier):
    custom_answers = {
        "package_name": "company.mypackage",
        "use_jupyter_notebooks": True,
        "strip_jupyter_outputs": True,
        "generate_example_code": True,
        "generate_dockerfile": True,
        "generate_docs": "mkdocs",
        "type_checker": "mypy",
        "type_checker_strictness": "strict",
        "ide": "vscode",
        "package_type": "cli",
    }
    project = copier.copy(tmp_path, **custom_answers)
    setup_git_repo(project)
    setup_precommit_strict(project)
    project.run("uv sync")

    project.run("uv run pre-commit run --all-files")


@pytest.mark.venv
def test_mypy_exclude_respected_in_pre_commit(tmp_path, copier):
    """Test that mypy respects exclude patterns in pyproject.toml.

    Creates a file with type errors and verifies pre-commit passes
    when the file is explicitly excluded in mypy configuration.
    """
    custom_answers = {
        "type_checker": "mypy",
        "type_checker_strictness": "strict",
        "package_name": "mypackage",
    }
    project = copier.copy(tmp_path, **custom_answers)
    setup_git_repo(project)
    src_dir = project.path / "src" / "mypackage"
    src_file_with_error = src_dir / "exclude_me.py"
    src_file_with_error.write_text(
        "def src_function_with_type_error() -> str:\n"
        '    """Add random docstring here to avoid pre-commit error."""\n'
        "    return 999  # Type error: Incompatible return value\n"
    )
    pyproject_path = project.path / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    src_exclude_path = "src/mypackage/exclude_me.py"
    updated_content = pyproject_content.replace(
        'exclude = ["tests/*"]',
        f'exclude = ["tests/*", "{src_exclude_path}"]',
    )
    pyproject_path.write_text(updated_content)
    project.run(f"git add {src_exclude_path} pyproject.toml")
    project.run(
        "git commit -m 'Add file with type errors in src directory and update mypy"
        " excludes'"
    )
    setup_precommit_strict(project)
    project.run("uv sync")

    project.run("uv run pre-commit run --all-files")
