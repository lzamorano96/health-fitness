#!/usr/bin/env python3
"""
export_grocery_list.py — Extract and merge all ingredients from a weekly meal plan.

Usage:
  python scripts/export_grocery_list.py             # Current ISO week
  python scripts/export_grocery_list.py --week 2026-W13
  python scripts/export_grocery_list.py --week 2026-W13 --output grocery.txt

Output: A deduplicated, quantity-merged plain-text ingredient list, ready to
paste into the heb-list-builder skill or save as a .txt file.
"""

import json
import sys
import re
import math
import argparse
from pathlib import Path
from datetime import date, timedelta
from collections import defaultdict

SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = SCRIPT_DIR.parent
MEAL_PLANS_DIR = PLUGIN_ROOT / "data" / "meal-plans"

WEEK_PATTERN = re.compile(r"^\d{4}-W\d{2}$")


def validate_week(week_str: str) -> str:
    """Validate ISO week format YYYY-WNN. Exits on bad input."""
    if not WEEK_PATTERN.match(week_str):
        print(f"  Error: Invalid week format '{week_str}'. Expected YYYY-WNN (e.g., 2026-W13).")
        sys.exit(1)
    year, week_num = week_str.split("-W")
    week_num = int(week_num)
    if week_num < 1 or week_num > 53:
        print(f"  Error: Week number {week_num} out of range (1–53).")
        sys.exit(1)
    return week_str


def get_current_iso_week() -> str:
    today = date.today()
    iso = today.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def load_plan(week_str: str) -> dict:
    plan_file = MEAL_PLANS_DIR / f"{week_str}.json"
    if not plan_file.exists():
        print(f"  Error: No meal plan found for {week_str}.")
        print(f"  Expected file: {plan_file.name} in meal-plans directory.")
        sys.exit(1)
    try:
        with open(plan_file) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"  Error: {plan_file.name} has unexpected format (expected JSON object).")
            sys.exit(1)
        return data
    except json.JSONDecodeError:
        print(f"  Error: {plan_file.name} contains invalid JSON. Fix or regenerate the meal plan.")
        sys.exit(1)
    except PermissionError:
        print(f"  Error: Permission denied reading {plan_file.name}.")
        sys.exit(1)
    except OSError as e:
        print(f"  Error: Could not read meal plan: {e}")
        sys.exit(1)


def normalize_item(item: str) -> str:
    """Normalize item name for deduplication."""
    return item.lower().strip().rstrip("s")  # basic pluralization normalize


def merge_ingredients(plan: dict) -> list[dict]:
    """Extract and merge all ingredients across all meals in the plan."""
    # key: (normalized_name, unit) -> {item, quantity, unit}
    merged = defaultdict(lambda: {"quantity": 0.0, "unit": "", "item": ""})

    for day in plan.get("days", []):
        for slot_name, meal in day.get("meals", {}).items():
            if not isinstance(meal, dict):
                continue
            for ing in meal.get("ingredients", []):
                if not isinstance(ing, dict):
                    continue
                item = str(ing.get("item", "")).strip()
                if not item:
                    continue  # skip entries with no item name
                unit = str(ing.get("unit", "")).strip().lower()
                try:
                    qty = float(ing.get("quantity", 0))
                except (ValueError, TypeError):
                    qty = 1.0  # default to 1 if quantity is not a number
                norm_key = (normalize_item(item), unit)

                if merged[norm_key]["item"] == "":
                    merged[norm_key]["item"] = item
                    merged[norm_key]["unit"] = unit
                merged[norm_key]["quantity"] += qty

    # Sort: by item name
    result = sorted(merged.values(), key=lambda x: x["item"].lower())
    return result


def format_quantity(qty: float) -> str:
    """Format quantity: use integers when whole, otherwise 1 decimal.
    Guards against NaN, infinity, and negative values."""
    if math.isnan(qty) or math.isinf(qty):
        return "1"  # safe fallback
    if qty < 0:
        qty = abs(qty)
    if qty == int(qty):
        return str(int(qty))
    return f"{qty:.1f}"


def format_list(ingredients: list[dict]) -> str:
    lines = []
    for ing in ingredients:
        qty = format_quantity(ing["quantity"])
        unit = ing["unit"]
        item = ing["item"]
        if unit:
            lines.append(f"{qty} {unit} {item}")
        else:
            lines.append(f"{qty} {item}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Export ingredient list from a weekly meal plan."
    )
    parser.add_argument("--week", default=None,
                        help="ISO week string (e.g., 2026-W13). Default: current week.")
    parser.add_argument("--output", default=None,
                        help="Save output to this file instead of printing.")
    args = parser.parse_args()

    week = args.week or get_current_iso_week()
    if args.week:
        week = validate_week(args.week)
    print(f"\n  Loading meal plan: {week}")

    plan = load_plan(week)
    ingredients = merge_ingredients(plan)

    if not ingredients:
        print("  No ingredients found in this meal plan.")
        sys.exit(0)

    formatted = format_list(ingredients)
    header = (
        f"# Grocery List — {week}\n"
        f"# {len(ingredients)} items\n"
        f"# Generated from meal plan by health-fitness plugin\n\n"
    )
    output = header + formatted

    if args.output:
        if not args.output.strip():
            print("  Error: Output path is empty. Provide a valid file path.")
            sys.exit(1)
        out_path = Path(args.output.strip())
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output)
            print(f"  Saved to: {out_path}")
        except PermissionError:
            print(f"  Error: Permission denied writing to {out_path}.")
            sys.exit(1)
        except OSError as e:
            print(f"  Error: Could not write output file: {e}")
            sys.exit(1)
    else:
        print(f"\n{'─'*50}")
        print(output)
        print(f"{'─'*50}")
        print(f"\n  {len(ingredients)} items. Copy the list above into the heb-list-builder skill.\n")


if __name__ == "__main__":
    main()
