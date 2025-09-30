"""Tests for external tool integration functionality."""

import pytest

from .conftest import setup_git_repo


class TestDocumentationGeneration:
    """Tests for documentation generation tools (pdoc, mkdocs)."""

    @pytest.mark.parametrize(
        ("framework", "frontpage_path"),
        [
            ("pdoc", "build/site/python_boilerplate.html"),
            ("mkdocs", "build/site/index.html"),
        ],
    )
    @pytest.mark.venv
    def test_bake_with_documentation(self, tmp_path, copier, framework, frontpage_path):
        custom_answers = {"generate_docs": framework}
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)
        project.run("just setup")

        project.run("just docs")

        frontpage_path = project.path / frontpage_path
        assert frontpage_path.exists()
        title = project.answers["package_name"] or project.answers["distribution_name"]
        with open(frontpage_path) as index:
            front_page = "\n".join(index.readlines())
        assert title in front_page
        assert "Usage" in front_page


class TestTypeChecking:
    """Tests for type checking tool integration (mypy)."""

    @pytest.mark.venv
    def test_mypy_with_mkdocs(self, tmp_path, copier):
        custom_answers = {
            "generate_docs": "mkdocs",
            "type_checker": "mypy",
        }
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)
        project.run("just setup-strict")

        project.run("just lint")


class TestDockerLinting:
    """Tests for Docker linting tool integration (hadolint)."""

    @pytest.mark.venv
    def test_hadolint_integration(self, tmp_path, copier):
        custom_answers = {
            "generate_dockerfile": True,
            "lint_dockerfile": True,
        }
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)
        project.run("just setup")

        project.run("uv run pre-commit run hadolint --all-files")


class TestVersionManagement:
    """Tests for version management tool integration (bump-my-version)."""

    @pytest.mark.venv
    def test_bump_version_updates_files(self, tmp_path, copier):
        custom_answers = {"package_name": "mypackage"}
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)

        project.run("uv run bump-my-version bump major")

        copier_answers_path = project.path / ".copier-answers.yml"
        pyproject_path = project.path / "pyproject.toml"
        project_init = project.path / "src" / "mypackage" / "__init__.py"
        assert "1.0.0" in copier_answers_path.read_text()
        assert "1.0.0" in pyproject_path.read_text()
        assert "1.0.0" in project_init.read_text()


class TestBlackIntegration:
    """Tests for code formatting tool integration (black)."""

    @pytest.mark.venv
    def test_black_fails_on_unformatted_code(self, tmp_path, copier):
        custom_answers = {"code_formatter": "black"}
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)
        project.run("just setup")

        # Create a file with unformatted code
        test_file = project.path / "src" / project.answers["package_name"] / "test.py"
        test_file.write_text(
            'test = "Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
            " Donec porta, nunc at interdum gravida, massa sem lacinia libero,"
            ' non feugiat turpis nunc nec sapien."'
        )

        with pytest.raises(RuntimeError) as exc_info:
            project.run("uv run black --check src/")

        assert "would be reformatted" in str(exc_info.value)

    @pytest.mark.venv
    def test_black_passes_on_formatted_code(self, tmp_path, copier):
        custom_answers = {"code_formatter": "black"}
        project = copier.copy(tmp_path, **custom_answers)
        setup_git_repo(project)
        project.run("just setup")

        output = project.run("uv run black --check src/")

        assert "left unchanged" in output
