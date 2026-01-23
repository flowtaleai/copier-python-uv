import pytest


def test_bake_with_defaults(tmp_path, copier):
    project = copier.copy(tmp_path)

    found_toplevel_files = [f.name for f in project.path.glob("*")]
    assert ".gitignore" in found_toplevel_files
    assert "pyproject.toml" in found_toplevel_files
    assert ".python-version" in found_toplevel_files
    assert ".editorconfig" in found_toplevel_files
    assert "README.md" in found_toplevel_files
    assert "LICENSE" in found_toplevel_files
    assert ".gitattributes" in found_toplevel_files
    assert "tests" in found_toplevel_files
    assert ".vscode" in found_toplevel_files
    assert ".gitlab-ci.yml" not in found_toplevel_files
    assert "Pipfile" not in found_toplevel_files
    assert (project.path / "src" / "python_boilerplate").exists()
    assert not (project.path / "docs").exists()


def test_bake_with_proprietary_license(tmp_path, copier):
    custom_answers = {"license": "Proprietary"}

    project = copier.copy(tmp_path, **custom_answers)

    found_toplevel_files = [f.name for f in project.path.glob("*")]
    assert "LICENSE" in found_toplevel_files


def test_bake_with_invalid_package_name(tmp_path, copier):
    custom_answers = {"package_name": "1invalid"}

    with pytest.raises(ValueError, match="Validation error for question"):
        copier.copy(tmp_path, **custom_answers)


def test_bake_cli_application(tmp_path, copier):
    custom_answers = {"package_type": "cli"}

    project = copier.copy(tmp_path, **custom_answers)

    found_cli_script = [f.name for f in project.path.glob("**/cli.py")]
    assert found_cli_script


def test_bake_library(tmp_path, copier):
    custom_answers = {"package_type": "library"}

    project = copier.copy(tmp_path, **custom_answers)

    found_cli_script = [f.name for f in project.path.glob("**/cli.py")]
    assert not found_cli_script


def test_bake_namespaced_library(tmp_path, copier):
    custom_answers = {
        "package_type": "library",
        "package_name": "flowtale.copier.template",
    }

    project = copier.copy(tmp_path, **custom_answers)

    package_path = project.path / "src"
    assert list(package_path.iterdir())[0].name == "flowtale"
    assert list((package_path / "flowtale").iterdir())[0].name == "copier"
    assert list((package_path / "flowtale" / "copier").iterdir())[0].name == "template"


def test_bake_app_and_check_cli_scripts(tmp_path, copier):
    custom_answers = {"package_type": "cli"}

    project = copier.copy(tmp_path, **custom_answers)

    assert project.path.is_dir()
    pyproject_path = project.path / "pyproject.toml"
    assert_str = '[project.scripts]\npython_boilerplate = "python_boilerplate.cli:app"'
    assert assert_str in pyproject_path.read_text()


def test_bake_gitlab(tmp_path, copier):
    custom_answers = {"git_hosting": "gitlab"}

    project = copier.copy(tmp_path, **custom_answers)

    found_toplevel_files = [f.name for f in project.path.glob("*")]
    assert ".github" not in found_toplevel_files
    assert ".gitlab-ci.yml" in found_toplevel_files


def test_bake_github(tmp_path, copier):
    custom_answers = {"git_hosting": "github"}

    project = copier.copy(tmp_path, **custom_answers)

    found_toplevel_files = [f.name for f in project.path.glob("*")]
    assert ".gitlab-ci.yml" not in found_toplevel_files
    github_workflow_path = project.path / ".github/workflows/ci.yml"
    assert github_workflow_path.exists()


def test_bake_with_code_examples(tmp_path, copier):
    custom_answers = {
        "use_jupyter_notebooks": True,
        "generate_example_code": True,
    }

    project = copier.copy(tmp_path, **custom_answers)

    package_name = project.answers["package_name"]
    if "." in package_name:
        package_test_name = package_name.replace(".", "_")
        package_namespace = package_name.replace(".", "/")
    else:
        package_namespace = package_name
        package_test_name = package_name
    main_module_example_path = project.path / "src" / package_namespace / "core.py"
    main_module_test_example_path = (
        project.path / "tests" / f"test_{package_test_name}.py"
    )
    jupyter_notebook_example_path = (
        project.path / "notebooks" / "example_notebook.ipynb"
    )
    assert main_module_example_path.exists() is True
    assert main_module_test_example_path.exists() is True
    assert jupyter_notebook_example_path.exists() is True


def test_bake_without_code_examples(tmp_path, copier):
    custom_answers = {"use_jupyter_notebooks": True, "generate_example_code": False}

    project = copier.copy(tmp_path, **custom_answers)

    package_name = project.answers["package_name"]
    if "." in package_name:
        package_test_name = package_name.replace(".", "_")
        package_namespace = package_name.replace(".", "/")
    else:
        package_namespace = package_name
        package_test_name = package_name
    main_module_example_path = project.path / "src" / package_namespace / "core.py"
    main_module_test_example_path = (
        project.path / "tests" / f"test_{package_test_name}.py"
    )
    jupyter_notebook_example_path = (
        project.path / "notebooks" / "example_notebook.ipynb"
    )
    assert main_module_example_path.exists() is False
    assert main_module_test_example_path.exists() is False
    assert jupyter_notebook_example_path.exists() is False


