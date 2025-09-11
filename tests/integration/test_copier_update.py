# tests/integration/test_copier_update.py
import shutil
import subprocess
from pathlib import Path

import yaml

from .conftest import setup_git_repo


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True)


def test_copier_update_respects_skip_if_exists(tmp_path, copier):
    """
    End-to-end:
      - Create a mutable, versioned (git) template.
      - Force _skip_if_exists to only .envrc and pyproject.toml (README must NOT be skipped).
      - Bake a project from the template (records _commit).
      - Change README and pyproject templates and commit.
      - Run `copier update --defaults --conflict=replace`.
      - Assert skipped files unchanged; README updated.
    """
    # ---- 1) Prepare a mutable *git* template ----
    repo_root = Path(__file__).resolve().parents[2]
    mutable_tpl = tmp_path / "tpl"
    mutable_tpl.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "template", mutable_tpl / "template")
    shutil.copy2(repo_root / "copier.yml", mutable_tpl / "copier.yml")

    # Force _skip_if_exists EXACTLY to the files we want skipped for this test.
    copier_yml = mutable_tpl / "copier.yml"
    config = yaml.safe_load(copier_yml.read_text(encoding="utf-8")) or {}
    config["_skip_if_exists"] = [".envrc", "pyproject.toml"]
    copier_yml.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")

    # Initialize git for the template BEFORE baking; commit as v1
    _git(mutable_tpl, "init")
    _git(mutable_tpl, "config", "user.email", "test@example.com")
    _git(mutable_tpl, "config", "user.name", "Test User")
    _git(mutable_tpl, "add", "-A")
    _git(mutable_tpl, "commit", "-m", "template v1")

    # ---- 2) Bake a project from the template (answers now record _commit) ----
    dest = tmp_path / "proj"
    project = copier.copy(
        dest,
        template=str(mutable_tpl),  # path to the git repo
        generate_docs="mkdocs",
        package_type="cli",
    )
    setup_git_repo(project)  # helper expects a CopierProject and uses .run()

    # Paths to verify
    pyproject_path = project.path / "pyproject.toml"
    envrc_path = project.path / ".envrc"
    readme_path = project.path / "README.md"

    # Ensure .envrc exists with a local tweak so we can detect any clobber
    if not envrc_path.exists():
        envrc_path.write_text('export FOO="local"\n', encoding="utf-8")

    # Snapshot before update (for skipped files)
    pyproject_before = pyproject_path.read_text(encoding="utf-8")
    envrc_before = envrc_path.read_text(encoding="utf-8")

    # Sanity check: answers should contain _commit (means template was a git repo at bake time)
    answers_text = (project.path / ".copier-answers.yml").read_text(encoding="utf-8")
    assert "_commit:" in answers_text

    # ---- 3) Change the TEMPLATE (not the baked project) and commit as v2 ----
    (mutable_tpl / "template" / "README.md.jinja").write_text(
        "# NEW README TITLE FROM TEMPLATE\n",
        encoding="utf-8",
    )

    pyproject_tpl = mutable_tpl / "template" / "pyproject.toml.jinja"
    if pyproject_tpl.exists():
        tpl_text = pyproject_tpl.read_text(encoding="utf-8")
        if "# updated by template" not in tpl_text:
            tpl_text = tpl_text.replace(
                "[project]", "[project]\n# updated by template\n", 1
            )
        pyproject_tpl.write_text(tpl_text, encoding="utf-8")
    else:
        # Ensure there is a template delta that would change pyproject.toml (but should be skipped)
        pyproject_tpl.write_text(
            "[project]\n# updated by template\n{{ super() if false else '' }}\n",
            encoding="utf-8",
        )

    _git(mutable_tpl, "add", "-A")
    _git(mutable_tpl, "commit", "-m", "template v2: change README & pyproject")

    # ---- 4) Make a checkpoint commit in the project (clean tree) ----
    project.run("git add .")
    project.run('git commit --allow-empty -m "pre-update state"')

    # ---- 5) Update (explicitly replace on conflicts so non-skipped files get updated) ----
    project.run("copier update --defaults --conflict=replace")

    # ---- 6) Assertions ----
    # Skipped files unchanged
    assert pyproject_path.read_text(encoding="utf-8") == pyproject_before
    assert envrc_path.read_text(encoding="utf-8") == envrc_before

    # Non-skipped README updated
    readme_after = readme_path.read_text(encoding="utf-8")
    assert readme_after.startswith("# NEW README TITLE FROM TEMPLATE")
