"""CLI entry point."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

CONSOLE = Console(stderr=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="codeweather",
        description="A weather forecast for your codebase health.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    args = parser.parse_args()

    try:
        from git.exc import InvalidGitRepositoryError, NoSuchPathError

        from codeweather import git_analysis, metrics, forecast, display

        raw = git_analysis.collect(args.path)
        scores = metrics.compute(raw)
        condition = forecast.generate(scores, raw)
        display.render(condition, raw)

    except Exception as exc:
        # Import here to avoid circular import issues at top level
        try:
            from git.exc import InvalidGitRepositoryError, NoSuchPathError
            if isinstance(exc, InvalidGitRepositoryError):
                CONSOLE.print(f"[bold red]Error:[/bold red] '{args.path}' is not a git repository.")
                sys.exit(1)
            if isinstance(exc, NoSuchPathError):
                CONSOLE.print(f"[bold red]Error:[/bold red] Path not found: '{args.path}'")
                sys.exit(1)
        except ImportError:
            pass
        CONSOLE.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(1)
