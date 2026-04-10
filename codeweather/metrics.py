"""Pure functions: RawData -> normalized Scores in [0.0, 1.0]."""

from __future__ import annotations

import math
from dataclasses import dataclass

from codeweather.git_analysis import RawData

# Calibration constants
TEMP_MAX = 60       # commits/30d that = score 1.0
WIND_MAX = 5000     # lines changed/30d that = score 1.0
FOG_MAX = 5.0       # TODOs-per-file that = score 1.0
STORM_MAX = 0.5     # fix-commit-ratio that = score 1.0


@dataclass
class Scores:
    temperature: float   # 0.0 = frozen, 1.0 = scorching
    fog: float           # 0.0 = clear,  1.0 = dense fog
    sunshine: float      # 0.0 = overcast, 1.0 = blazing
    wind: float          # 0.0 = calm,   1.0 = gale
    storm_index: float   # 0.0 = clear,  1.0 = severe


def compute(raw: RawData) -> Scores:
    return Scores(
        temperature=_temperature_score(raw.commit_count_30d),
        fog=_fog_score(raw.todo_count, raw.total_files),
        sunshine=_sunshine_score(raw.test_files, raw.total_files),
        wind=_wind_score(raw.lines_changed_30d),
        storm_index=_storm_score(raw.fix_commit_count, raw.commit_count_30d),
    )


def _temperature_score(commit_count: int) -> float:
    return _clamp(math.log1p(commit_count) / math.log1p(TEMP_MAX), 0.0, 1.0)


def _fog_score(todo_count: int, total_files: int) -> float:
    todos_per_file = todo_count / max(total_files, 1)
    return _clamp(todos_per_file / FOG_MAX, 0.0, 1.0)


def _sunshine_score(test_files: int, total_files: int) -> float:
    return _clamp(test_files / max(total_files, 1), 0.0, 1.0)


def _wind_score(lines_changed: int) -> float:
    return _clamp(math.log1p(lines_changed) / math.log1p(WIND_MAX), 0.0, 1.0)


def _storm_score(fix_count: int, commit_count: int) -> float:
    fix_ratio = fix_count / max(commit_count, 1)
    return _clamp(fix_ratio / STORM_MAX, 0.0, 1.0)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
