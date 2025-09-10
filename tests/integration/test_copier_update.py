# tests/integration/test_copier_update.py
from pathlib import Path
import shutil

from .conftest import setup_git_repo


def test_copier_update_respects_skip_if_exists(tmp_path, copier):
    """
    End-to-end test:
    - Make a mutable copy of the template.
    - Ensure _skip_if_exists contains .envrc and pyproject.toml.
    - Bake a project from the mutable template.
    - Change the template's README and pyproject templates.
    - Run `copier update --defaults` in the baked project.
    - Assert skipped files are unchanged; non-skipped one (README) changed.
    """
    # 1) Build a mutable template copy we can edit safely inside the test
    repo_root = Path(__file__).resolve().parents[2]
    mutable_tpl = tmp_path / "tpl"
    (mutable_tpl).mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "template", mutable_tpl / "template")
    shutil.copy2(repo_root / "copier.yml", mutable_tpl / "copier.yml")

    # 1a) Ensure _skip_if_exists includes only what we want for this test
    #     (so README.md is NOT skipped and should update)
    copier_yml = mutable_tpl / "copier.yml"
    print(copier_yml)
    yml = copier_yml.read_text()
    if "_skip_if_exists:" not in yml:
        yml += (
            "\n_skip_if_exists:\n"
            "  - .envrc\n"
            "  - pyproject.toml\n"
        )
    else:
        # Append (idempotently) the entries we care about
        if ".envrc" not in yml:
            yml += "\n  - .envrc\n"
        if "pyproject.toml" not in yml:
            yml += "  - pyproject.toml\n"
    copier_yml.write_text(yml)

    # 2) Bake a project from the mutable template
    project = copier.copy(
        tmp_path / "proj",
        template=str(mutable_tpl),
        generate_docs="mkdocs",   # enable docs to exercise more outputs
        package_type="cli",       # enable CLI to exercise src layout
    )
    setup_git_repo(project)

    # Paths we will check
    pyproject_path = project.path / "pyproject.toml"
    envrc_path = project.path / ".envrc"
    readme_path = project.path / "README.md"

    # Ensure .envrc exists with some local tweak so we can detect clobbering
    if not envrc_path.exists():
        envrc_path.write_text('export FOO="local"\n')

    # Snapshots before update (for skipped files)
    pyproject_before = pyproject_path.read_text(encoding="utf-8")
    envrc_before = envrc_path.read_text(encoding="utf-8")

    # 3) Modify the TEMPLATE (not the baked project)
    #    - Change README.md.jinja so README in project should update
    #    - Change pyproject.toml.jinja so pyproject would update, but is skipped
    (mutable_tpl / "template" / "README.md.jinja").write_text(
        "# NEW README TITLE FROM TEMPLATE\n",
        encoding="utf-8",
    )

    pyproject_tpl = mutable_tpl / "template" / "pyproject.toml.jinja"
    # If template is identical to the rendered content, inject a harmless line
    # so update would try to rewrite pyproject.toml unless skipped.
    if pyproject_tpl.exists():
        pyproject_tpl_text = pyproject_tpl.read_text(encoding="utf-8")
        if "# updated by template" not in pyproject_tpl_text:
            pyproject_tpl_text = pyproject_tpl_text.replace(
                "[project]",
                "[project]\n# updated by template\n",
                1
            )
        pyproject_tpl.write_text(pyproject_tpl_text, encoding="utf-8")
    else:
        # Fallback: create a minimal jinja file to ensure a template change exists
        pyproject_tpl.write_text(
            "[project]\n# updated by template\n{{ super() if false else '' }}\n",
            encoding="utf-8",
        )

    # 4) Make a checkpoint commit so the tree is "clean" (not strictly required,
    #    but mirrors docs recommendations and prevents CI warnings)
    # Use an empty commit because we didn’t change the baked project yet.
    project.run('git commit --allow-empty -m "pre-update state"')

    # 5) Run copier update from inside the baked project using previous answers
    project.run("copier update --defaults")

    # 6) Assertions
    # Skipped files remain unchanged
    assert pyproject_path.read_text(encoding="utf-8") == pyproject_before
    assert envrc_path.read_text(encoding="utf-8") == envrc_before

    # Non-skipped README should reflect the template change
    assert readme_path.read_text(encoding="utf-8").startswith(
        "# NEW README TITLE FROM TEMPLATE"
    )

