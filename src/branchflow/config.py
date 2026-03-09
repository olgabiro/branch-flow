from pathlib import Path
from typing import Optional

import yaml

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


def add_task(name: str, description: Optional[str], projects: list[str], parent: Optional[str]):
    config = load_config()
    tasks_: list[dict] = config.get("tasks", [])

    task_names = [task['name'] for task in tasks_]
    if name in task_names:
        raise ValueError(f"Task [bold green]{name}[/] already exists.")

    if parent and parent not in task_names:
        raise ValueError(f"Parent task [bold green]{parent}[/] does not exist.")

    projects_ = config.get("projects", {})
    for project in projects:
        if project not in projects_:
            raise ValueError(f"Unknown project [bold]{project}[/]. Add it with [italic]'bf add {project}'[/] first.")

    task = {"name": name}
    if description:
        task["description"] = description
    if projects:
        task["projects"] = projects
    if parent:
        task["parent"] = parent
    tasks_.append(task)
    config["tasks"] = tasks_
    save_config(config)


def get_all_tasks():
    tasks = load_config().get("tasks", [])
    return tasks if tasks else []
