from dataclasses import dataclass

from branchflow.project import Project


@dataclass
class Task:
    name: str
    description: str | None
    projects: list[Project]
    parent: str | None
