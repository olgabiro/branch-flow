from rich.console import Console

_task = {
    "name": "PD-1234",
    "description": "Fix that issue we've been ignoring for 5 years",
    "projects": ["GIS", "GPM", "ETB"],
    "branches": {
        "GIS": "feature/PD-1234",
        "GPM": "feature/PD-1234",
        "ETB": "feature/PD-1234",
    }
}

_sub_task = {
    "name": "PD-1444",
    "description": "Bugfix subtask",
    "parent": "PD-1234",
    "projects": ["GIS", "GPM", "ETB"],
    "branches": {}
}

projects = [
    {
        "name": "GIS",
        "directory": "~/dev/gis"
    },
    {
        "name": "GPM",
        "directory": "~/dev/gpm"
    },
    {
        "name": "ETB",
        "directory": "~/dev/etb"
    }
]

console = Console()


def print_projects():
    console.print("[bold green]Tracked Projects[/]")
    for project in projects:
        console.print(f"- [bold]{project['name']}[/] ({project['directory']})")


def print_tasks():
    console.print("[bold green]Tracked Tasks[/]")

    for t in [_task, _sub_task]:
        print_task(t)


def print_task(t=_task):
    console.print()
    console.print(f"[bold green]{t['name']}[/]: {t['description']}")
    console.print(f"[bold]Projects:[/] {', '.join(t['projects'])}")
    console.print("[bold]Branches:[/]")
    for project, branch in t['branches'].items():
        emoji = ":arrow_up_small:" if project == "GPM" else ":computer:"
        console.print(f"  * {project}: {branch} {emoji}")
    if t['branches'].items().__len__() == 0:
        console.print("  * No branches tracked")
