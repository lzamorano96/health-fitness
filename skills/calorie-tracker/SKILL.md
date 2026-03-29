---
name: calorie-tracker
description: >
  Use this skill when the user says "log a meal", "track my calories", "I ate",
  "log my food", "add food to my log", "what did I eat today", "how many calories
  have I had", "log breakfast/lunch/dinner/snack", "delete a food entry",
  "edit my log", "show my calories for today", or "what are my macros so far".
  Also trigger when the user pastes a list of foods and wants them logged.
metadata:
  version: "0.1.0"
---

## Calorie Tracker

Log daily food intake and query running calorie/macro totals. All data is stored in `data/logs/YYYY-MM-DD.json`.

### Data Path

- **Daily log**: `data/logs/YYYY-MM-DD.json` (one file per day, e.g., `data/logs/2026-03-27.json`)
- **Targets**: `data/targets.json`

### Logging a Meal

**1. Parse the input**

Extract food items, quantities, and meal slot (breakfast/lunch/dinner/snack). Accept casual input:
- "I had 2 scrambled eggs and a slice of whole wheat toast" → parse as breakfast if before noon, otherwise ask
- "log: grilled chicken 6oz, brown rice 1 cup, broccoli 1 cup" → parse all three

**2. Estimate macros**

Use well-known nutritional data. When precision matters, prefer USDA reference values. State confidence:
- High confidence (standard item like "1 cup oats") — log without comment
- Medium confidence (restaurant item, vague portion) — flag: `"estimated": true`, note assumption

Common reference values in `references/nutrition-reference.md`.

**3. Load and update the log**

Read today's `data/logs/YYYY-MM-DD.json`. If it doesn't exist, create it with the schema below. Append the new entries. Write back.

**4. Confirm with running totals**

After logging, always show:
```
Logged: Grilled chicken (6 oz) — 280 kcal | 52g P / 0g C / 6g F

Today so far:
  Calories:  1,420 / 2,200  (780 remaining)
  Protein:   118g / 165g
  Carbs:     162g / 220g
  Fat:       44g  / 70g
```

### Querying the Log

When the user asks "what did I eat today" or "show my log":
- Read today's log file
- Display a meal-by-meal breakdown with per-item macros
- Show daily totals vs targets
- Flag any macro that is >110% of target in red notation: `⚠ 178g protein (108%)`

### Editing and Deleting Entries

If the user says "remove the chicken" or "delete my snack entry":
1. Find the matching entry by name + meal slot
2. Remove it from the entries array
3. Recalculate day totals
4. Write the updated file
5. Confirm: "Removed grilled chicken. Today: 1,140 kcal remaining."

### Log File Schema

See `references/log-schema.md` for the exact JSON structure.

### Nutrition Estimation

When the user gives vague input, ask one clarifying question maximum — don't interrogate. Default to a medium portion if truly unknown and flag it.

Do not invent brands. Use generic item names in the log.

### Error Handling

Follow these defensive rules at every step:

**Missing data directory**: If `data/` or `data/logs/` does not exist, create it before writing. Never crash on a missing directory.

**Corrupt or empty log file**: If a log file exists but contains invalid JSON, warn the user ("Your log for [date] appears corrupted — starting a fresh log") and create a new empty log. Do not silently discard the corrupt file — rename it to `YYYY-MM-DD.json.bak` first.

**Deletion on empty log**: If the user asks to delete an entry but the log is empty or the entry doesn't exist, respond with: "No matching entry found for [item] in [slot]. Here's what's currently logged:" and display the log. Never error silently.

**Empty or unprintable input**: If the user provides an empty string or a string with only whitespace/control characters, respond: "No food items provided. Try something like: 'log chicken breast 6oz for lunch'."

**Non-numeric macro values**: If a log entry has non-numeric values for calories or macros (e.g., from a hand-edited file), treat them as 0 and flag the entry as needing correction.
