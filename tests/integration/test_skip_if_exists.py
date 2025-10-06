"""Integration: skip_if_exists behavior."""

import shutil
from pathlib import Path

from pytest_copier.plugin import CopierFixture

from .conftest import (
    answers_commit,
    commit_template_changes,
    setup_git_repo,
    template_paths_license,
    update_project,
)


def test_skip_if_exists_preserves_readme_on_update(
    tmp_path,
    tmp_path_factory,
    copier,
):
    original_template_path = Path(copier.template)
    copy_template_path = tmp_path_factory.mktemp("template_root_copy")
    shutil.copytree(original_template_path, copy_template_path, dirs_exist_ok=True)
    copy_template_fixture = CopierFixture(
        template=copy_template_path,
        defaults=copier.defaults,
        monkeypatch=copier.monkeypatch,
    )

    project = copy_template_fixture.copy(tmp_path)
    setup_git_repo(project)

    readme_path = project.path / "README.md"
    user_content = "User-managed README content\n"
    readme_path.write_text(user_content)
    project.run("git add README.md")
    project.run("git commit -m 'Customize README'")

    copy_template_readme_path = copy_template_path / "template" / "README.md.jinja"
    marker = "\n<!-- Template README change marker -->\n"
    commit_template_changes(copy_template_path, {copy_template_readme_path: marker})

    template_commit_before = answers_commit(project)
    project.update()
    template_commit_after = answers_commit(project)

    assert template_commit_before != template_commit_after
    assert readme_path.read_text() == user_content


def test_skip_if_exists_updates_license_from_template(tmp_path, copier):
    project = copier.copy(tmp_path)
    setup_git_repo(project)

    license_file = project.path / "LICENSE"
    original = license_file.read_text()

    template_repo, tpl_license = template_paths_license(copier)
    license_marker = "\nUpdated LICENSE template marker\n"

    with commit_template_changes(template_repo, {tpl_license: license_marker}):
        update_project(project)

    updated = license_file.read_text()
    assert updated != original
    assert license_marker in updated
