from pathlib import Path
from typing import List

from branchflow.config_service import find_task, get_project, add_task, set_current_task
from branchflow.git import get_branch_name, create_branch, get_default_branch
from branchflow.task import Task


def create_task(
        name: str, description: str | None, project_names: List[str], parent: str | None
) -> Task:
    projects = fetch_and_validate_projects(project_names)
    task = Task(name, description, projects, parent)
    validate_task(task)
    create_parent_task_if_needed(task, project_names)
    create_branches(task)
    add_task(task)
    set_current_task(name)
    return task


def validate_task(task: Task):
    if find_task(task.name) is not None:
        raise ValueError(f"Task [bold green]{task.name}[/] already exists.")
    validate_no_cycles(task)


def validate_no_cycles(task: Task):
    parent: Task | None = find_task(task.parent)
    while parent is not None:
        if parent.name == task.name:
            raise ValueError(
                "Cyclic dependency detected. Correct the parent task relationships."
            )
        parent = find_task(parent.parent)


def fetch_and_validate_projects(project_names: List[str]):
    projects = []
    for project_name in project_names:
        project = get_project(project_name)
        if project is None:
            raise ValueError(
                f"Unknown project [bold]{project_name}[/]. Add it with [italic]'bf add {project_name}'[/] first."
            )
        projects.append(project)
    return projects


def create_parent_task_if_needed(task: Task, project_names: List[str]):
    if task.parent is not None:
        parent_task = find_task(task.parent)
        if parent_task is None:
            create_task(task.parent, None, project_names, None)


def create_branches(task: Task):
    for project in task.projects:
        directory = project.directory
        default_branch = get_default_branch(directory)
        feature_branch_name = get_branch_name(task.name)
        if task.parent is not None:
            grandparent_branch_name = get_parent_base_branch(task.parent, directory)
            parent_branch_name = get_branch_name(task.parent)
            create_branch(
                parent_branch_name, directory, grandparent_branch_name
            )
            create_branch(feature_branch_name, directory, parent_branch_name)
        else:
            create_branch(feature_branch_name, directory, default_branch)


def get_parent_base_branch(parent_task_name: str, directory: Path):
    grandparent_task = find_task(parent_task_name)
    if grandparent_task is None or grandparent_task.parent is None:
        return get_default_branch(directory)
    else:
        return get_branch_name(grandparent_task.parent)
