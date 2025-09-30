"""Integration: skip_if_exists behavior."""

from .conftest import (
    answers_commit,
    commit_template_changes,
    setup_git_repo,
    template_paths_license,
    template_paths_readme,
    update_project,
)


def test_skip_if_exists_preserves_readme_on_update(
    tmp_path,
    copier,
):
    project = copier.copy(tmp_path)
    setup_git_repo(project)

    readme = project.path / "README.md"
    user_content = "User-managed README content\n"
    readme.write_text(user_content)
    project.run("git add README.md")
    project.run("git commit -m 'Customize README'")

    before = answers_commit(project)

    template_repo, tpl_readme = template_paths_readme(copier)
    marker = "\n<!-- Template README change marker -->\n"

    with commit_template_changes(template_repo, {tpl_readme: marker}) as (
        new_sha,
        new_desc,
    ):
        update_project(project)

    assert readme.read_text() == user_content
    assert marker not in readme.read_text()
    assert answers_commit(project) == new_desc
    assert answers_commit(project) != before


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
