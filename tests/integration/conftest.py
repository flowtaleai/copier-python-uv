"""Shared helpers for integration tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

import pytest
import yaml
from pytest_copier.plugin import CopierProject


@pytest.fixture
def ensure_clean_git():
    """
    Stage & commit anything pending in the baked project so Copier sees a clean tree.
    Usage: ensure_clean_git(project, "optional message")
    """

    def _ensure(project: CopierProject, message: str = "test: snapshot") -> None:
        project.run("git add -A")
        project.run(f"sh -c \"git diff --cached --quiet || git commit -m '{message}'\"")
        project.run("git config core.autocrlf false")

    return _ensure


@pytest.fixture
def template_git_repo(tmp_path: Path, copier_template_paths: Iterable[str]) -> Path:
    """
    Make a git-backed working copy of the template so we can mutate + commit (v1→v2).
    """
    tpl = tmp_path / "tpl"
    tpl.mkdir(parents=True, exist_ok=True)

    for rel in copier_template_paths:  # usually ["copier.yml", "template"]
        src = Path(rel)
        dst = tpl / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Ensure stable answers file path
    cfg_path = tpl / "copier.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    cfg.setdefault("_answers_file", ".copier-answers.yml")
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    # Init git (v1)
    subprocess.run(["git", "init"], cwd=tpl, check=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=tpl, check=True, text=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=tpl,
        check=True,
        text=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=tpl, check=True, text=True)
    subprocess.run(["git", "commit", "-m", "v1"], cwd=tpl, check=True, text=True)

    return tpl


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