# tests/integration/test_copier_update.py
from pathlib import Path
import shutil
import yaml

from .conftest import setup_git_repo


# tests/integration/test_copier_update.py
from pathlib import Path
import shutil
import yaml

from .conftest import setup_git_repo


def test_copier_update_respects_skip_if_exists_2(tmp_path, copier):
    """
    End-to-end test:
    - Make a mutable copy of the template.
    - Ensure _skip_if_exists contains .envrc and pyproject.toml.
    - Bake a project from the mutable template.
    - Change the template's README and pyproject templates.
    - Run `copier update --defaults` in the baked project.
    - Assert skipped files are unchanged; non-skipped one (README) changed.
    """
    # 1) Build a mutable template copy we can edit safely inside the test
    repo_root = Path(__file__).resolve().parents[2]
    mutable_tpl = tmp_path / "tpl"
    (mutable_tpl).mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo_root / "template", mutable_tpl / "template")
    shutil.copy2(repo_root / "copier.yml", mutable_tpl / "copier.yml")

    # Correctly modify copier.yml to include the skip-if-exists configuration
    copier_yml = mutable_tpl / "copier.yml"
    with open(copier_yml, 'r') as f:
        config = yaml.safe_load(f)

    if '_skip_if_exists' not in config:
        config['_skip_if_exists'] = []

    files_to_skip = ['.envrc', 'pyproject.toml']
    for file in files_to_skip:
        if file not in config['_skip_if_exists']:
            config['_skip_if_exists'].append(file)
    
    with open(copier_yml, 'w') as f:
        yaml.safe_dump(config, f)

    # 2) Bake a project from the mutable template
    project = copier.copy(
        tmp_path / "proj",
        template=str(mutable_tpl),
        generate_docs="mkdocs",
        package_type="cli",
    )
    # The project variable is a CopierProject object with a .run() method.
    setup_git_repo(project)

    # Paths we will check
    pyproject_path = project.path / "pyproject.toml"
    envrc_path = project.path / ".envrc"
    readme_path = project.path / "README.md"

    if not envrc_path.exists():
        envrc_path.write_text('export FOO="local"\n')

    pyproject_before = pyproject_path.read_text(encoding="utf-8")
    envrc_before = envrc_path.read_text(encoding="utf-8")

    # 3) Modify the TEMPLATE (not the baked project) and commit the changes
    (mutable_tpl / "template" / "README.md.jinja").write_text(
        "# NEW README TITLE FROM TEMPLATE\n",
        encoding="utf-8",
    )

    pyproject_tpl = mutable_tpl / "template" / "pyproject.toml.jinja"
    if pyproject_tpl.exists():
        pyproject_tpl_text = pyproject_tpl.read_text(encoding="utf-8")
        if "# updated by template" not in pyproject_tpl_text:
            pyproject_tpl_text = pyproject_tpl_text.replace(
                "[project]",
                "[project]\n# updated by template\n",
                1
            )
        pyproject_tpl.write_text(pyproject_tpl_text, encoding="utf-8")
    else:
        pyproject_tpl.write_text(
            "[project]\n# updated by template\n{{ super() if false else '' }}\n",
            encoding="utf-8",
        )

    # Make the template a git repository and commit the base files
    setup_git_repo(mutable_tpl)
    mutable_tpl.run('git add .')
    mutable_tpl.run('git commit -m "Initial template commit"')
    
    # 4) Make a checkpoint commit in the project
    project.run('git add .')
    project.run('git commit -m "Pre-update state"')

    # 5) Run copier update
    project.run("copier update --defaults")

    # 6) Assertions
    assert pyproject_path.read_text(encoding="utf-8") == pyproject_before
    assert envrc_path.read_text(encoding="utf-8") == envrc_before

    assert readme_path.read_text(encoding="utf-8").startswith(
        "# NEW README TITLE FROM TEMPLATE"
    )