"""Shared helpers for integration tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

from pytest_copier.plugin import CopierProject


def setup_git_repo(project: CopierProject) -> None:
    """Initialize git repository with initial commit."""
    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")


def setup_precommit_strict(project: CopierProject) -> None:
    """Setup pre-commit with strict configuration."""
    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    combined_config = (
        std_pre_commit_path.read_text() + strict_pre_commit_path.read_text()
    )
    dst_pre_commit_path.write_text(combined_config)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)


def git_output(cwd: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd).decode().strip()


def ensure_template_git_identity(repo: Path) -> None:
    git(repo, "config", "user.name", "Template User")
    git(repo, "config", "user.email", "template@example.com")


def template_paths_readme(copier) -> tuple[Path, Path]:
    template_root = Path(copier.template)
    readme_template = template_root / "template" / "README.md.jinja"
    assert readme_template.exists()
    return template_root, readme_template


def template_paths_license(copier) -> tuple[Path, Path]:
    template_root = Path(copier.template)
    candidates = [
        template_root / "template" / "LICENSE.jinja",
        template_root
        / "template"
        / "{% if license != 'Proprietary' %}LICENSE{% endif %}.jinja",
    ]
    license_template = next((p for p in candidates if p.exists()), None)
    assert license_template
    assert license_template.exists()
    return template_root, license_template


def commit_template_changes(repo: Path, changes: dict[Path, str]):
    """Apply changes to template files and commit them."""
    ensure_template_git_identity(repo)
    for path, delta in changes.items():
        original = path.read_text()
        path.write_text(original + delta)
        git(repo, "add", path.relative_to(repo).as_posix())
    git(repo, "commit", "-m", "Apply template markers for tests")


def update_project(project: CopierProject) -> None:
    project.run("copier update --defaults --vcs-ref HEAD")


def answers_commit(project: CopierProject) -> str:
    answers = (project.path / ".copier-answers.yml").read_text()
    for line in answers.splitlines():
        if line.strip().startswith("_commit:"):
            return line.split(":", 1)[1].strip().strip("'").strip('"')
    return ""
