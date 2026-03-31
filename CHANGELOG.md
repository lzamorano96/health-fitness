# Changelog

All notable changes to `health-fitness` are documented in this file.

This project adheres to [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
and [Semantic Versioning 2.0.0](https://semver.org/).

---

## Change Types Reference

| Tag | Meaning |
|-----|---------|
| `Added` | New skill, feature, script, or agent |
| `Changed` | Modification to existing behavior |
| `Deprecated` | Feature marked for removal in a future MAJOR release |
| `Removed` | Feature removed (always a MAJOR bump if user-facing) |
| `Fixed` | Defect corrected |
| `Security` | Vulnerability patched |
| `Data` | Schema change or data file update (note BREAKING if schema changes) |

---

## [Unreleased]

> Changes on `develop` not yet tagged as a release.

---

## [0.1.1] — 2026-03-30

### Fixed

- `log_meal.py`: Replaced substring fuzzy match with whole-word boundary
  matching to prevent false positives (e.g., "michigan salad" no longer
  matches "chicken"). Added entry name sanitization — names are capped at
  120 characters and control characters are stripped before writing to log.
- `export_grocery_list.py`: `format_quantity()` now guards against `NaN`,
  `inf`, and negative float values. Added validation to reject empty or
  whitespace-only `--output` paths before attempting a write.
- `weekly_summary.py`: `print_week_summary()` now returns cleanly on an
  empty dates list instead of crashing with `IndexError`. `safe_int()`
  expanded to handle `None`, `NaN`, `inf`, and string-encoded numbers.
- `calorie-tracker` skill: Added Error Handling section covering corrupt
  log files, deletion on empty log, empty input, and non-numeric macros.
- `meal-prep-planner` skill: Added Error Handling section covering missing
  targets, corrupt meal library, and null macro values.
- `meal-plan-generator` agent: Added Error Handling section covering
  missing targets, null values, corrupt library, missing `last_used`
  field, and write failures.

---

## [0.1.0] — 2026-03-27

### Added

- **meal-prep-planner skill**: Generates a 7-day macro-accurate meal plan with
  protein rotation, variety enforcement against the meal library, and prep-friendly
  meal tagging. Exports ingredient list directly to `heb-list-builder`.
- **calorie-tracker skill**: Logs daily food intake from natural language input.
  Maintains running calorie and macro totals per meal slot. Supports edit and
  delete operations. Data stored in `data/logs/YYYY-MM-DD.json`.
- **macro-targets skill**: Calculates personalized TDEE using Mifflin-St Jeor BMR
  formula with activity multipliers. Supports cut / maintain / lean bulk goal
  presets. Writes to `data/targets.json` as the plugin-wide source of truth.
- **fitness-dashboard skill**: Aggregates weekly log files into a formatted summary
  table with per-day macro breakdown, on-target counts, and data-backed insights.
  Exports to `data/reports/YYYY-WNN-report.md`.
- **meal-plan-generator agent**: Autonomous end-to-end meal plan generation. Reads
  targets, cross-references meal library for variety, validates macro compliance per
  day, saves plan, and offers HEB export — no interactive prompts required.
- **`scripts/log_meal.py`**: CLI utility for terminal-based meal logging. Supports
  comma-separated multi-item entries, date targeting, and `--show` display mode.
- **`scripts/export_grocery_list.py`**: Extracts and quantity-merges all ingredients
  from a weekly meal plan JSON. Outputs plain-text list for HEB integration.
- **`scripts/weekly_summary.py`**: Prints a formatted weekly or monthly nutrition
  summary table from daily log files vs. targets.
- **`data/targets.json`**: Seed configuration file with default 2,200 kcal /
  165g P / 220g C / 74g F targets. Overwritten on first `macro-targets` run.
- **`data/meals-library.json`**: Empty meal library seed. Populated automatically
  by `meal-prep-planner` on first plan generation.

### Security / Hardening

- All JSON file reads protected against `JSONDecodeError`, `PermissionError`,
  and `OSError` with user-facing error messages that expose no system paths.
- `save_log()` uses atomic writes (temp file → `os.replace`) to prevent
  data corruption on interrupted writes.
- All CLI date, week, and month arguments validated with regex + calendar
  verification before file path construction.
- Division-by-zero guards on all percentage calculations; zero/negative
  target values fall back to hardcoded defaults.

---

## Version Bump Decision Log

| Version | Trigger |
|---------|---------|
| `0.2.0` | Add new skill or agent |
| `0.1.x` | Bug fix, error handling improvement, documentation update |
| `1.0.0` | Data schemas stable, CLI interface finalized, 4+ weeks production use |
| `2.0.0` | Breaking change to `targets.json` or `logs/` schema |

---

[Unreleased]: https://github.com/lzamorano96/health-fitness/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/lzamorano96/health-fitness/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/lzamorano96/health-fitness/releases/tag/v0.1.0
