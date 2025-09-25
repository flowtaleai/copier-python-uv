import pytest


@pytest.mark.venv
def test_make_build(tmp_path, copier):
    custom_answers = {
        "package_type": "cli",
        "use_just": False,
    }
    project = copier.copy(tmp_path, **custom_answers)
    project.run("uv sync --no-install-project")

    project.run("make build")

    package_name = project.answers["package_name"]
    package_version = project.answers["version"]
    python_wheel_path = (
        project.path / "dist" / f"{package_name}-{package_version}-py3-none-any.whl"
    )
    assert python_wheel_path.exists()


@pytest.mark.venv
def test_just_build(tmp_path, copier):
    custom_answers = {
        "package_type": "cli",
    }
    project = copier.copy(tmp_path, **custom_answers)
    project.run("just setup --no-install-project")

    project.run("just build")

    package_name = project.answers["package_name"]
    package_version = project.answers["version"]
    python_wheel_path = (
        project.path / "dist" / f"{package_name}-{package_version}-py3-none-any.whl"
    )
    assert python_wheel_path.exists()
