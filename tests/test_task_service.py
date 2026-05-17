import pytest
import subprocess

from branchflow import task_service
from branchflow.project_service import create_project
from branchflow import config_service
from branchflow.task import Task, BranchData


def test_validate_task_duplicate(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    task = Task("PD-1234", "Test", [project], None, {})
    config_service.add_task(task)

    with pytest.raises(ValueError, match="already exists"):
        task_service.validate_task(Task("PD-1234", "Test", [], None, {}))


def test_validate_no_cycles(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    parent_task = Task("PD-1000", "Parent", [project], None, {})
    config_service.add_task(parent_task)

    task = Task("PD-1234", "Child", [project], "PD-1000", {})
    task_service.validate_no_cycles(task)


def test_validate_no_cycles_detect_cycle(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    task1 = Task("PD-1000", "Task 1", [project], "PD-2000", {})
    config_service.add_task(task1)

    task2 = Task("PD-2000", "Task 2", [project], "PD-1000", {})
    with pytest.raises(ValueError, match="Cyclic dependency"):
        task_service.validate_no_cycles(task2)


def test_validate_no_cycles_detect_longer_cycle(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    task1 = Task("PD-1000", "Task 1", [project], "PD-2000", {})
    config_service.add_task(task1)

    task2 = Task("PD-2000", "Task 2", [project], "PD-3000", {})
    config_service.add_task(task2)

    task3 = Task("PD-3000", "Task 3", [project], "PD-1000", {})
    with pytest.raises(ValueError, match="Cyclic dependency"):
        task_service.validate_no_cycles(task3)


def test_fetch_and_validate_projects(temp_config_file, git_repo):
    create_project("TestProject", str(git_repo))

    projects = task_service.fetch_and_validate_projects(["TestProject"])
    assert len(projects) == 1
    assert projects[0].name == "TestProject"


def test_fetch_and_validate_projects_unknown(temp_config_file):
    with pytest.raises(ValueError, match="Unknown project"):
        task_service.fetch_and_validate_projects(["NonExistent"])


def test_get_current_task(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))
    task = Task("PD-1234", "Test", [project], None, {})
    config_service.add_task(task)
    config_service.save_current_task("PD-1234")

    current = task_service.get_current_task()
    assert current is not None
    assert current.name == "PD-1234"


def test_get_current_task_none(temp_config_file):
    result = task_service.get_current_task()
    assert result is None


def test_get_all_tasks(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    task1 = Task("PD-1234", "Task 1", [project], None, {})
    task2 = Task("PD-5678", "Task 2", [project], None, {})
    config_service.add_task(task1)
    config_service.add_task(task2)

    tasks = task_service.get_all_tasks()
    assert len(tasks) == 2


def test_change_current_task(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    subprocess.run(["git", "branch", "feature/test"], cwd=git_repo, check=True)

    task = Task(
        name="PD-1234",
        description="Test",
        projects=[project],
        parent=None,
        branches={"TestProject": BranchData("TestProject", "feature/test")},
    )
    config_service.add_task(task)

    responses = task_service.change_current_task("PD-1234")

    assert len(responses) == 1
    assert "feature/test" in responses[0]


def test_change_current_task_not_found(temp_config_file):
    with pytest.raises(ValueError, match="does not exist"):
        task_service.change_current_task("NonExistent")


def test_merge_master_to_branches_no_task(temp_config_file):
    with pytest.raises(ValueError, match="No task is currently active"):
        task_service.merge_master_to_branches()


def test_get_base_branch_no_parent(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))
    task = Task("PD-1234", "Test", [project], None, {})
    config_service.add_task(task)

    result = task_service.get_base_branch("PD-1234", git_repo)
    assert result in ["main", "master"]


def test_get_base_branch_with_parent(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    parent_task = Task("PD-1000", "Parent", [project], None, {})
    config_service.add_task(parent_task)

    child_task = Task("PD-1234", "Child", [project], "PD-1000", {})
    config_service.add_task(child_task)

    result = task_service.get_base_branch("PD-1234", git_repo)
    assert result == "feature/PD-1000"
