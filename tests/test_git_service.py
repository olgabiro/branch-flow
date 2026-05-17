import subprocess

import pytest

from branchflow import git_service


def test_get_branch_name():
    assert git_service.get_branch_name("PD-1234") == "feature/PD-1234"
    assert git_service.get_branch_name("my-task") == "feature/my-task"


def test_feature_branch_name():
    assert git_service.feature_branch_name("PD-1234") == "feature/PD-1234"
    assert git_service.feature_branch_name("my task") == "feature/my-task"


def test_branch_exists(git_repo):
    assert git_service.branch_exists("main", git_repo) is True
    assert git_service.branch_exists("main", git_repo) is True
    assert git_service.branch_exists("nonexistent", git_repo) is False


def test_branch_exists_from_remote(git_repo_with_remote):
    repo = git_repo_with_remote["repo"]

    subprocess.run(
        ["git", "push", "origin", "main:refs/heads/feature/test"], cwd=repo, check=True
    )

    assert git_service.branch_exists("main", repo) is True
    assert git_service.branch_exists("feature/test", repo) is False


def test_branch_exists_tracks_remote_branch(git_repo_with_remote):
    repo = git_repo_with_remote["repo"]

    subprocess.run(["git", "fetch", "origin"], cwd=repo, check=True)

    assert git_service.branch_exists("main", repo) is True


def test_detect_base_branch_main(git_repo):
    result = git_service.detect_base_branch(git_repo)
    assert result == "main"


def test_detect_base_branch_master(temp_dir):
    repo_path = temp_dir / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=repo_path, check=True
    )
    subprocess.run(["git", "checkout", "-b", "master"], cwd=repo_path, check=True)

    (repo_path / "README.md").write_text("# Test\n")
    subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_path, check=True)

    result = git_service.detect_base_branch(repo_path)
    assert result == "master"


def test_detect_base_branch_none(temp_dir):
    repo_path = temp_dir / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)

    with pytest.raises(ValueError, match="neither 'main' nor 'master'"):
        git_service.detect_base_branch(repo_path)


def test_create_branch(git_repo):
    git_service.create_branch("feature/test-task", git_repo, "main")

    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "feature/test-task"


def test_create_branch_already_exists(git_repo):
    git_service.create_branch("feature/test-task", git_repo, "main")

    current = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=git_repo,
        capture_output=True,
        text=True,
    ).stdout.strip()

    assert current == "feature/test-task"


def test_switch_branch(git_repo):
    git_service.switch_branch("main", git_repo)

    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=git_repo,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "main"


def test_merge_branch(git_repo):
    subprocess.run(
        ["git", "checkout", "-b", "feature/feature1"], cwd=git_repo, check=True
    )
    (git_repo / "file.txt").write_text("content")
    subprocess.run(["git", "add", "."], cwd=git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "add file"], cwd=git_repo, check=True)

    git_service.merge_branch("feature/feature1", "main", git_repo)

    content = (git_repo / "file.txt").read_text()
    assert content == "content"


def test_ensure_branch_creates_new(git_repo):
    result = git_service.ensure_branch("feature/new-branch", "main", git_repo)
    assert result is True

    branches = subprocess.run(
        ["git", "branch"], cwd=git_repo, capture_output=True, text=True
    ).stdout
    assert "feature/new-branch" in branches


def test_ensure_branch_existing(git_repo):
    subprocess.run(["git", "branch", "feature/existing"], cwd=git_repo, check=True)

    result = git_service.ensure_branch("feature/existing", "main", git_repo)
    assert result is False


def test_needs_stash_clean(git_repo):
    result = git_service.needs_stash(git_repo)
    assert result is False


def test_needs_stash_dirty(git_repo):
    (git_repo / "newfile.txt").write_text("changes")
    result = git_service.needs_stash(git_repo)
    assert result is True


def test_stash_and_pop(git_repo):
    (git_repo / "newfile.txt").write_text("changes")

    git_service.stash(git_repo, "test stash")

    assert not (git_repo / "newfile.txt").exists()

    subprocess.run(["git", "stash", "pop"], cwd=git_repo, check=True)
    assert (git_repo / "newfile.txt").read_text() == "changes"
