from __future__ import annotations

import subprocess

import yaml

from .conftest import setup_git_repo


def test_skip_if_exists_respected_on_update(
    tmp_path,
    copier,
    copier_defaults,
    template_git_repo,
    ensure_clean_git,
):
    """README stays untouched on update while LICENSE picks up template changes."""

    project = copier.copy(
        tmp_path,
        _src_path=str(template_git_repo),
        **copier_defaults,
    )

    setup_git_repo(project)
    ensure_clean_git(project, "test: baseline snapshot")

    readme_path = project.path / "README.md"
    license_path = project.path / "LICENSE"

    readme_before = readme_path.read_text(encoding="utf-8")
    license_before = license_path.read_text(encoding="utf-8")

    readme_marker = "### README_SKIP_IF_EXISTS_MARKER"
    readme_tpl_path = template_git_repo / "template" / "README.md.jinja"
    readme_tpl_path.write_text(
        readme_tpl_path.read_text(encoding="utf-8") + "\n" + readme_marker + "\n",
        encoding="utf-8",
    )

    license_marker = "### LICENSE_SHOULD_UPDATE_MARKER"
    license_tpl_path = (
        template_git_repo
        / "template"
        / "{% if license != 'Proprietary' %}LICENSE{% endif %}.jinja"
    )
    license_tpl_path.write_text(
        license_tpl_path.read_text(encoding="utf-8") + "\n" + license_marker + "\n",
        encoding="utf-8",
    )

    subprocess.run(["git", "add", "-A"], cwd=template_git_repo, check=True, text=True)
    subprocess.run(
        ["git", "commit", "-m", "test: mutate README and LICENSE"],
        cwd=template_git_repo,
        check=True,
        text=True,
    )

    answers_path = project.path / ".copier-answers.yml"
    answers = yaml.safe_load(answers_path.read_text(encoding="utf-8")) or {}
    answers["_src_path"] = str(template_git_repo)
    answers.pop("_commit", None)
    answers.pop("_src_url", None)
    answers_path.write_text(yaml.safe_dump(answers, sort_keys=False), encoding="utf-8")
    ensure_clean_git(project, "test: answers point to HEAD")

    project.run("copier recopy --defaults --force -r HEAD")

    readme_after = readme_path.read_text(encoding="utf-8")
    assert readme_after == readme_before
    assert readme_marker not in readme_after

    license_after = license_path.read_text(encoding="utf-8")
    assert license_after != license_before
    assert license_marker in license_after
