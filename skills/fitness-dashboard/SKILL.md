---
name: fitness-dashboard
description: >
  Use this skill when the user says "show my dashboard", "how am I doing this week",
  "nutrition summary", "weekly recap", "show my progress", "how close am I to my goals",
  "weekly stats", "macro summary", "how's my nutrition", "show me my week",
  "calorie report", or "am I hitting my targets". Also trigger at the start of a session
  when the user seems to want a general health check-in.
metadata:
  version: "0.1.0"
---

## Fitness Dashboard

Aggregate and display a weekly nutrition summary. Pull from all daily log files and the active targets to produce a clear, data-dense report.

### Data Sources

- `data/targets.json` — daily goals
- `data/logs/YYYY-MM-DD.json` × 7 — current ISO week's daily logs
- `data/meal-plans/YYYY-WNN.json` — current week's meal plan (if exists)

### Determine the Week

Default to the current ISO week. If the user asks for "last week", use the previous ISO week. Accept explicit date requests ("week of March 23").

### Build the Report

**1. Load all daily logs for the week**

Read each file `2026-03-23.json` through `2026-03-29.json`. If a file is missing, mark that day as `— (no data)` — never fabricate.

**2. Compute weekly aggregates**

- Total calories logged (sum)
- Average daily calories
- Total and average per macro (protein, carbs, fat)
- Days on target: count days where calories were within ±10% of goal
- Best day (closest to all macro targets)
- Highest protein day

**3. Display the report**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  WEEKLY NUTRITION DASHBOARD — W13 2026
  Mon Mar 23 → Sun Mar 29
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DAILY BREAKDOWN
  Day        Calories    Protein    Carbs     Fat     vs Target
  Monday     2,195       162g       218g      71g     ✓ On target
  Tuesday    1,980       148g       200g      65g     ↓ -220 kcal
  Wednesday  2,310       170g       228g      74g     ↑ +110 kcal
  Thursday   —           —          —         —       No data
  Friday     2,200       165g       220g      70g     ✓ On target
  Saturday   2,050       155g       205g      68g     ↓ -150 kcal
  Sunday     —           —          —         —       No data

  WEEKLY SUMMARY (5 days logged)
  Avg calories:   2,147 / 2,200 target  (−53 avg)
  Avg protein:    160g  / 165g target   (97%)
  Avg carbs:      214g  / 220g target   (97%)
  Avg fat:        70g   / 70g target    (100%)

  Days on target:  2 / 5 logged  (3 within ±10%)
  Best day:        Friday (all macros within 2%)
  Highest protein: Wednesday (170g)

  MEAL PLAN ADHERENCE
  Meal plan exists for this week: Yes
  Logged meals matching plan:     ~3 of 5 days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**4. Insights (2–3 maximum)**

Add a short "Insights" block with data-backed observations only. No filler. Examples:
- "Protein average is 97% of target — solid consistency."
- "Tuesday and Saturday were low-calorie days — check if that was intentional."
- "2 days unlogged this week. Consider logging retroactively or noting them as rest days."

### Monthly View

If the user asks for a monthly summary, aggregate all daily log files for the current month. Show:
- Total days logged / days in month
- Monthly average for each macro vs target
- Week-by-week calorie trend (7-day average per row)

### Exporting

If the user asks to "export" or "save" the dashboard, write it as a markdown file to `data/reports/YYYY-WNN-report.md`.

See `references/dashboard-format.md` for the exact markdown export template.
