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


def answers_commit(project: CopierProject) -> str:
    answers = (project.path / ".copier-answers.yml").read_text()
    for line in answers.splitlines():
        if line.strip().startswith("_commit:"):
            return line.split(":", 1)[1].strip().strip("'").strip('"')
    return ""
