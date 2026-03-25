import os
import subprocess
from pathlib import Path


def get_branch_name(task_name: str):
    return f"feature/{task_name}"


def create_branch(branch_name: str, project_path: Path, parent_branch_name: str):
    switch_branch(parent_branch_name, project_path)

    if not branch_exists(branch_name, project_path):
        result = subprocess.run(
            ["git", "branch", branch_name],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ValueError(result.stderr)

    switch_branch(branch_name, project_path)


def get_default_branch(project_path: Path) -> str:
    head_ref = os.path.join(project_path, ".git", "refs", "remotes", "origin", "HEAD")
    if os.path.exists(head_ref):
        with open(head_ref, "r") as f:
            ref = f.read().strip()
            return ref.split("/")[-1]
    return "main"


def branch_exists(name: str, project_path: Path):
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
        cwd=project_path,
    )
    return result.returncode == 0


def switch_branch(branch_name: str, project_path: Path):
    result = subprocess.run(
        ["git", "checkout", branch_name],
        cwd=project_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError(result.stderr)
