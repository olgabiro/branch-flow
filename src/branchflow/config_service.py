from pathlib import Path
from typing import List

import yaml
from branchflow.project import Project
from branchflow.task import Task

CONFIG_PATH = Path.home() / ".branchflow" / "config.yaml"


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f)
            return config if config else {}
    else:
        return {}


def save_config(config):
    CONFIG_PATH.parent.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)


def find_task(name: str | None) -> Task | None:
    if name is None:
        return None

    tasks = load_config().get("tasks", [])
    for task in tasks:
        if task["name"] == name:
            return from_config(name, task)
    return None


def add_project(name: str, directory: str) -> str:
    config = load_config()
    projects_ = config.get("projects", {})

    if name in projects_:
        raise ValueError(f"Project [bold]{name}[/] already exists ({projects_[name]}).")

    project_path = Path(directory).resolve()

    if not project_path.exists():
        raise ValueError(f"Directory {directory} does not exist.")

    projects_[name] = str(project_path)
    config["projects"] = projects_
    save_config(config)
    return str(project_path)


def add_task(task: Task):
    config = load_config()
    tasks_: list[dict] = config.get("tasks", [])
    task_config = task_to_config(task)
    tasks_.append(task_config)
    config["tasks"] = tasks_
    save_config(config)


def get_all_tasks():
    tasks = load_config().get("tasks", [])
    return tasks if tasks else []


def get_current_task() -> Task | None:
    config = load_config()
    task_name = config.get("current_task", None)
    if task_name:
        tasks_by_name = {task["name"]: task for task in config.get("tasks", [])}
        if task_name not in tasks_by_name.keys():
            return None
        return from_config(task_name, tasks_by_name[task_name])
    return None


def set_current_task(task_name: str):
    config = load_config()
    if task_name not in [task["name"] for task in config.get("tasks", [])]:
        raise ValueError(f"Task [bold green]{task_name}[/] does not exist.")

    config["current_task"] = task_name
    save_config(config)


def get_project(name: str) -> Project | None:
    projects = load_config().get("projects", {})
    project_path = projects.get(name, None)
    return project_from_config(name, project_path) if project_path else None


def project_from_config(name: str, project_path) -> Project:
    assert project_path is not None
    return Project(name, Path(project_path))


def get_all_projects() -> List[Project]:
    projects = load_config().get("projects", {})
    return [project_from_config(name, path) for name, path in projects.items()]


def from_config(name, task_config) -> Task:
    project_names: list[str] = task_config.get("projects", [])
    projects: list[Project] = [
        project for name in project_names if (project := get_project(name)) is not None
    ]
    return Task(
        name,
        task_config.get("description", None),
        projects,
        task_config.get("parent", None),
    )


def task_to_config(task: Task) -> dict[str, str | list[str]]:
    config: dict[str, str | list[str]] = {"name": task.name}
    if task.description:
        config["description"] = task.description
    if task.projects:
        config["projects"] = [project.name for project in task.projects]
    if task.parent:
        config["parent"] = task.parent
    return config
