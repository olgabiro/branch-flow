from pathlib import Path

from branchflow.config_service import find_project, add_project
from branchflow.project import Project


def add_repository(name: str, directory: str) -> Project:
    existing_repository = find_project(name)
    if existing_repository is not None:
        raise ValueError(
            f"Repository [bold]{name}[/] already exists ({existing_repository.directory})."
        )

    repository_path = Path(directory).resolve()

    if not repository_path.exists():
        raise ValueError(f"Directory {directory} does not exist.")

    project = Project(name, repository_path)
    add_project(project)
    return project
