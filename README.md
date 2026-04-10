# codeweather

A weather forecast for your codebase health.

Point `codeweather` at any git repository and get a fun, accurate "weather report" based on real code metrics — commit activity, technical debt, test coverage, and churn. No API keys, no config, no nonsense.

```
                           CODEWEATHER REPORT
         repo: myproject  |  branch: main  |  April 10, 2026

╭────── CLOUDY ──────╮ ╭──────────────────── Metrics ────────────────────╮
│        ___         │ │  Temperature       57 F   (Cool)               │
│     .-'   '-.      │ │  Wind              8 mph     (Breeze)           │
│   .'  ___    '.    │ │  Fog / Tech Debt   Hazy                        │
│  (  .'   '.   )    │ │  Sunshine / Tests  23%    (Cloudy)             │
│   '.       .'      │ │  Storm Watch       None                        │
│     '-----'        │ ╰─────────────────────────────────────────────────╯
╰────────────────────╯

╭────────────────────────── Forecast ───────────────────────────╮
│  Overcast conditions with pockets of uncertainty. A moderate  │
│  pace of commits keeps things moving. A handful of TODO and   │
│  FIXME markers are floating around - worth scheduling a       │
│  cleanup sprint. Test coverage is sparse...                   │
╰───────────────────────────────────────────────────────────────╯
```

## Installation

```bash
pip install codeweather
```

Or install from source:

```bash
git clone https://github.com/ParamChordiya/codeweather
cd codeweather
pip install -e .
```

## Usage

```bash
# Forecast for the current directory
codeweather

# Forecast for a specific repo
codeweather /path/to/your/repo

# Or run as a module
python -m codeweather /path/to/your/repo
```

## Weather Conditions

| Condition | Trigger |
|-----------|---------|
| **STORMY** | High ratio of fix/bug/hotfix commits (>=70% of threshold) |
| **FROZEN** | Near-zero commits in the last 30 days |
| **FOGGY** | High TODO/FIXME density + low test coverage |
| **SUNNY** | Strong test coverage + clean codebase |
| **RAINY** | High churn + moderate storm index |
| **WINDY** | High commit velocity + high churn |
| **CLOUDY** | Elevated technical debt fog |
| **PARTLY CLOUDY** | Mixed signals, typical working repo |

## Metrics Explained

| Metric | What it measures | Weather analogy |
|--------|-----------------|-----------------|
| **Temperature** | Commits in the last 30 days (log scale) | Project activity level |
| **Fog** | TODO/FIXME/HACK density per tracked file | Technical debt visibility |
| **Sunshine** | Ratio of test files to total files | Code confidence |
| **Wind** | Lines changed in the last 30 days (log scale) | Code churn / volatility |
| **Storm Watch** | Ratio of fix/bug/hotfix commits | Firefighting mode |

All scores use a log scale where appropriate, so both small hobby projects and large monorepos get meaningful readings.

## Requirements

- Python 3.9+
- A git repository with at least one commit
- Dependencies: `gitpython`, `rich`

## How It Works

1. **Collect** — reads your git history, tracked files, and `git grep` output (no filesystem walk, only tracked files are analyzed)
2. **Score** — converts raw numbers to normalized `[0.0, 1.0]` scores using log scales
3. **Forecast** — maps scores to weather conditions via a priority cascade
4. **Display** — renders the ASCII art, metrics table, and narrative paragraph with `rich`

The narrative is fully deterministic — running `codeweather` twice on the same repo gives the same output.

## License

MIT
