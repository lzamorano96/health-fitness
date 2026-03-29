# health-fitness

Local health and fitness hub for Claude. Handles weekly meal planning, daily calorie/macro tracking, nutrition target management, and weekly progress reporting — all stored locally as JSON files with zero external dependencies.

## What It Does

| Capability | Trigger phrases |
|-----------|----------------|
| **Meal prep planning** | "plan my meals", "meal prep for the week", "build my meal plan" |
| **Calorie/macro logging** | "log my food", "I ate", "track my calories", "log breakfast" |
| **Macro target setup** | "set my macros", "update my calorie goal", "calculate my TDEE" |
| **Weekly dashboard** | "show my dashboard", "how am I doing this week", "nutrition summary" |
| **Auto-generate meal plan** | "generate my meal plan", "auto-generate meals" |

## Skills

### `meal-prep-planner`
Generates a 7-day meal plan hitting your macro targets. Rotates proteins, avoids repeat meals from last week, and flags batch-cookable (prep-friendly) meals. Exports the ingredient list directly to the HEB grocery ordering skill.

### `calorie-tracker`
Log food in plain language ("I had 6oz chicken and brown rice"). Maintains a running daily total vs your targets. Supports editing and deleting entries. All data stored in `data/logs/YYYY-MM-DD.json`.

### `macro-targets`
Calculate personalized macro targets using Mifflin-St Jeor BMR + TDEE. Supports cut / maintain / lean bulk goal presets. Saves to `data/targets.json` — all other skills read from this file.

### `fitness-dashboard`
Aggregates the week's daily logs into a formatted summary table. Shows per-day macros, on-target counts, and 2–3 data-backed insights. Exports to markdown if needed.

## Agent

### `meal-plan-generator`
Autonomous version of meal prep planning. Reads targets, cross-references the meal library, generates a macro-accurate 7-day plan, saves it, and returns a summary — no back-and-forth required.

## HEB Integration

The `meal-prep-planner` skill integrates with the `heb-list-builder` skill (separate plugin). After generating a meal plan, say "export grocery list to HEB" and the plugin will compile a deduplicated, quantity-merged ingredient list and hand it off automatically.

To run the export manually from the terminal:
```bash
python scripts/export_grocery_list.py
python scripts/export_grocery_list.py --week 2026-W13
```

## Setup

No API keys or external services required. Everything runs locally.

**First-time setup — set your targets:**
> "Set my macro targets" — Claude will walk you through BMR/TDEE calculation.

Or edit `data/targets.json` directly with your preferred values.

## Data Structure

```
data/
├── targets.json              # Daily calorie + macro goals
├── meals-library.json        # All meals ever used (for variety tracking)
├── logs/
│   └── YYYY-MM-DD.json       # One file per day
└── meal-plans/
    └── YYYY-WNN.json         # One file per ISO week
```

All files are plain JSON — easy to version in git, edit by hand, or query with any tool.

**Recommended: put the `data/` folder in a git repo for history tracking.**

## CLI Scripts

For power users who want terminal access:

```bash
# Log a meal
python scripts/log_meal.py --meal "chicken breast 6oz, brown rice 1 cup" --slot lunch

# Show today's log
python scripts/log_meal.py --show

# Weekly summary
python scripts/weekly_summary.py
python scripts/weekly_summary.py --week 2026-W13
python scripts/weekly_summary.py --month 2026-03

# Export grocery list
python scripts/export_grocery_list.py
python scripts/export_grocery_list.py --week 2026-W13 --output my-list.txt
```

Python 3.10+ required. No external packages needed.

## GitHub Versioning

To track your data in git:
```bash
cd path/to/health-fitness
git init
git add data/targets.json data/meals-library.json
git commit -m "Initial targets"
# Daily: git add data/logs/ && git commit -m "Log $(date +%Y-%m-%d)"
```
