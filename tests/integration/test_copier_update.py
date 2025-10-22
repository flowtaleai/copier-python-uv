"""Integration: skip_if_exists behavior."""

import shutil
from pathlib import Path

import pytest
from pytest_copier.plugin import CopierFixture, CopierProject

from .conftest import git, setup_git_repo


@pytest.fixture
def template_copy(tmp_path_factory, copier):
    original_template_path = Path(copier.template)
    copy_template_path = tmp_path_factory.mktemp("template_root_copy")
    shutil.copytree(original_template_path, copy_template_path, dirs_exist_ok=True)

    git(copy_template_path, "config", "user.name", "Template User")
    git(copy_template_path, "config", "user.email", "template@example.com")

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


def modify_template_file(template_fixture, target_file_path: Path):
    template_root_path = template_fixture.template

    original = target_file_path.read_text()
    marker = "\n<!-- change marker -->\n"
    target_file_path.write_text(original + marker)

    git(template_root_path, "add", target_file_path)
    git(template_root_path, "commit", "-m", "Apply template markers for tests")
    git(template_root_path, "tag", "999.999.999")

    return marker


def answers_commit(project: CopierProject) -> str:
    answers = (project.path / ".copier-answers.yml").read_text()
    for line in answers.splitlines():
        if line.strip().startswith("_commit:"):
            return line.split(":", 1)[1].strip().strip("'").strip('"')
    return ""


def safe_update_project(project):
    """Safely update the project by checking for changes."""
    template_commit_before = answers_commit(project)
    project.update()
    template_commit_after = answers_commit(project)
    assert template_commit_before != template_commit_after


class TestSkipIfExists:
    """Tests for the skip_if_exists behavior of copier."""

    @pytest.mark.parametrize(
        ("project_file_path", "template_file_path", "custom_answers"),
        [
            ("README.md", "template/README.md.jinja", {}),
            ("CONTRIBUTING.md", "template/CONTRIBUTING.md.jinja", {}),
            (
                "src/python_boilerplate/cli.py",
                (
                    "template/src/{% if package_type == 'cli' %}"
                    "{{ package_name | replace('.', _copier_conf.sep) }}"
                    "{{ _copier_conf.sep }}cli.py{% endif %}.jinja"
                ),
                {},
            ),
            (
                "docs/user_guide.md",
                (
                    'template/{% if generate_docs != "none" %}docs{% endif %}/'
                    "{% if generate_example_code %}user_guide.md{% endif %}.jinja"
                ),
                {"generate_docs": "mkdocs", "generate_example_code": True},
            ),
        ],
    )
    def test_skip_if_exists_preserves_file_on_update(
        self,
        template_copy,
        tmp_path,
        project_file_path,
        template_file_path,
        custom_answers,
    ):
        project = template_copy.copy(tmp_path, **custom_answers)
        setup_git_repo(project)

        target_file = project.path / project_file_path
        user_content = modify_project_file(project, target_file)
        template_file = template_copy.template / template_file_path
        modify_template_file(template_copy, template_file)
        safe_update_project(project)

        assert target_file.read_text() == user_content

    def test_skip_if_exists_updates_non_skipped_file_from_template(
        self, template_copy, tmp_path
    ):
        project = template_copy.copy(tmp_path)
        setup_git_repo(project)

        project_pyproject_path = project.path / "pyproject.toml"
        modify_project_file(project, project_pyproject_path)
        copy_template_license_path = (
            template_copy.template / "template" / "pyproject.toml.jinja"
        )
        marker = modify_template_file(template_copy, copy_template_license_path)
        safe_update_project(project)

        assert marker in project_pyproject_path.read_text()
