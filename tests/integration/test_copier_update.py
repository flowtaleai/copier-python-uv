"""Integration: skip_if_exists behavior."""

import shutil
from pathlib import Path

import pytest
from pytest_copier.plugin import CopierFixture

from .conftest import (
    answers_commit,
    commit_template_changes,
    setup_git_repo,
)


@pytest.fixture
def copy_template_fixture(tmp_path_factory, copier):
    original_template_path = Path(copier.template)
    copy_template_path = tmp_path_factory.mktemp("template_root_copy")
    shutil.copytree(original_template_path, copy_template_path, dirs_exist_ok=True)
    return CopierFixture(
        template=copy_template_path,
        defaults=copier.defaults,
        monkeypatch=copier.monkeypatch,
    )


def modify_project_file(project, target_file_path: Path):
    user_content = "User-managed README content\n"
    target_file_path.write_text(user_content)
    project.run(f"git add {target_file_path}")
    project.run("git commit -m 'Changes'")
    return user_content


class TestSkipIfExists:
    """Tests for the skip_if_exists behavior of copier."""

    def test_skip_if_exists_preserves_readme_on_update(
        self, copy_template_fixture, tmp_path
    ):
        project = copy_template_fixture.copy(tmp_path)
        setup_git_repo(project)

        readme_path = project.path / "README.md"
        user_content = modify_project_file(project, readme_path)

        copy_template_readme_path = (
            copy_template_fixture.template / "template" / "README.md.jinja"
        )
        marker = "\n<!-- Template README change marker -->\n"
        commit_template_changes(
            copy_template_fixture.template, {copy_template_readme_path: marker}
        )

        template_commit_before = answers_commit(project)
        project.update()
        template_commit_after = answers_commit(project)

        assert template_commit_before != template_commit_after
        assert readme_path.read_text() == user_content

    def test_skip_if_exists_updates_license_from_template(
        self, copy_template_fixture, tmp_path
    ):
        project = copy_template_fixture.copy(tmp_path)
        setup_git_repo(project)

        project_pyproject_path = project.path / "pyproject.toml"
        modify_project_file(project, project_pyproject_path)

        copy_template_license_path = (
            copy_template_fixture.template / "template" / "pyproject.toml.jinja"
        )
        marker = "\n<!-- Template pyproject change marker -->\n"
        commit_template_changes(
            copy_template_fixture.template, {copy_template_license_path: marker}
        )

        template_commit_before = answers_commit(project)
        project.update()
        template_commit_after = answers_commit(project)

        assert template_commit_before != template_commit_after
        assert marker in project_pyproject_path.read_text()
