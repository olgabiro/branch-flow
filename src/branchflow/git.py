import subprocess
from os import popen
from pathlib import Path

from branchflow.task import Task

def get_branch_name(task_name: str):
    return f"feature/{task_name}"

def create_branches(task: Task):
    for project in task.projects:
        default_branch = get_default_branch(project.directory)
        feature_branch_name = get_branch_name(task.name)
        if task.parent is not None:
            parent_branch_name = get_branch_name(task.parent)
            create_branch(parent_branch_name, project.directory, default_branch)
            create_branch(feature_branch_name, project.directory, parent_branch_name)
        else:
            create_branch(feature_branch_name, project.directory, default_branch)


def create_branch(name: str, project_path: Path, parent_branch_name: str):
    result = subprocess.run(["git", "checkout", parent_branch_name], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return
    if not branch_exists(name, project_path):
        result = subprocess.run(["git", "branch", name], cwd=project_path, capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stderr)
            return
    result = subprocess.run(["git", "checkout", name], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)

def get_default_branch(project_path: Path) -> str:
    result = subprocess.run(["git", "var", "GIT_DEFAULT_BRANCH"], cwd=project_path, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return "main"

def branch_exists(name: str, project_path: Path):
    result = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"], cwd=project_path)
    return result.returncode == 0