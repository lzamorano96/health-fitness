#!/usr/bin/env python3
"""
weekly_summary.py — Print a weekly nutrition summary from daily logs.

Usage:
  python scripts/weekly_summary.py             # Current ISO week
  python scripts/weekly_summary.py --week 2026-W13
  python scripts/weekly_summary.py --month 2026-03

Output: Formatted summary table with per-day and weekly-average macros vs targets.
"""

import json
import sys
import re
import math
import argparse
from datetime import date, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent
LOGS_DIR = PLUGIN_ROOT / "data" / "logs"
TARGETS_FILE = PLUGIN_ROOT / "data" / "targets.json"

WEEK_PATTERN = re.compile(r"^\d{4}-W\d{2}$")
MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")

_DEFAULT_TARGETS = {"daily_calories": 2200, "macros": {"protein_g": 165, "carbs_g": 220, "fat_g": 70}}


def validate_week(week_str: str) -> str:
    """Validate ISO week format. Exits on bad input."""
    if not WEEK_PATTERN.match(week_str):
        print(f"  Error: Invalid week format '{week_str}'. Expected YYYY-WNN (e.g., 2026-W13).")
        sys.exit(1)
    _, wn = week_str.split("-W")
    if not (1 <= int(wn) <= 53):
        print(f"  Error: Week number {wn} out of range (1–53).")
        sys.exit(1)
    return week_str


def validate_month(month_str: str) -> str:
    """Validate month format YYYY-MM. Exits on bad input."""
    if not MONTH_PATTERN.match(month_str):
        print(f"  Error: Invalid month format '{month_str}'. Expected YYYY-MM (e.g., 2026-03).")
        sys.exit(1)
    _, m = month_str.split("-")
    if not (1 <= int(m) <= 12):
        print(f"  Error: Month {m} out of range (01–12).")
        sys.exit(1)
    return month_str


def get_week_dates(week_str: str) -> list[date]:
    """Return Monday–Sunday dates for an ISO week string like '2026-W13'."""
    try:
        year, week = week_str.split("-W")
        monday = date.fromisocalendar(int(year), int(week), 1)
        return [monday + timedelta(days=i) for i in range(7)]
    except (ValueError, OverflowError) as e:
        print(f"  Error: Cannot parse week '{week_str}': {e}")
        sys.exit(1)


def get_month_dates(month_str: str) -> list[date]:
    """Return all dates in a month string like '2026-03'."""
    try:
        year, month = map(int, month_str.split("-"))
        result = []
        d = date(year, month, 1)
        while d.month == month:
            result.append(d)
            d += timedelta(days=1)
        return result
    except (ValueError, OverflowError) as e:
        print(f"  Error: Cannot parse month '{month_str}': {e}")
        sys.exit(1)


def load_log(log_date: date) -> dict | None:
    log_file = LOGS_DIR / f"{log_date}.json"
    if not log_file.exists():
        return None
    try:
        with open(log_file) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"  Warning: {log_file.name} has unexpected format. Skipping.")
            return None
        # Ensure totals key exists
        if "totals" not in data or not isinstance(data.get("totals"), dict):
            data["totals"] = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
        return data
    except json.JSONDecodeError:
        print(f"  Warning: {log_file.name} contains invalid JSON. Skipping.")
        return None
    except (PermissionError, OSError):
        print(f"  Warning: Cannot read {log_file.name}. Skipping.")
        return None


def load_targets() -> dict:
    """Load targets with validation. Zero/negative values fall back to defaults."""
    data = _DEFAULT_TARGETS
    if TARGETS_FILE.exists():
        try:
            with open(TARGETS_FILE) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                data = _DEFAULT_TARGETS
        except (json.JSONDecodeError, PermissionError, OSError):
            print("  Warning: Cannot read targets file. Using defaults.")
            data = _DEFAULT_TARGETS

    # Ensure required keys with safe defaults
    if not isinstance(data.get("daily_calories"), (int, float)) or data["daily_calories"] <= 0:
        data["daily_calories"] = _DEFAULT_TARGETS["daily_calories"]
    if not isinstance(data.get("macros"), dict):
        data["macros"] = _DEFAULT_TARGETS["macros"]
    for key in ("protein_g", "carbs_g", "fat_g"):
        val = data["macros"].get(key)
        if not isinstance(val, (int, float)) or val <= 0:
            data["macros"][key] = _DEFAULT_TARGETS["macros"][key]
    return data


def safe_int(val, default: int = 0) -> int:
    """Coerce a value to int safely. Handles None, strings, NaN, and infinity."""
    if val is None:
        return default
    if isinstance(val, float):
        if math.isnan(val) or math.isinf(val):
            return default
        return int(val)
    if isinstance(val, int):
        return val
    # Try to parse string numbers
    if isinstance(val, str):
        try:
            return int(float(val))
        except (ValueError, OverflowError):
            return default
    return default


