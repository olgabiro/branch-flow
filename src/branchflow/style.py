from rich import box
from rich.markup import escape
from rich.panel import Panel
from rich.style import Style
from rich.theme import Theme

rose_theme = Theme({
    "rose": Style(color="#f0a0a0"),
    "rose.bold": Style(color="#f0a0a0", bold=True),
    "rose.deep": Style(color="#d47878"),
    "rose.light": Style(color="#f5baba"),
    "text": Style(color="#e8d5d5"),
    "text.muted": Style(color="#8a7070"),
    "text.dim": Style(color="#634f4f"),
    "success": Style(color="#a8c9a8", bold=False),
    "warning": Style(color="#d4b878"),
    "error": Style(color="#d47878", bold=True),
    "border": Style(color="#3d2a2e"),
    "title": Style(color="#f0a0a0", bold=True),
    "subtitle": Style(color="#d4a0a0", italic=True),
    "muted": Style(color="#634f4f"),
})

STYLE = {
    "bg": "#1a1517",
    "surface": "#231d20",
    "surface2": "#2d2428",
    "surface3": "#382c31",
    "rose": "#f0a0a0",
    "primary": "#f0a0a0",
    "rose_light": "#f5baba",
    "rose_deep": "#d47878",
    "rose_dark": "#b85a5a",
    "text": "#e8d5d5",
    "text_muted": "#8a7070",
    "info": "#2d2428",
    "text_dim": "#634f4f",
    "success": "#a8c9a8",
    "warning": "#d4b878",
    "error": "#d47878",
    "border": "#3d2a2e",
}


def _panel(title, content, style=STYLE["primary"]):
    return Panel(
        content,
        title=f"[{style}]{escape(title)}[/]",
        border_style=style,
        box=box.ROUNDED,
        padding=(1, 2),
    )


def _badge(text, style=STYLE["primary"]):
    return f"[{style}]● {escape(text)}[/]"


def success(text):
    return f"[{STYLE['success']}]✓ {escape(text)}[/]"


def warning(text):
    return f"[{STYLE['warning']}]△ {escape(text)}[/]"


def error(text):
    return f"[{STYLE['error']}]✗ error:[/] {escape(text)}"


def _muted(text):
    return f"[{STYLE['muted']}]{escape(text)}[/]"


def info(text):
    return f"[{STYLE['info']}]● {escape(text)}[/]"


def _spinner(msg):
    """Run a git op with a spinner — simple synchronous wrapper."""
    return f"[{STYLE['muted']}]  {escape(msg)}[/]"


def _branch_label(branch, is_current=False):
    if is_current:
        return f"[{STYLE['primary']}]{escape(branch)}[/]"
    return f"[{STYLE['muted']}]{escape(branch)}[/]"
