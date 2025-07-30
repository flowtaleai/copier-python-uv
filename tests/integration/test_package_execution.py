"""Tests for package runtime execution functionality."""

import pytest


@pytest.mark.venv
def test_bake_and_run_tests_with_pytest_framework(tmp_path, copier):
    custom_answers = {"testing_framework": "pytest"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("pytest")


@pytest.mark.venv
def test_bake_and_run_cli(tmp_path, copier):
    custom_answers = {"package_type": "cli"}
    project = copier.copy(tmp_path, **custom_answers)

    project.run("uv sync")
    project.run("uv run python_boilerplate")
