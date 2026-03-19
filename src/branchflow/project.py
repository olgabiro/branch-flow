from dataclasses import dataclass
from pathlib import Path


@dataclass
class Project:
    name: str
    directory: Path


def from_config(config):
    return Project(config["name"], Path(config["directory"]))
