"""Shared helpers for integration tests."""


def setup_git_repo(project):
    """Initialize git repository with initial commit."""
    project.run("git init")
    project.run("git add .")
    project.run("git config user.name 'User Name'")
    project.run("git config user.email 'user@email.org'")
    project.run("git commit -m init")


def setup_precommit_strict(project):
    """Setup pre-commit with strict configuration."""
    std_pre_commit_path = project.path / ".pre-commit-config.standard.yaml"
    strict_pre_commit_path = project.path / ".pre-commit-config.addon.strict.yaml"
    dst_pre_commit_path = project.path / ".pre-commit-config.yaml"
    combined_config = (
        std_pre_commit_path.read_text() + strict_pre_commit_path.read_text()
    )
    dst_pre_commit_path.write_text(combined_config)
