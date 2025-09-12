# tests/integration/test_readme_respects_skip_if_exists_update.py
import shutil
import subprocess
from pathlib import Path

import yaml


def sh(cwd: Path, *args: str) -> None:
    subprocess.run(list(args), cwd=cwd, check=True, text=True)


def data_args(answers: dict) -> list[str]:
    out = []
    for k, v in answers.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        out += ["--data", f"{k}={v}"]
    return out


def test_readme_respects_skip_if_exists_with_update(tmp_path: Path, copier_defaults):
    repo_root = Path(__file__).resolve().parents[2]
    tpl = tmp_path / "tpl"
    tpl.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "template", tpl / "template")
    shutil.copy2(repo_root / "copier.yml", tpl / "copier.yml")

    cfg_path = tpl / "copier.yml"
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    cfg.setdefault("_answers_file", ".copier-answers.yml")
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    dargs = data_args(copier_defaults)
    sh(tpl, "git", "init")
    sh(tpl, "git", "config", "user.email", "test@example.com")
    sh(tpl, "git", "config", "user.name", "Test User")
    sh(tpl, "git", "add", "-A")
    sh(tpl, "git", "commit", "-m", "v1")

    dest = tmp_path / "proj"
    sh(
        tmp_path,
        "copier",
        "copy",
        "--defaults",
        "--answers-file",
        ".copier-answers.yml",
        *dargs,
        str(tpl),
        str(dest),
    )

    # Destination must be git-tracked for `copier update`
    sh(dest, "git", "init")
    sh(dest, "git", "config", "user.email", "test@example.com")
    sh(dest, "git", "config", "user.name", "Test User")
    sh(dest, "git", "add", "-A")
    sh(dest, "git", "commit", "-m", "initial bake")

    # Paths & snapshots
    readme = dest / "README.md"
    readme_before = readme.read_text(encoding="utf-8")

    control_name = "Makefile"  # Should be updated
    control_path = dest / control_name
    assert control_path.exists(), f"{control_name} not generated in dest"
    control_before = control_path.read_text(encoding="utf-8")

    readme_marker = "### READMESKIPTEST_V2_MARKER"
    (tpl / "template" / "README.md.jinja").write_text(
        readme_marker + "\n", encoding="utf-8"
    )

    control_marker = "### CONTROL_V2_MARKER"
    control_tpl_jinja = tpl / "template" / f"{control_name}.jinja"
    control_tpl_raw = tpl / "template" / control_name
    if control_tpl_jinja.exists():
        control_tpl_jinja.write_text(control_marker + "\n", encoding="utf-8")
    elif control_tpl_raw.exists():
        control_tpl_raw.write_text(control_marker + "\n", encoding="utf-8")
    else:
        raise AssertionError(
            f"Template source for {control_name} not found in template/"
        )

    sh(tpl, "git", "add", "-A")
    sh(tpl, "git", "commit", "-m", "v2: change README and control file")

    sh(dest, "copier", "update", "--defaults", *dargs)

    readme_after = readme.read_text(encoding="utf-8")
    assert (
        readme_after == readme_before
    ), "README.md changed even though it's in _skip_if_exists"
    assert (
        readme_marker not in readme_after
    ), "Marker found; README.md should have been skipped"

    control_after = control_path.read_text(encoding="utf-8")
    assert (
        control_after != control_before
    ), f"{control_name} did not change but it is NOT in _skip_if_exists"
    assert (
        control_marker in control_after
    ), f"{control_name} did not pick up new template content"
