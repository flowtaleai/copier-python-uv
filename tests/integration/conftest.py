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


def setup_precommit_strict(project: CopierProject) -> None:
    """Setup pre-commit with strict configuration."""
    config_dir = project.path / ".pre-commit-configs"
    std_pre_commit_path = config_dir / "standard.yaml"
    strict_pre_commit_path = config_dir / "addon.strict.yaml"
    ruff_pre_commit_path = config_dir / "addon.ruff.yaml"
    mypy_pre_commit_path = config_dir / "addon.mypy.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"

    combined_config = (
        std_pre_commit_path.read_text()
        + strict_pre_commit_path.read_text()
        + ruff_pre_commit_path.read_text()
    )

    # Add mypy if it exists
    if mypy_pre_commit_path.exists():
        combined_config += mypy_pre_commit_path.read_text()

    dst_pre_commit_path.write_text(combined_config)


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)
