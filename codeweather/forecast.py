"""Maps Scores to named weather conditions and generates the forecast narrative."""

from __future__ import annotations

from dataclasses import dataclass

from codeweather.git_analysis import RawData
from codeweather.metrics import Scores


@dataclass
class WeatherCondition:
    name: str
    art_key: str
    temperature_label: str
    wind_label: str
    fog_label: str
    sunshine_label: str
    storm_label: str
    narrative: str


def generate(scores: Scores, raw: RawData) -> WeatherCondition:
    condition_name = _determine_condition(scores)
    return WeatherCondition(
        name=condition_name,
        art_key=condition_name,
        temperature_label=_temperature_label(scores.temperature),
        wind_label=_wind_label(scores.wind),
        fog_label=_fog_label(scores.fog),
        sunshine_label=_sunshine_label(scores.sunshine),
        storm_label=_storm_label(scores.storm_index),
        narrative=_narrative(scores, condition_name, raw),
    )


def _determine_condition(scores: Scores) -> str:
    if scores.storm_index >= 0.70:
        return "STORMY"
    if scores.temperature < 0.15:
        return "FROZEN"
    if scores.fog >= 0.70 and scores.sunshine < 0.30:
        return "FOGGY"
    if scores.sunshine >= 0.70 and scores.fog < 0.30:
        return "SUNNY"
    if scores.wind >= 0.70 and scores.storm_index >= 0.40:
        return "RAINY"
    if scores.temperature >= 0.60 and scores.wind >= 0.50:
        return "WINDY"
    if scores.fog >= 0.40:
        return "CLOUDY"
    return "PARTLY CLOUDY"


# --- Label formatters ---

def _temperature_label(score: float) -> str:
    if score < 0.15:
        return "12 F   (Frozen)"
    if score < 0.30:
        return "38 F   (Cold)"
    if score < 0.50:
        return "57 F   (Cool)"
    if score < 0.70:
        return "72 F   (Active)"
    if score < 0.85:
        return "88 F   (Hot)"
    return "102 F  (Scorching)"


def _wind_label(score: float) -> str:
    if score < 0.15:
        return "< 1 mph   (Calm)"
    if score < 0.35:
        return "8 mph     (Breeze)"
    if score < 0.55:
        return "18 mph    (Breezy)"
    if score < 0.75:
        return "32 mph    (Windy)"
    return "55+ mph   (Gale)"


def _fog_label(score: float) -> str:
    if score < 0.20:
        return "Clear"
    if score < 0.45:
        return "Hazy"
    if score < 0.70:
        return "Foggy"
    return "Dense Fog"


def _sunshine_label(score: float) -> str:
    pct = int(score * 100)
    if pct == 0:
        return "0%     (No tests found)"
    if pct < 10:
        return f"{pct}%     (Overcast)"
    if pct < 30:
        return f"{pct}%    (Cloudy)"
    if pct < 60:
        return f"{pct}%    (Partly Sunny)"
    return f"{pct}%    (Sunny)"


def _storm_label(score: float) -> str:
    if score < 0.30:
        return "None"
    if score < 0.50:
        return "Watch"
    if score < 0.70:
        return "Warning"
    return "!! SEVERE !!"


# --- Narrative assembly ---

_OPENINGS = {
    "STORMY":        "Severe conditions detected across the repository.",
    "FROZEN":        "Activity has come to a near standstill - the codebase is in deep freeze.",
    "FOGGY":         "Visibility is poor. Navigating this codebase requires patience and a good map.",
    "SUNNY":         "Clear skies and strong foundations across the board.",
    "RAINY":         "Persistent headwinds ahead - expect a bumpy ride.",
    "WINDY":         "High velocity detected. The codebase is moving fast.",
    "CLOUDY":        "Overcast conditions with pockets of uncertainty.",
    "PARTLY CLOUDY": "Mixed conditions with room for improvement.",
}

_TEMP_SENTENCES = {
    "frozen": "No commits have landed in quite some time; the codebase may be in maintenance mode or quietly abandoned.",
    "cold":   "Commit activity is light. Development appears to be winding down or in a quiet phase.",
    "cool":   "A moderate pace of commits keeps things moving, though acceleration would be welcome.",
    "active": "Healthy commit frequency signals an engaged team keeping things fresh.",
    "hot":    "High commit volume - the team is shipping fast and iterating quickly.",
    "scorch": "Commit rate is extremely high. Ensure code review quality keeps pace with the velocity.",
}

_FOG_SENTENCES = {
    "clear":    "The TODO count is low and the path ahead looks clean.",
    "hazy":     "A handful of TODO and FIXME markers are floating around - worth scheduling a cleanup sprint.",
    "foggy":    "A growing fog of unresolved TODOs is reducing visibility. Consider a dedicated debt-reduction day.",
    "dense":    "Dense fog of technical debt detected. The sheer volume of TODO/FIXME/HACK markers signals serious deferred work.",
}

_SUNSHINE_SENTENCES = {
    "none":    "No test files were detected. Flying without instruments is thrilling, but dangerous.",
    "low":     "Test coverage is sparse. Adding a few well-placed tests would clear things up considerably.",
    "medium":  "Test coverage is moderate - a solid foundation, but there is room to let more sunshine in.",
    "high":    "Strong test coverage is keeping this codebase well-lit and navigable.",
}

_OUTROS = {
    "none":    "Overall, conditions are manageable. Stay the course.",
    "watch":   "Monitor the situation - the fix-to-feature ratio is climbing.",
    "warning": "Conditions are deteriorating. Prioritize stabilization before adding new features.",
    "severe":  "Batten down the hatches. The repo needs serious attention before new feature work resumes.",
}


def _narrative(scores: Scores, condition: str, raw: RawData) -> str:
    opening = _OPENINGS[condition]

    if scores.temperature < 0.15:
        temp_key = "frozen"
    elif scores.temperature < 0.30:
        temp_key = "cold"
    elif scores.temperature < 0.50:
        temp_key = "cool"
    elif scores.temperature < 0.70:
        temp_key = "active"
    elif scores.temperature < 0.85:
        temp_key = "hot"
    else:
        temp_key = "scorch"

    if scores.fog < 0.20:
        fog_key = "clear"
    elif scores.fog < 0.45:
        fog_key = "hazy"
    elif scores.fog < 0.70:
        fog_key = "foggy"
    else:
        fog_key = "dense"

    if scores.sunshine == 0.0:
        sun_key = "none"
    elif scores.sunshine < 0.10:
        sun_key = "low"
    elif scores.sunshine < 0.60:
        sun_key = "medium"
    else:
        sun_key = "high"

    if scores.storm_index < 0.30:
        storm_key = "none"
    elif scores.storm_index < 0.50:
        storm_key = "watch"
    elif scores.storm_index < 0.70:
        storm_key = "warning"
    else:
        storm_key = "severe"

    parts = [
        opening,
        _TEMP_SENTENCES[temp_key],
        _FOG_SENTENCES[fog_key],
        _SUNSHINE_SENTENCES[sun_key],
        _OUTROS[storm_key],
    ]
    return " ".join(parts)
