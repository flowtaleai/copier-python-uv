# tests/integration/test_readme_respects_skip_if_exists_update.py
from pathlib import Path
import shutil
import subprocess
import yaml

from tests.conftest import copier_defaults

def sh(cwd: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=cwd, check=True, text=True)

def data_args(answers: dict) -> list[str]:
    out = []
    for k, v in answers.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        out += ["--data", f"{k}={v}"]
    return out

def test_readme_respects_skip_if_exists_with_update(tmp_path: Path):
    # --- make a mutable copy of YOUR template ---
    repo_root = Path(__file__).resolve().parents[2]
    tpl = tmp_path / "tpl"
    tpl.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "template", tpl / "template")
    shutil.copy2(repo_root / "copier.yml", tpl / "copier.yml")

    # Ensure answers get written so `copier update` can find _src/_commit
    cfg = yaml.safe_load((tpl / "copier.yml").read_text(encoding="utf-8")) or {}
    if "_answers_file" not in cfg:
        cfg["_answers_file"] = ".copier-answers.yml"
        (tpl / "copier.yml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    readme_is_skipped = "README.md" in set(cfg.get("_skip_if_exists", []) or [])

    # Non-interactive answers for your template (adjust if you add required questions)
    answers = {
        "author_email": "user@example.com",
        "author_name": "The User",
        "distribution_name": "python-boilerplate",
        "package_name": "python_boilerplate",
        "project_name": "Python Boilerplate",
        "project_short_description": "An very nice project",
        "license": "MIT license",
        "package_type": "cli",
        "type_checker": "none",
        "type_checker_strictness": "strict",
    }
    dargs = data_args(answers)
    #dargs = copier_defaults()

    # Make the TEMPLATE a git repo so _commit is recorded
    sh(tpl, "git", "init")
    sh(tpl, "git", "config", "user.email", "test@example.com")
    sh(tpl, "git", "config", "user.name", "Test User")
    sh(tpl, "git", "add", "-A")
    sh(tpl, "git", "commit", "-m", "v1")

    # --- initial bake with answers file so update has state ---
    dest = tmp_path / "proj"
    sh(
        tmp_path,
        "copier", "copy",
        "--defaults",
        "--answers-file", ".copier-answers.yml",
        *dargs,
        str(tpl), str(dest),
    )

    # IMPORTANT: make the DESTINATION a git repo before update
    sh(dest, "git", "init")
    sh(dest, "git", "config", "user.email", "test@example.com")
    sh(dest, "git", "config", "user.name", "Test User")
    sh(dest, "git", "add", "-A")
    sh(dest, "git", "commit", "-m", "initial bake")

    readme = dest / "README.md"
    before = readme.read_text(encoding="utf-8")

    # Change TEMPLATE README so update would alter it (if not skipped)
    marker = "### READMESKIPTEST_V2_MARKER"
    (tpl / "template" / "README.md.jinja").write_text(marker + "\n", encoding="utf-8")
    sh(tpl, "git", "add", "-A")
    sh(tpl, "git", "commit", "-m", "v2")

    # --- run copier update in the baked project ---
    sh(dest, "copier", "update", "--defaults", *dargs)
    after = readme.read_text(encoding="utf-8")

    #if readme_is_skipped:
    assert after == before, "README.md changed even though it's in _skip_if_exists"
    assert marker not in after, "Marker found; README.md should have been skipped"
    # else:
    #     assert after != before, "README.md did not change but it's NOT in _skip_if_exists"
    #     assert after.startswith(marker), "README.md didn't pick up new template content"
