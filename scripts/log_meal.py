#!/usr/bin/env python3
"""
log_meal.py — CLI utility for logging meals directly from the terminal.

Usage:
  python scripts/log_meal.py --meal "chicken breast 6oz" --slot lunch
  python scripts/log_meal.py --meal "oats 1 cup, banana 1 large" --slot breakfast
  python scripts/log_meal.py --show              # Show today's log
  python scripts/log_meal.py --date 2026-03-25   # Show specific date

Data is read from and written to data/logs/YYYY-MM-DD.json relative to the
plugin root. Macro values are looked up from a built-in reference table.
"""

import json
import sys
import os
import tempfile
import argparse
import re
from datetime import date, datetime
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent
DATA_DIR = PLUGIN_ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
TARGETS_FILE = DATA_DIR / "targets.json"

try:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    print("  Error: Cannot create logs directory. Check file permissions.")
    sys.exit(1)

# ── Date validation ──────────────────────────────────────────────────────────
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(date_str: str) -> str:
    """Validate that a string is a real YYYY-MM-DD date. Returns the string or exits."""
    if not DATE_PATTERN.match(date_str):
        print(f"  Error: Invalid date format '{date_str}'. Expected YYYY-MM-DD.")
        sys.exit(1)
    try:
        date.fromisoformat(date_str)
    except ValueError:
        print(f"  Error: '{date_str}' is not a valid calendar date.")
        sys.exit(1)
    return date_str


# ── Safe JSON helpers ────────────────────────────────────────────────────────
def safe_read_json(filepath: Path, fallback: dict | None = None) -> dict | None:
    """Read a JSON file with error handling. Returns fallback on any failure."""
    if not filepath.exists():
        return fallback
    try:
        with open(filepath) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"  Warning: {filepath.name} has unexpected format. Using defaults.")
            return fallback
        return data
    except json.JSONDecodeError:
        print(f"  Warning: {filepath.name} contains invalid JSON. Using defaults.")
        return fallback
    except PermissionError:
        print(f"  Error: Permission denied reading {filepath.name}.")
        return fallback
    except OSError as e:
        print(f"  Error: Could not read {filepath.name}: {e}")
        return fallback


def safe_write_json(filepath: Path, data: dict) -> bool:
    """Write JSON atomically: write to temp file, then rename. Returns True on success."""
    try:
        fd, tmp_path = tempfile.mkstemp(
            dir=filepath.parent, suffix=".tmp", prefix=".write_"
        )
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, filepath)
            return True
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except PermissionError:
        print(f"  Error: Permission denied writing {filepath.name}.")
        return False
    except OSError as e:
        print(f"  Error: Could not write {filepath.name}: {e}")
        return False

# ── Nutrition reference (subset) ─────────────────────────────────────────────
NUTRITION_DB = {
    "chicken breast 4oz": {"calories": 187, "protein_g": 35, "carbs_g": 0, "fat_g": 4},
    "chicken breast 6oz": {"calories": 280, "protein_g": 52, "carbs_g": 0, "fat_g": 6},
    "ground beef 4oz":    {"calories": 196, "protein_g": 28, "carbs_g": 0, "fat_g": 9},
    "salmon 4oz":         {"calories": 233, "protein_g": 25, "carbs_g": 0, "fat_g": 15},
    "eggs 2":             {"calories": 156, "protein_g": 12, "carbs_g": 2, "fat_g": 10},
    "oats 1 cup":         {"calories": 300, "protein_g": 10, "carbs_g": 54, "fat_g": 6},
    "brown rice 1 cup":   {"calories": 216, "protein_g": 5,  "carbs_g": 45, "fat_g": 2},
    "banana 1 large":     {"calories": 121, "protein_g": 1,  "carbs_g": 31, "fat_g": 0},
    "greek yogurt 1 cup": {"calories": 150, "protein_g": 17, "carbs_g": 9,  "fat_g": 4},
    "broccoli 1 cup":     {"calories": 55,  "protein_g": 4,  "carbs_g": 11, "fat_g": 1},
    "sweet potato 1":     {"calories": 103, "protein_g": 2,  "carbs_g": 24, "fat_g": 0},
}


