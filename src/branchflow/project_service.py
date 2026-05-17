from pathlib import Path

from branchflow.config_service import find_project, add_project
from branchflow.project import Project


def create_project(name: str, directory: str) -> Project:
    existing_project = find_project(name)
    if existing_project is not None:
        raise ValueError(
            f"Project [bold]{name}[/] already exists ({existing_project.directory})."
        )

    project_path = Path(directory).resolve()

    if not project_path.exists():
        raise ValueError(f"Directory {directory} does not exist.")

    project = Project(name, project_path)
    add_project(project)
    return project
