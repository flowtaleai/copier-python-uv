import shutil

import pytest


@pytest.mark.venv
def test_bake_and_run_tests_with_pytest_framework(tmp_path, copier):
    custom_answers = {"testing_framework": "pytest"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("pytest")


@pytest.mark.slow
@pytest.mark.venv
def test_bake_and_run_cli(tmp_path, copier):
    custom_answers = {"package_type": "cli"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("uv sync")
    project.run("uv run python_boilerplate")


@pytest.mark.slow
@pytest.mark.venv
def test_bake_defaults_and_run_pre_commit(tmp_path, copier):
    custom_answers = {"package_type": "cli"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")

    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    shutil.copy(std_pre_commit_path, dst_pre_commit_path)
    with dst_pre_commit_path.open("a") as f:
        f.write(strict_pre_commit_path.read_text())

    project.run("uv sync")
    project.run("uv run pre-commit run --all-files")


@pytest.mark.slow
@pytest.mark.venv
def test_bump_version_updates_files(tmp_path, copier):
    custom_answers = {"package_name": "mypackage"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")
    project.run("uv run bump-my-version bump major")

    copier_answers_path = project.path / ".copier-answers.yml"
    pyproject_path = project.path / "pyproject.toml"
    project_init = project.path / "src" / "mypackage" / "__init__.py"

    assert "1.0.0" in copier_answers_path.read_text()
    assert "1.0.0" in pyproject_path.read_text()
    assert "1.0.0" in project_init.read_text()


@pytest.mark.parametrize(
    ("framework", "frontpage_path"),
    [
        ("pdoc", "build/site/python_boilerplate.html"),
        ("mkdocs", "build/site/index.html"),
    ],
)
@pytest.mark.venv
def test_bake_with_documentation(tmp_path, copier, framework, frontpage_path):
    custom_answers = {"generate_docs": framework}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("git init")
    project.run("make setup")
    project.run("make docs")

    # Check that index.html exists
    frontpage_path = project.path / frontpage_path
    assert frontpage_path.exists()

    # Check that readme is displayed on frontpage
    title = project.answers["package_name"] or project.answers["distribution_name"]
    with open(frontpage_path) as index:
        front_page = "\n".join(index.readlines())
    assert title in front_page
    assert "Usage" in front_page


@pytest.mark.slow
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

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")

    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    shutil.copy(std_pre_commit_path, dst_pre_commit_path)
    with dst_pre_commit_path.open("a") as f:
        f.write(strict_pre_commit_path.read_text())

    project.run("uv sync")
    project.run("uv run pre-commit run --all-files")


@pytest.mark.slow
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

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")

    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    shutil.copy(std_pre_commit_path, dst_pre_commit_path)
    with dst_pre_commit_path.open("a") as f:
        f.write(strict_pre_commit_path.read_text())

    project.run("uv sync")
    project.run("uv run pre-commit run --all-files")


@pytest.mark.slow
@pytest.mark.venv
def test_mypy_exclude_respected_in_pre_commit(tmp_path, copier):
    """Test that mypy respects exclude patterns in pyproject.toml.

    Creates a file with type errors and verifies pre-commit passes
    when the file is explicitly excluded in mypy configuration.
    """
    custom_answers = {
        "type_checker": "mypy",
        "type_checker_strictness": "strict",
        "package_name": "mypackage",  # Specify a fixed package name
    }

    project = copier.copy(tmp_path, **custom_answers)

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")

    # Create a file with type errors in src directory
    src_dir = project.path / "src" / "mypackage"
    src_file_with_error = src_dir / "exclude_me.py"
    src_file_with_error.write_text(
        "def src_function_with_type_error() -> str:\n"
        '    """Add random docstring here to avoid pre-commit error."""\n'
        "    return 999  # Type error: Incompatible return value\n"
    )

    # Modify pyproject.toml to exclude the specific file
    pyproject_path = project.path / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    src_exclude_path = "src/mypackage/exclude_me.py"
    updated_content = pyproject_content.replace(
        'exclude = ["tests/*"]',
        f'exclude = ["tests/*", "{src_exclude_path}"]',
    )
    pyproject_path.write_text(updated_content)

    # Stage and commit the new file and changes
    project.run(f"git add {src_exclude_path} pyproject.toml")
    project.run(
        "git commit -m 'Add file with type errors in src directory and update mypy"
        " excludes'"
    )

    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    shutil.copy(std_pre_commit_path, dst_pre_commit_path)
    with dst_pre_commit_path.open("a") as f:
        f.write(strict_pre_commit_path.read_text())

    project.run("uv sync")
    project.run("uv run pre-commit run --all-files")


@pytest.mark.venv
def test_mypy_with_mkdocs(tmp_path, copier):
    custom_answers = {
        "generate_docs": "mkdocs",
        "type_checker": "mypy",
    }
    project = copier.copy(tmp_path, **custom_answers)

    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")

    project.run("make setup-strict")
    project.run("make lint")
