import subprocess

from branchflow.project_service import create_project
from branchflow.task_service import (
    create_task,
    get_current_task,
    merge_master_to_branches,
    change_current_task,
)


def run_git(cwd, *args):
    result = subprocess.run(
        ["git"] + list(args), cwd=cwd, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr}")
    return result


def get_current_branch(repo_path):
    result = run_git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    return result.stdout.strip()


def list_branches(repo_path):
    result = run_git(repo_path, "branch", "--format=%(refname:short)")
    return [b.strip() for b in result.stdout.split("\n") if b.strip()]


class TestIntegrationWithRemote:
    def test_full_workflow_with_remote(self, temp_config_file, tmp_path):
        remote_path = tmp_path / "remote.git"
        run_git(tmp_path, "init", "--bare", str(remote_path))

        local_repo = tmp_path / "project"
        local_repo.mkdir()
        run_git(local_repo, "init")
        run_git(local_repo, "config", "user.email", "test@test.com")
        run_git(local_repo, "config", "user.name", "Test User")
        run_git(local_repo, "remote", "add", "origin", str(remote_path))

        (local_repo / "README.md").write_text("# Project\n")
        run_git(local_repo, "add", ".")
        run_git(local_repo, "commit", "-m", "initial commit")
        run_git(local_repo, "push", "-u", "origin", "main")

        project = create_project("MyProject", str(local_repo))
        assert project.name == "MyProject"

        create_task("PD-1234", "Test task", ["MyProject"], None)

        current = get_current_task()
        assert current is not None
        assert current.name == "PD-1234"
        assert "MyProject" in current.branches

        branch_name = current.branches["MyProject"].branch_name
        assert branch_name == "feature/PD-1234"

        current_branch = get_current_branch(local_repo)
        assert current_branch == "feature/PD-1234"

        branches = list_branches(local_repo)
        assert "feature/PD-1234" in branches

        run_git(local_repo, "checkout", "main")
        (local_repo / "new_feature.py").write_text("print('new feature')")
        run_git(local_repo, "add", ".")
        run_git(local_repo, "commit", "-m", "add new feature")
        run_git(local_repo, "push", "origin", "main")

        run_git(local_repo, "checkout", "feature/PD-1234")
        merge_master_to_branches()

    def test_workflow_with_parent_task(self, temp_config_file, tmp_path):
        local_repo = tmp_path / "project"
        local_repo.mkdir()
        run_git(local_repo, "init")
        run_git(local_repo, "config", "user.email", "test@test.com")
        run_git(local_repo, "config", "user.name", "Test User")

        (local_repo / "README.md").write_text("# Project\n")
        run_git(local_repo, "add", ".")
        run_git(local_repo, "commit", "-m", "initial")

        create_project("MyProject", str(local_repo))

        create_task("PD-1000", "Parent task", ["MyProject"], None)

        parent = get_current_task()
        assert parent.name == "PD-1000"
        assert "feature/PD-1000" in list_branches(local_repo)

        create_task("PD-2000", "Child task", ["MyProject"], "PD-1000")

        child = get_current_task()
        assert child.name == "PD-2000"
        assert child.parent == "PD-1000"

        branches = list_branches(local_repo)
        assert "feature/PD-1000" in branches
        assert "feature/PD-2000" in branches

        current_branch = get_current_branch(local_repo)
        assert current_branch == "feature/PD-2000"

    def test_switch_between_tasks(self, temp_config_file, tmp_path):
        local_repo = tmp_path / "project"
        local_repo.mkdir()
        run_git(local_repo, "init")
        run_git(local_repo, "config", "user.email", "test@test.com")
        run_git(local_repo, "config", "user.name", "Test User")

        (local_repo / "README.md").write_text("# Project\n")
        run_git(local_repo, "add", ".")
        run_git(local_repo, "commit", "-m", "initial")

        create_project("MyProject", str(local_repo))

        create_task("PD-1000", "Task 1", ["MyProject"], None)
        create_task("PD-2000", "Task 2", ["MyProject"], None)

        run_git(local_repo, "checkout", "main")

        change_current_task("PD-1000")
        assert get_current_branch(local_repo) == "feature/PD-1000"

        change_current_task("PD-2000")
        assert get_current_branch(local_repo) == "feature/PD-2000"

    def test_refresh_with_multiple_projects(self, temp_config_file, tmp_path):
        project1_dir = tmp_path / "project1"
        project2_dir = tmp_path / "project2"

        for project_dir in [project1_dir, project2_dir]:
            project_dir.mkdir()
            run_git(project_dir, "init")
            run_git(project_dir, "config", "user.email", "test@test.com")
            run_git(project_dir, "config", "user.name", "Test User")

            (project_dir / "README.md").write_text("# Project\n")
            run_git(project_dir, "add", ".")
            run_git(project_dir, "commit", "-m", "initial")

        create_project("Project1", str(project1_dir))
        create_project("Project2", str(project2_dir))

        create_task("PD-1234", "Test task", ["Project1", "Project2"], None)

        current = get_current_task()
        assert len(current.projects) == 2

        for project_dir in [project1_dir, project2_dir]:
            run_git(project_dir, "checkout", "main")
            (project_dir / "update.txt").write_text("update")
            run_git(project_dir, "add", ".")
            run_git(project_dir, "commit", "-m", "update")

        for project_dir in [project1_dir, project2_dir]:
            run_git(project_dir, "checkout", "feature/PD-1234")
            merge_master_to_branches()

            assert (project_dir / "update.txt").exists()
            assert (project_dir / "update.txt").read_text() == "update"
