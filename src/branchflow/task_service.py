from pathlib import Path
from typing import List

from branchflow.config_service import (
    find_task,
    find_project,
    add_task,
    get_current_task_name,
    get_tasks,
    save_current_task,
)
from branchflow.git_service import (
    get_branch_name,
    create_branch,
    get_default_branch,
    switch_branch,
)
from branchflow.project import Project
from branchflow.task import Task, BranchData


def create_task(
    name: str, description: str | None, project_names: List[str], parent: str | None
) -> Task:
    projects = fetch_and_validate_projects(project_names)
    task = Task(name, description, projects, parent, {})
    validate_task(task)
    create_parent_task_if_needed(task, project_names)
    create_branches(task)
    add_task(task)
    save_current_task(name)
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
        project = find_project(project_name)
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
            create_branch(parent_branch_name, directory, grandparent_branch_name)
            _add_tracked_branch(task, project, parent_branch_name)
            create_branch(feature_branch_name, directory, parent_branch_name)
            _add_tracked_branch(task, project, feature_branch_name)
        else:
            create_branch(feature_branch_name, directory, default_branch)
            _add_tracked_branch(task, project, feature_branch_name)


def _add_tracked_branch(task: Task, project: Project, branch_name: str):
    branch_data = BranchData(project.name, branch_name)
    task.branches[project.name] = branch_data


def get_parent_base_branch(parent_task_name: str, directory: Path):
    grandparent_task = find_task(parent_task_name)
    if grandparent_task is None or grandparent_task.parent is None:
        return get_default_branch(directory)
    else:
        return get_branch_name(grandparent_task.parent)


def get_current_task() -> Task | None:
    task_name = get_current_task_name()
    return find_task(task_name)


def get_all_tasks() -> List[Task]:
    return get_tasks()


def set_current_task(name: str) -> list[str]:
    task = find_task(name)
    if task is None:
        raise ValueError(f"Task [bold green]{name}[/] does not exist.")
    save_current_task(name)
    response = []
    for project in task.projects:
        branch = task.branches.get(project.name, None)
        if branch is not None:
            switch_branch(branch.branch_name, project.directory)
            response.append(
                f"Switched to branch [green]{branch.branch_name}[/] in project [bold green]{project.name}[/]"
            )
    return response
