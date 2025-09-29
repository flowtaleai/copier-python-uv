from __future__ import annotations

import subprocess
from pathlib import Path

from .conftest import setup_git_repo


def test_skip_if_exists_preserves_readme_on_update(tmp_path, copier):
    """README stays untouched while LICENSE picks up template changes."""
    project = copier.copy(tmp_path)
    setup_git_repo(project)

    readme_path = project.path / "README.md"
    license_path = project.path / "LICENSE"

    original_license_content = license_path.read_text()

    user_managed_readme = "User-managed README content\n"
    readme_path.write_text(user_managed_readme)
    project.run("git add README.md")
    project.run("git commit -m 'Customize README'")

    template_root = Path(copier.template)
    template_subdir = template_root / "template"
    template_repo = template_root
    original_template_commit = (
        subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=template_repo)
        .decode()
        .strip()
    )
    template_readme_path = template_subdir / "README.md.jinja"
    license_template_name = "{% if license != 'Proprietary' %}LICENSE{% endif %}.jinja"
    template_license_path = template_subdir / license_template_name

    template_readme_content = template_readme_path.read_text()
    template_license_content = template_license_path.read_text()

    readme_template_marker = "\n<!-- Template README change marker -->\n"
    license_template_marker = "\nUpdated LICENSE template marker\n"

    rel_template_readme = template_readme_path.relative_to(template_repo).as_posix()
    rel_template_license = template_license_path.relative_to(template_repo).as_posix()

    subprocess.run(
        ["git", "config", "user.name", "Template User"],
        cwd=template_repo,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "template@example.com"],
        cwd=template_repo,
        check=True,
    )

    try:
        template_readme_path.write_text(
            template_readme_content + readme_template_marker
        )
        template_license_path.write_text(
            template_license_content + license_template_marker
        )

        subprocess.run(
            ["git", "add", rel_template_readme, rel_template_license],
            cwd=template_repo,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Apply template marker for tests"],
            cwd=template_repo,
            check=True,
        )

        project.run("copier update --defaults --vcs-ref HEAD")

        updated_readme = readme_path.read_text()
        updated_license = license_path.read_text()
    finally:
        subprocess.run(
            ["git", "reset", "--hard", original_template_commit],
            cwd=template_repo,
            check=True,
        )

    assert updated_readme == user_managed_readme
    assert readme_template_marker not in updated_readme

    assert updated_license != original_license_content
    assert license_template_marker in updated_license