def status_label(actual_cal: int, target_cal: int) -> str:
    if actual_cal == 0:
        return "No data"
    if target_cal <= 0:
        return "—"  # cannot compute status without a valid target
    pct = actual_cal / target_cal
    if pct >= 0.95 and pct <= 1.05:
        return "✓ On target"
    elif pct < 0.85:
        return "↓↓ Very low"
    elif pct < 0.95:
        return "↓ Low"
    elif pct > 1.15:
        return "↑↑ Very high"
    else:
        return "↑ High"


def print_week_summary(dates: list[date], week_label: str):
    if not dates:
        print(f"\n  No dates to display for {week_label}.")
        return

    targets = load_targets()
    cal_t = targets["daily_calories"]
    p_t = targets["macros"]["protein_g"]
    c_t = targets["macros"]["carbs_g"]
    f_t = targets["macros"]["fat_g"]

    header = f"WEEKLY NUTRITION DASHBOARD — {week_label}"
    print(f"\n{'━'*60}")
    print(f"  {header}")
    print(f"  {dates[0]} → {dates[-1]}")
    print(f"{'━'*60}")

    print(f"\n  {'Day':<12} {'Calories':>10} {'Protein':>10} {'Carbs':>10} {'Fat':>8}  Status")
    print(f"  {'─'*12} {'─'*10} {'─'*10} {'─'*10} {'─'*8}  {'─'*14}")

    logged_days = 0
    total_cal, total_p, total_c, total_f = 0, 0, 0, 0
    on_target = 0

    for d in dates:
        day_name = d.strftime("%A")
        log = load_log(d)
        if log:
            t = log.get("totals", {})
            cal = safe_int(t.get("calories", 0))
            p = safe_int(t.get("protein_g", 0))
            c = safe_int(t.get("carbs_g", 0))
            f = safe_int(t.get("fat_g", 0))
            status = status_label(cal, cal_t)
            print(f"  {day_name:<12} {cal:>7,} kcal {p:>7}g    {c:>7}g    {f:>5}g  {status}")
            total_cal += cal
            total_p += p
            total_c += c
            total_f += f
            logged_days += 1
            if "✓" in status:
                on_target += 1
        else:
            print(f"  {day_name:<12} {'—':>10} {'—':>10} {'—':>10} {'—':>8}  No data")

    if logged_days == 0:
        print("\n  No logs found for this week.")
        return

    avg_cal = total_cal // logged_days
    avg_p = total_p // logged_days
    avg_c = total_c // logged_days
    avg_f = total_f // logged_days

    # Safe percentage: guard against zero targets (load_targets validates, but belt-and-suspenders)
    def pct(actual: int, target: int) -> str:
        if target <= 0:
            return "—"
        return f"{actual / target * 100:.0f}%"

    print(f"\n  {'─'*60}")
    print(f"  WEEKLY SUMMARY ({logged_days} days logged)")
    print(f"  Avg calories: {avg_cal:,} / {cal_t:,} kcal  "
          f"({avg_cal - cal_t:+} avg)")
    print(f"  Avg protein:  {avg_p}g / {p_t}g  ({pct(avg_p, p_t)})")
    print(f"  Avg carbs:    {avg_c}g / {c_t}g  ({pct(avg_c, c_t)})")
    print(f"  Avg fat:      {avg_f}g / {f_t}g  ({pct(avg_f, f_t)})")
    print(f"  Days on target: {on_target} / {logged_days}")
    print(f"{'━'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Print weekly nutrition summary.")
    parser.add_argument("--week", default=None, help="ISO week (e.g., 2026-W13)")
    parser.add_argument("--month", default=None, help="Month (e.g., 2026-03)")
    args = parser.parse_args()

    if args.month:
        month_str = validate_month(args.month)
        dates = get_month_dates(month_str)
        if not dates:
            print(f"  No dates found for month {month_str}.")
            sys.exit(0)
        # Split into weeks for display
        week_map = {}
        for d in dates:
            iso = d.isocalendar()
            wk = f"{iso[0]}-W{iso[1]:02d}"
            week_map.setdefault(wk, []).append(d)
        for wk, wk_dates in sorted(week_map.items()):
            print_week_summary(wk_dates, wk)
    else:
        if args.week:
            week_str = validate_week(args.week)
        else:
            today = date.today()
            iso = today.isocalendar()
            week_str = f"{iso[0]}-W{iso[1]:02d}"
        dates = get_week_dates(week_str)
        print_week_summary(dates, week_str)


if __name__ == "__main__":
    main()
