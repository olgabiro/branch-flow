import pytest

from branchflow.project_service import create_project
from branchflow import config_service


def test_create_project_new(temp_config_file, git_repo):
    project = create_project("TestProject", str(git_repo))

    assert project.name == "TestProject"
    assert project.directory == git_repo.resolve()

    found = config_service.find_project("TestProject")
    assert found is not None
    assert found.name == "TestProject"


def test_create_project_duplicate(temp_config_file, git_repo):
    create_project("TestProject", str(git_repo))

    with pytest.raises(ValueError, match="already exists"):
        create_project("TestProject", str(git_repo))


def test_create_project_directory_not_exists(temp_config_file):
    with pytest.raises(ValueError, match="does not exist"):
        create_project("TestProject", "/nonexistent/path")


def test_find_project_nonexistent(temp_config_file):
    result = config_service.find_project("NonExistent")
    assert result is None
