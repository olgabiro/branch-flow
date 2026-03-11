import subprocess
from os import popen
from pathlib import Path

from branchflow.task import Task


def create_branches(task: Task):
    for project in task.projects:
        create_branch(f"feature/{task.name}", project.directory)


def create_branch(name: str, project_path: Path):
    result = subprocess.run(["git", "checkout", "main"], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return
    result = subprocess.run(["git", "branch", name], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        return
    result = subprocess.run(["git", "checkout", name], cwd=project_path, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
