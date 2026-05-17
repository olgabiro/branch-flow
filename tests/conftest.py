import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def git_repo(temp_dir):
    repo_path = temp_dir / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )

    (repo_path / "README.md").write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_path, check=True)

    return repo_path


@pytest.fixture
def git_repo_with_remote(temp_dir):
    remote_path = temp_dir / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote_path)], check=True)

    repo_path = temp_dir / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )

    subprocess.run(
        ["git", "remote", "add", "origin", str(remote_path)], cwd=repo_path, check=True
    )

    (repo_path / "README.md").write_text("# Test Repo\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_path, check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], cwd=repo_path, check=True)

    return {"repo": repo_path, "remote": remote_path}


@pytest.fixture
def config_path(temp_dir):
    config_dir = temp_dir / ".branchflow"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.yaml"


@pytest.fixture
def temp_config_file(tmp_path, monkeypatch):
    config_file = tmp_path / "config.yaml"
    monkeypatch.setattr("branchflow.config_service.CONFIG_PATH", config_file)
    return config_file
