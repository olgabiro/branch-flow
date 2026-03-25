import subprocess
from pathlib import Path


def get_branch_name(task_name: str):
    return f"feature/{task_name}"


def create_branch(name: str, project_path: Path, parent_branch_name: str):
    result = subprocess.run(
        ["git", "checkout", parent_branch_name],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr)

    if not branch_exists(name, project_path):
        result = subprocess.run(
            ["git", "branch", name], cwd=project_path, capture_output=True, text=True
        )
        if result.returncode != 0:
            raise ValueError(result.stderr)
    result = subprocess.run(
        ["git", "checkout", name], cwd=project_path, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise ValueError(result.stderr)


def get_default_branch(project_path: Path) -> str:
    result = subprocess.run(
        ["git", "var", "GIT_DEFAULT_BRANCH"],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return "main"


def branch_exists(name: str, project_path: Path):
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
        cwd=project_path,
    )
    return result.returncode == 0


def switch_branch(name: str, project_path: Path):
    branch_name = get_branch_name(name)
    result = subprocess.run(["git", "checkout", branch_name], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(result.stderr)