def test_bake_with_many_files(tmp_path, copier):
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

    package_name = project.answers["package_name"]
    if "." in package_name:
        package_test_name = package_name.replace(".", "_")
        package_namespace = package_name.replace(".", "/")
    else:
        package_namespace = package_name
        package_test_name = package_name
    main_module_example_path = project.path / "src" / package_namespace / "core.py"
    main_module_test_example_path = (
        project.path / "tests" / f"test_{package_test_name}.py"
    )
    jupyter_notebook_example_path = (
        project.path / "notebooks" / "example_notebook.ipynb"
    )
    mkdocs_config_filepath = project.path / "mkdocs.yml"
    mkdocs_dir_path = project.path / "docs"
    dockerfile_path = project.path / "Dockerfile"
    assert main_module_example_path.exists() is True
    assert main_module_test_example_path.exists() is True
    assert jupyter_notebook_example_path.exists() is True
    assert mkdocs_config_filepath.exists() is True
    assert mkdocs_dir_path.exists() is True
    assert dockerfile_path.exists() is True


def test_bake_namespaced_package_with_many_files(tmp_path, copier):
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

    package_name = project.answers["package_name"]
    if "." in package_name:
        package_namespace = package_name.replace(".", "/")
        package_test_name = package_name.replace(".", "_")
    else:
        package_namespace = package_name
        package_test_name = package_name
    main_module_example_path = project.path / "src" / package_namespace / "core.py"
    main_module_test_example_path = (
        project.path / "tests" / f"test_{package_test_name}.py"
    )
    jupyter_notebook_example_path = (
        project.path / "notebooks" / "example_notebook.ipynb"
    )
    mkdocs_config_filepath = project.path / "mkdocs.yml"
    mkdocs_dir_path = project.path / "docs"
    dockerfile_path = project.path / "Dockerfile"
    assert main_module_example_path.exists() is True
    assert main_module_test_example_path.exists() is True
    assert jupyter_notebook_example_path.exists() is True
    assert mkdocs_config_filepath.exists() is True
    assert mkdocs_dir_path.exists() is True
    assert dockerfile_path.exists() is True


@pytest.mark.parametrize("git_hosting", ["github", "gitlab"])
def test_uv_version_consistency(tmp_path, copier, git_hosting):
    custom_answers = {
        "uv_version": "0.7.13",
        "generate_dockerfile": True,
        "git_hosting": git_hosting,
    }

    project = copier.copy(tmp_path, **custom_answers)

    dockerfile_path = project.path / "Dockerfile"
    assert "uv:0.7.13" in dockerfile_path.read_text()
    if git_hosting == "github":
        ci_path = project.path / ".github" / "workflows" / "ci.yml"
        assert 'UV_VERSION: "0.7.13"' in ci_path.read_text()
    elif git_hosting == "gitlab":
        ci_path = project.path / ".gitlab-ci.yml"
        assert "pip install uv==0.7.13" in ci_path.read_text()
    contributing_path = project.path / "CONTRIBUTING.md"
    assert "uv" in contributing_path.read_text()
    devcontainer_path = project.path / ".devcontainer" / "devcontainer.json"
    assert 'uv:1": {"version": "0.7.13" }' in devcontainer_path.read_text()


def test_with_hadolint_config_generation(tmp_path, copier):
    custom_answers = {
        "generate_dockerfile": True,
        "lint_dockerfile": True,
    }

    project = copier.copy(tmp_path, **custom_answers)

    pre_commit_path = project.path / ".pre-commit-configs" / "addon.standard.yaml"
    pyproject_path = project.path / "pyproject.toml"
    assert "hadolint" in pre_commit_path.read_text()
    assert "hadolint" in pyproject_path.read_text()


def test_without_hadolint(tmp_path, copier):
    custom_answers = {
        "lint_dockerfile": False,
    }

    project = copier.copy(tmp_path, **custom_answers)

    pre_commit_path = project.path / ".pre-commit-configs" / "addon.standard.yaml"
    pyproject_path = project.path / "pyproject.toml"
    assert "hadolint" not in pre_commit_path.read_text()
    assert "hadolint" not in pyproject_path.read_text()


def test_bake_with_docstring_linting_enabled(tmp_path, copier):
    custom_answers = {
        "customize_linting_components": True,
        "lint_docstrings": True,
    }

    project = copier.copy(tmp_path, **custom_answers)

    pyproject_path = project.path / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert '"D"' in pyproject_content
    assert "[tool.ruff.lint.pydocstyle]" in pyproject_content


def test_bake_with_docstring_linting_disabled(tmp_path, copier):
    custom_answers = {
        "customize_linting_components": True,
        "lint_docstrings": False,
    }

    project = copier.copy(tmp_path, **custom_answers)

    pyproject_path = project.path / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert '"D"' not in pyproject_content
    assert "[tool.ruff.lint.pydocstyle]" not in pyproject_content


def test_bake_without_selecting_linting_components(tmp_path, copier):
    custom_answers = {
        "customize_linting_components": False,
    }

    project = copier.copy(tmp_path, **custom_answers)

    pyproject_path = project.path / "pyproject.toml"
    pyproject_content = pyproject_path.read_text()
    assert '"D"' in pyproject_content
    assert "[tool.ruff.lint.pydocstyle]" in pyproject_content
