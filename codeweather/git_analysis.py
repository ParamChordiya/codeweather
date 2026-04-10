"""Git repository data extraction. All gitpython usage lives here."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import git
from git.exc import GitCommandError, InvalidGitRepositoryError  # noqa: F401 (re-exported)


@dataclass
class RawData:
    commit_count_30d: int
    todo_count: int
    total_files: int
    test_files: int
    lines_changed_30d: int
    fix_commit_count: int
    repo_name: str
    branch_name: str
    first_commit_date: datetime | None
    error_flags: list[str] = field(default_factory=list)


TEST_PATTERNS = re.compile(
    r"(^|/)test_[^/]+\.py$"
    r"|(^|/)[^/]+_test\.py$"
    r"|(^|/)[^/]+\.spec\.(js|ts|jsx|tsx|mjs)$"
    r"|(^|/)[^/]+_spec\.rb$"
    r"|(^|/)[^/]+_test\.(go|rs)$"
    r"|(^|/)tests?/[^/]+\.(py|js|ts|rb|go|rs)$",
    re.IGNORECASE,
)

FIX_PATTERN = re.compile(r"\b(fix|bug|hotfix|patch|revert)\b", re.IGNORECASE)


def collect(path: str) -> RawData:
    repo = git.Repo(path, search_parent_directories=True)
    flags: list[str] = []

    repo_name = repo.working_dir.split("/")[-1] if repo.working_dir else "unknown"

    try:
        branch_name = repo.active_branch.name
    except TypeError:
        branch_name = repo.head.commit.hexsha[:7] if not repo.head.is_detached else "detached"

    commits_30d = _get_commits_30d(repo, flags)
    commit_count = len(commits_30d)
    fix_count = _fix_commit_count(commits_30d)
    total_files, test_file_count = _count_files(repo, flags)
    todo_count = _count_todos(repo, flags)
    lines_changed = _lines_changed_30d(repo, flags)
    first_commit_date = _first_commit_date(repo)

    return RawData(
        commit_count_30d=commit_count,
        todo_count=todo_count,
        total_files=total_files,
        test_files=test_file_count,
        lines_changed_30d=lines_changed,
        fix_commit_count=fix_count,
        repo_name=repo_name,
        branch_name=branch_name,
        first_commit_date=first_commit_date,
        error_flags=flags,
    )


def _get_commits_30d(repo: git.Repo, flags: list[str]) -> list[git.Commit]:
    try:
        commits = list(repo.iter_commits(since="30 days ago"))
        if not commits:
            flags.append("No commits found in the last 30 days")
        return commits
    except (GitCommandError, ValueError):
        flags.append("Could not read commit history")
        return []


def _fix_commit_count(commits: list[git.Commit]) -> int:
    return sum(1 for c in commits if FIX_PATTERN.search(c.message))


def _count_files(repo: git.Repo, flags: list[str]) -> tuple[int, int]:
    try:
        tracked = [entry for entry in repo.index.entries]
        paths = [e[0] for e in tracked]
        total = len(paths)
        test_count = sum(1 for p in paths if TEST_PATTERNS.search(p))
        return total, test_count
    except Exception:
        flags.append("Could not enumerate tracked files")
        return 0, 0


def _count_todos(repo: git.Repo, flags: list[str]) -> int:
    try:
        result = repo.git.grep(
            "--count", "--extended-regexp", "TODO|FIXME|HACK",
            "--", ".",
            with_extended_output=True,
        )
        # result is (status, stdout, stderr)
        stdout = result[1] if isinstance(result, tuple) else result
        total = 0
        for line in stdout.splitlines():
            parts = line.rsplit(":", 1)
            if len(parts) == 2:
                try:
                    total += int(parts[1])
                except ValueError:
                    pass
        return total
    except GitCommandError:
        # No matches found (exit code 1 from grep) or git grep unavailable
        return 0
    except Exception:
        flags.append("Could not count TODO/FIXME markers")
        return 0


def _lines_changed_30d(repo: git.Repo, flags: list[str]) -> int:
    try:
        commits_30d = list(repo.iter_commits(since="30 days ago"))
        if len(commits_30d) < 1:
            return 0
        # Find the oldest commit in the range
        oldest = commits_30d[-1]
        # Get parent of oldest commit if available
        if oldest.parents:
            base = oldest.parents[0].hexsha
        else:
            base = oldest.hexsha

        stat_output = repo.git.diff("--stat", base, "HEAD")
        # Parse final summary line: "X files changed, Y insertions(+), Z deletions(-)"
        summary_match = re.search(
            r"(\d+) insertion|(\d+) deletion",
            stat_output,
        )
        if not summary_match:
            return 0

        insertions = len(re.findall(r"(\d+) insertion", stat_output))
        deletions = len(re.findall(r"(\d+) deletion", stat_output))

        # Better: sum all insertion/deletion counts
        ins_counts = [int(m) for m in re.findall(r"(\d+) insertion", stat_output)]
        del_counts = [int(m) for m in re.findall(r"(\d+) deletion", stat_output)]
        return sum(ins_counts) + sum(del_counts)
    except GitCommandError:
        flags.append("Shallow clone detected - line change data unavailable")
        return 0
    except Exception:
        flags.append("Could not compute lines changed")
        return 0


def _first_commit_date(repo: git.Repo) -> datetime | None:
    try:
        commits = list(repo.iter_commits())
        if commits:
            ts = commits[-1].committed_date
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        return None
    except Exception:
        return None
