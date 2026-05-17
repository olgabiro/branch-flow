from pathlib import Path

from branchflow.config_service import (
    load_config,
    save_config,
    add_project,
    add_task,
    find_task,
    get_tasks,
    get_current_task_name,
    save_current_task,
    from_config,
    task_to_config,
)
from branchflow.project import Project
from branchflow.task import Task, BranchData


def test_save_and_load_config(temp_config_file):
    config = {"projects": {"test": "/path/to/test"}}
    save_config(config)

    loaded = load_config()
    assert loaded == config


def test_add_project(temp_config_file):
    project = Project("TestProject", Path("/tmp/test"))
    add_project(project)

    config = load_config()
    assert config["projects"]["TestProject"] == "/tmp/test"


def test_add_task(temp_config_file, git_repo):
    project = Project("TestProject", git_repo)
    add_project(project)

    task = Task(
        name="PD-1234",
        description="Test task",
        projects=[project],
        parent=None,
        branches={"TestProject": BranchData("TestProject", "feature/PD-1234")},
    )
    add_task(task)

    config = load_config()
    assert "PD-1234" in config["tasks"]


def test_find_task(temp_config_file, git_repo):
    project = Project("TestProject", git_repo)
    add_project(project)

    task = Task(
        name="PD-1234",
        description="Test task",
        projects=[project],
        parent=None,
        branches={},
    )
    add_task(task)

    found = find_task("PD-1234")
    assert found is not None
    assert found.name == "PD-1234"
    assert found.description == "Test task"


def test_find_task_nonexistent(temp_config_file):
    result = find_task("NonExistent")
    assert result is None


def test_get_tasks(temp_config_file, git_repo):
    project = Project("TestProject", git_repo)
    add_project(project)

    task1 = Task("PD-1234", "Task 1", [project], None, {})
    task2 = Task("PD-5678", "Task 2", [project], None, {})
    add_task(task1)
    add_task(task2)

    tasks = get_tasks()
    assert len(tasks) == 2
    task_names = [t.name for t in tasks]
    assert "PD-1234" in task_names
    assert "PD-5678" in task_names


def test_current_task(temp_config_file, git_repo):
    project = Project("TestProject", git_repo)
    add_project(project)

    task = Task("PD-1234", "Test", [project], None, {})
    add_task(task)

    save_current_task("PD-1234")

    assert get_current_task_name() == "PD-1234"


def test_task_to_config():
    project = Project("Test", Path("/tmp/test"))
    task = Task(
        name="PD-1234",
        description="Test task",
        projects=[project],
        parent="PD-1000",
        branches={"Test": BranchData("Test", "feature/PD-1234")},
    )

    config = task_to_config(task)

    assert config["description"] == "Test task"
    assert config["projects"] == ["Test"]
    assert config["parent"] == "PD-1000"
    assert config["branches"]["Test"] == "feature/PD-1234"


def test_task_to_config_minimal():
    task = Task(name="PD-1234", description=None, projects=[], parent=None, branches={})

    config = task_to_config(task)
    assert config == {}


def test_from_config(temp_config_file, git_repo):
    project = Project("TestProject", git_repo)
    add_project(project)

    task_config = {
        "description": "Test task",
        "projects": ["TestProject"],
        "parent": "PD-1000",
        "branches": {"TestProject": "feature/PD-1234"},
    }

    task = from_config("PD-1234", task_config)

    assert task.name == "PD-1234"
    assert task.description == "Test task"
    assert len(task.projects) == 1
    assert task.projects[0].name == "TestProject"
    assert task.parent == "PD-1000"
    assert "TestProject" in task.branches
