"""Test copier update behavior."""

import shutil
import subprocess
from pathlib import Path

import pytest
from pytest_copier.plugin import CopierFixture

from .conftest import setup_git_repo


def _git(cwd_path: Path, *args: str) -> None:
    """Run git command in specified directory."""
    subprocess.run(["git", *args], cwd=cwd_path, check=True)


@pytest.fixture
def template_copy(tmp_path_factory, copier, monkeypatch) -> CopierFixture:
    """Create a temporary copy of the template for safe modification."""
    template_copy_path = tmp_path_factory.mktemp("template")
    shutil.copytree(copier.template, template_copy_path, dirs_exist_ok=True)

    _git(template_copy_path, "config", "user.name", "Template User")
    _git(template_copy_path, "config", "user.email", "template@example.com")

    return CopierFixture(template_copy_path, copier.defaults, monkeypatch)


def _modify_template(template_root_path: Path, changes: dict[Path, str]) -> None:
    """Modify template files and commit changes."""
    for file_path, delta in changes.items():
        file_path.write_text(file_path.read_text() + delta)
        _git(
            template_root_path,
            "add",
            file_path.relative_to(template_root_path).as_posix(),
        )
    _git(template_root_path, "commit", "-m", "Update template")


class TestSkipIfExists:
    """Test skip_if_exists behavior during copier updates."""

    def test_update_when_readme_modified_then_preserved(
        self, tmp_path, template_copy
    ) -> None:
        """README has skip_if_exists - user modifications are preserved."""
        # Arrange
        project = template_copy.copy(tmp_path)
        setup_git_repo(project)

        readme_path = project.path / "README.md"
        user_content = "User's custom README"
        readme_path.write_text(user_content)
        project.run("git add . && git commit -m 'Customize README'")

        # Act
        template_root_path = Path(template_copy.template)
        template_readme_path = template_root_path / "template" / "README.md.jinja"
        template_change_marker = "\nTEMPLATE_CHANGE_MARKER"
        _modify_template(
            template_root_path, {template_readme_path: template_change_marker}
        )
        project.run("copier update --defaults --vcs-ref HEAD")

        # Assert
        assert readme_path.read_text() == user_content

    def test_update_when_license_not_skipped_then_updated(
        self, tmp_path, template_copy
    ) -> None:
        """LICENSE has no skip_if_exists - template updates are applied."""
        # Arrange
        project = template_copy.copy(tmp_path)
        setup_git_repo(project)

        # Act
        template_root_path = Path(template_copy.template)
        template_license_path = (
            template_root_path
            / "template"
            / "{% if license != 'Proprietary' %}LICENSE{% endif %}.jinja"
        )
        template_change_marker = "\nTEMPLATE_CHANGE_MARKER"
        _modify_template(
            template_root_path, {template_license_path: template_change_marker}
        )
        project.run("copier update --defaults --vcs-ref HEAD")

        # Assert
        license_path = project.path / "LICENSE"
        assert template_change_marker in license_path.read_text()
