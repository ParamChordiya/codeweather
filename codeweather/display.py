"""Rich-based terminal rendering. All visual output decisions live here."""

from __future__ import annotations

from datetime import datetime, timezone

from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codeweather.art import ART
from codeweather.forecast import WeatherCondition
from codeweather.git_analysis import RawData

CONSOLE = Console()


def render(condition: WeatherCondition, raw: RawData) -> None:
    _render_header(raw.repo_name, raw.branch_name)
    _render_art_and_stats(condition)
    _render_narrative(condition.narrative)
    _render_footer(raw)


def _render_header(repo_name: str, branch_name: str) -> None:
    today = datetime.now(tz=timezone.utc).strftime("%B %d, %Y")
    title = Text(f" CODEWEATHER REPORT ", style="bold white on blue")
    subtitle = Text(
        f"repo: {repo_name}  |  branch: {branch_name}  |  {today}",
        style="dim",
        justify="center",
    )
    CONSOLE.print()
    CONSOLE.print(title, justify="center")
    CONSOLE.print(subtitle, justify="center")
    CONSOLE.print()


def _render_art_and_stats(condition: WeatherCondition) -> None:
    art_text = ART.get(condition.art_key, ART["PARTLY CLOUDY"])

    art_panel = Panel(
        Text(art_text, style="cyan"),
        title=f"[bold cyan]{condition.name}[/bold cyan]",
        border_style="cyan",
        expand=False,
        padding=(0, 1),
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 1))
    stats_table.add_column("metric", style="dim", no_wrap=True)
    stats_table.add_column("value", no_wrap=True)

    temp_style = _temp_style(condition.temperature_label)
    fog_style = _fog_style(condition.fog_label)
    sun_style = _sun_style(condition.sunshine_label)
    wind_style = _wind_style(condition.wind_label)
    storm_style = _storm_style(condition.storm_label)

    stats_table.add_row("Temperature", Text(condition.temperature_label, style=temp_style))
    stats_table.add_row("Wind", Text(condition.wind_label, style=wind_style))
    stats_table.add_row("Fog / Tech Debt", Text(condition.fog_label, style=fog_style))
    stats_table.add_row("Sunshine / Tests", Text(condition.sunshine_label, style=sun_style))
    stats_table.add_row("Storm Watch", Text(condition.storm_label, style=storm_style))

    stats_panel = Panel(
        stats_table,
        title="[bold]Metrics[/bold]",
        border_style="white",
        expand=False,
        padding=(0, 1),
    )

    CONSOLE.print(Columns([art_panel, stats_panel], equal=False, expand=False))
    CONSOLE.print()


def _render_narrative(text: str) -> None:
    CONSOLE.print(
        Panel(
            Text(text, style="italic", justify="left"),
            title="[bold blue]Forecast[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    CONSOLE.print()


def _render_footer(raw: RawData) -> None:
    CONSOLE.print(
        f"  [dim]Analyzed {raw.commit_count_30d} commit(s) over the last 30 days.[/dim]"
    )
    if raw.first_commit_date:
        age_days = (datetime.now(tz=timezone.utc) - raw.first_commit_date).days
        CONSOLE.print(f"  [dim]Repository age: {age_days} days.[/dim]")
    for flag in raw.error_flags:
        CONSOLE.print(f"  [dim yellow]Note: {flag}[/dim yellow]")
    CONSOLE.print()


# --- Style helpers ---

def _temp_style(label: str) -> str:
    if "Frozen" in label or "Cold" in label:
        return "bold blue"
    if "Hot" in label or "Scorching" in label:
        return "bold red"
    return "default"


def _fog_style(label: str) -> str:
    if label == "Clear":
        return "green"
    if label == "Dense Fog":
        return "bold yellow"
    return "yellow"


def _sun_style(label: str) -> str:
    if "No tests" in label:
        return "bold red"
    if "Overcast" in label or "Cloudy" in label:
        return "dim"
    return "bright_yellow"


def _wind_style(label: str) -> str:
    if "Gale" in label or "Windy" in label:
        return "magenta"
    return "default"


def _storm_style(label: str) -> str:
    if label == "None":
        return "green"
    if label == "Watch":
        return "yellow"
    if label == "Warning":
        return "bold red"
    if "SEVERE" in label:
        return "bold red blink"
    return "default"
