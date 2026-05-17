import subprocess
from pathlib import Path

from rich.console import Console
from rich.markup import escape

from branchflow.style import STYLE

console = Console()


def get_branch_name(task_name: str):
    return f"feature/{task_name}"


def feature_branch_name(task_name):
    return "feature/" + task_name.replace(" ", "-")


def create_branch(branch_name: str, project_path: Path, parent_branch_name: str):
    switch_branch(parent_branch_name, project_path)

    if not branch_exists(branch_name, project_path):
        result = subprocess.run(
            ["git", "branch", branch_name],
            cwd=project_path,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise ValueError(result.stderr)

    switch_branch(branch_name, project_path)


def branch_exists(name: str, project_path: Path):
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{name}"],
        cwd=project_path,
    )
    return result.returncode == 0


def switch_branch(branch: str, project_path: Path):
    _git_assert("checkout", branch, cwd=project_path)


def merge_branch(source_branch: str, target_branch: str, project_path: Path):
    switch_branch(target_branch, project_path)
    _git_assert("merge", source_branch, cwd=project_path)


def _git(*args, cwd=None):
    r = subprocess.run(["git"] + list(args), capture_output=True, text=True, cwd=cwd)
    return r


def _git_assert(*args, cwd=None):
    r = _git(*args, cwd=cwd)
    if r.returncode != 0:
        msg = r.stderr.strip() if r.stderr.strip() else r.stdout.strip()
        raise ValueError(escape(msg))
    return r


def detect_base_branch(project_dir):
    r = _git("rev-parse", "--verify", "main", cwd=project_dir)
    if r.returncode == 0:
        return "main"
    r = _git("rev-parse", "--verify", "master", cwd=project_dir)
    if r.returncode == 0:
        return "master"
    raise ValueError(f"neither 'main' nor 'master' found in {escape(str(project_dir))}")


def needs_stash(project_dir):
    r = _git("status", "--porcelain", cwd=project_dir)
    return bool(r.stdout.strip())


def stash(project_dir, msg=None):
    args = ["stash", "push", "--include-untracked"]
    if msg:
        args.extend(["-m", msg])
    return _git_assert(*args, cwd=project_dir)


def ensure_branch(branch, base, project_dir):
    r = _git("rev-parse", "--verify", branch, cwd=project_dir)
    if r.returncode == 0:
        return False
    _git_assert("checkout", "-b", branch, base, cwd=project_dir)
    return True
