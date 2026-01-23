"""Shared helpers for integration tests."""

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


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)
