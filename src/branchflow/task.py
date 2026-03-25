from dataclasses import dataclass

from branchflow.project import Project


@dataclass
class BranchData:
    project_name: str
    branch_name: str


@dataclass
class Task:
    name: str
    description: str | None
    projects: list[Project]
    parent: str | None
    branches: dict[str, BranchData]