def _empty_log(log_date: str) -> dict:
    return {
        "date": log_date,
        "entries": [],
        "totals": {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0},
        "meal_slots": {
            slot: {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
            for slot in ("breakfast", "lunch", "dinner", "snack")
        }
    }


def load_log(log_date: str) -> dict:
    log_file = LOGS_DIR / f"{log_date}.json"
    empty = _empty_log(log_date)
    data = safe_read_json(log_file, fallback=empty)
    # Ensure required keys exist even if file was partially written
    if "entries" not in data or not isinstance(data.get("entries"), list):
        data["entries"] = []
    if "totals" not in data or not isinstance(data.get("totals"), dict):
        data["totals"] = empty["totals"]
    return data


def save_log(log_data: dict, log_date: str) -> bool:
    """Recompute totals and write log atomically. Returns True on success."""
    log_file = LOGS_DIR / f"{log_date}.json"
    # Recompute totals
    totals = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
    slots = {s: {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}
             for s in ("breakfast", "lunch", "dinner", "snack")}
    for entry in log_data.get("entries", []):
        slot = entry.get("meal_slot", "snack")
        if slot not in slots:
            slot = "snack"  # default unknown slots to snack
        for key in totals:
            val = entry.get(key, 0)
            if not isinstance(val, (int, float)):
                val = 0
            totals[key] += val
            slots[slot][key] += val
    log_data["totals"] = totals
    log_data["meal_slots"] = slots
    return safe_write_json(log_file, log_data)


def lookup_macros(item_name: str) -> dict:
    """Look up macros for an item. Returns estimated values if not found."""
    key = item_name.lower().strip()
    if key in NUTRITION_DB:
        return {**NUTRITION_DB[key], "estimated": False}
    # Fuzzy: check if any DB key is a substring
    for db_key, macros in NUTRITION_DB.items():
        if db_key.split()[0] in key:
            return {**macros, "estimated": True}
    # Default estimate
    print(f"  ⚠  Unknown item '{item_name}' — using placeholder values (estimated)")
    return {"calories": 200, "protein_g": 15, "carbs_g": 20, "fat_g": 8, "estimated": True}


_DEFAULT_TARGETS = {"daily_calories": 2200, "macros": {"protein_g": 165, "carbs_g": 220, "fat_g": 70}}


def load_targets() -> dict:
    data = safe_read_json(TARGETS_FILE, fallback=_DEFAULT_TARGETS)
    # Ensure required keys with safe defaults
    if "daily_calories" not in data or not isinstance(data.get("daily_calories"), (int, float)):
        data["daily_calories"] = _DEFAULT_TARGETS["daily_calories"]
    if "macros" not in data or not isinstance(data.get("macros"), dict):
        data["macros"] = _DEFAULT_TARGETS["macros"]
    # Guard against zero/negative targets (would cause division errors downstream)
    if data["daily_calories"] <= 0:
        data["daily_calories"] = _DEFAULT_TARGETS["daily_calories"]
    for macro_key in ("protein_g", "carbs_g", "fat_g"):
        val = data["macros"].get(macro_key, 0)
        if not isinstance(val, (int, float)) or val <= 0:
            data["macros"][macro_key] = _DEFAULT_TARGETS["macros"][macro_key]
    return data


def show_log(log_date: str):
    log = load_log(log_date)
    targets = load_targets()
    t = log["totals"]
    g = targets["macros"]
    cal_target = targets["daily_calories"]

    print(f"\n── Log for {log_date} ──────────────────────────────────────")
    if not log["entries"]:
        print("  No entries yet.")
    else:
        for slot in ("breakfast", "lunch", "dinner", "snack"):
            slot_entries = [e for e in log["entries"] if e.get("meal_slot") == slot]
            if slot_entries:
                print(f"\n  {slot.capitalize()}")
                for e in slot_entries:
                    flag = " (est.)" if e.get("estimated") else ""
                    name = e.get("name", "(unknown)")[:35]
                    cal = e.get("calories", 0)
                    p = e.get("protein_g", 0)
                    c = e.get("carbs_g", 0)
                    f = e.get("fat_g", 0)
                    print(f"    {name:<35} {cal} kcal  {p}P / {c}C / {f}F{flag}")

    remaining = cal_target - t.get("calories", 0)
    print(f"\n  ─────────────────────────────────────────────────────────")
    print(f"  Totals:   {t.get('calories', 0)} / {cal_target} kcal  "
          f"({remaining:+} remaining)")
    print(f"  Protein:  {t.get('protein_g', 0)}g / {g['protein_g']}g")
    print(f"  Carbs:    {t.get('carbs_g', 0)}g / {g['carbs_g']}g")
    print(f"  Fat:      {t.get('fat_g', 0)}g / {g['fat_g']}g\n")


def add_entry(meal_str: str, slot: str, log_date: str):
    log = load_log(log_date)
    items = [i.strip() for i in meal_str.split(",") if i.strip()]
    if not items:
        print("  Error: No food items provided. Nothing logged.")
        return
    added = []

    for item in items:
        macros = lookup_macros(item)
        entry = {
            "id": datetime.now().isoformat(),
            "meal_slot": slot,
            "logged_at": datetime.now().isoformat(),
            "name": item,
            "calories": macros["calories"],
            "protein_g": macros["protein_g"],
            "carbs_g": macros["carbs_g"],
            "fat_g": macros["fat_g"],
            "estimated": macros.get("estimated", False),
            "notes": ""
        }
        log["entries"].append(entry)
        added.append(entry)

    if not save_log(log, log_date):
        print("  Error: Failed to save log. Entries were not persisted.")
        return

    targets = load_targets()
    t = log["totals"]
    cal_target = targets["daily_calories"]

    print(f"\n  Logged ({slot}):")
    for e in added:
        flag = " [est.]" if e.get("estimated") else ""
        print(f"    + {e['name']} — {e['calories']} kcal  "
              f"{e['protein_g']}g P / {e['carbs_g']}g C / {e['fat_g']}g F{flag}")

    remaining = cal_target - t.get("calories", 0)
    print(f"\n  Today so far: {t.get('calories', 0)} / {cal_target} kcal  "
          f"({remaining:+} remaining)")
    print(f"  Protein: {t.get('protein_g', 0)}g  Carbs: {t.get('carbs_g', 0)}g  "
          f"Fat: {t.get('fat_g', 0)}g\n")


def main():
    parser = argparse.ArgumentParser(description="Log meals and track daily macros.")
    parser.add_argument("--meal", help="Meal description to log (comma-separated items)")
    parser.add_argument("--slot", default="lunch",
                        choices=["breakfast", "lunch", "dinner", "snack"],
                        help="Meal slot (default: lunch)")
    parser.add_argument("--show", action="store_true", help="Show today's log")
    parser.add_argument("--date", default=str(date.today()),
                        help="Date to log/show (YYYY-MM-DD, default: today)")
    args = parser.parse_args()

    validated_date = validate_date(args.date)
    if args.show:
        show_log(validated_date)
    elif args.meal:
        add_entry(args.meal, args.slot, validated_date)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
