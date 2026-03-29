---
name: meal-prep-planner
description: >
  Use this skill when the user says "plan my meals", "make a meal plan",
  "what should I eat this week", "generate a meal plan", "meal prep for the week",
  "prep my meals", "build my meal plan", "create a weekly menu", or asks to
  "export grocery list from meal plan". Also trigger when the user wants to
  review, edit, or regenerate their current weekly meal plan, or when they want
  to send a meal plan's ingredients to HEB.
metadata:
  version: "0.1.0"
---

## Meal Prep Planner

Generate, store, and manage weekly meal plans. Each plan balances culinary variety against macro targets from `data/targets.json`. Export the ingredient list directly to the heb-list-builder skill.

### Data Paths

All paths are relative to the plugin root (`${CLAUDE_PLUGIN_ROOT}`):

- **Targets**: `data/targets.json` — daily calorie and macro goals
- **Meal plans**: `data/meal-plans/YYYY-WNN.json` — one file per ISO week
- **Meal library**: `data/meals-library.json` — saved recipes and their macros

### Workflow

**1. Load context**

Read `data/targets.json`. If it doesn't exist, prompt the user to run the macro-targets skill first.

Read `data/meals-library.json` if it exists. Use it to seed variety — avoid repeating any meal from the previous week's plan if a prior plan file exists.

**2. Generate the plan**

Produce 7 days × 3 meals (breakfast, lunch, dinner) + optional snack.

Rules:
- No meal repeated within the same week
- Rotate proteins across the week (chicken, beef, fish, legumes, eggs, etc.)
- Each day's total must land within ±100 kcal of the daily calorie target and within ±10g of each macro target
- Label prep-friendly meals (batch-cookable, freezer-safe) with `"prep_friendly": true`
- Keep meals practical — 30 min or less unless user says otherwise

**3. Display the plan**

Present as a clean day-by-day table:

```
Day        | Breakfast          | Lunch                  | Dinner              | Calories | P/C/F
-----------|--------------------|-----------------------|---------------------|----------|------
Monday     | Greek yogurt bowl  | Grilled chicken wrap  | Salmon + rice       | 2,180    | 165/210/68
...
```

Show weekly totals and average daily macros at the bottom.

**4. Save the plan**

Write the plan to `data/meal-plans/YYYY-WNN.json` using the schema in `references/meal-plan-schema.md`.

Update `data/meals-library.json` with any new meals added during this session (merge, don't overwrite).

**5. HEB export**

After displaying the plan, always offer: *"Export ingredient list to HEB?"*

If yes, compile a deduplicated, quantity-merged ingredient list from all 7 days. Format it as plain-text line items (`quantity unit item`) and hand it off to the heb-list-builder skill with the instruction: "Build my HEB list from these meal plan ingredients."

### Editing the Plan

If the user wants to swap a meal:
1. Replace the meal in the displayed plan
2. Recalculate day totals
3. Warn if the swap pushes any day >150 kcal or >15g macro off target
4. Re-save the file

### Regeneration

If the user says "regenerate" or "different options", produce a new plan avoiding all meals used in both the current and previous week.

See `references/meal-plan-schema.md` for exact JSON format and `references/heb-integration.md` for the handoff format.

### Error Handling

**Missing `data/` or subdirectories**: If `data/meal-plans/` does not exist, create it before saving. Never crash on a missing directory.

**Missing targets**: If `data/targets.json` does not exist or contains invalid JSON, do not proceed. Respond: "No valid macro targets found. Run 'set my macro targets' first so I can build a plan that matches your goals."

**Corrupt meals library**: If `data/meals-library.json` exists but contains invalid JSON, warn the user ("Meal library is corrupted — starting fresh") and initialize a new empty library. Rename the corrupt file to `meals-library.json.bak`.

**Null values in targets**: If `targets.json` has `null` for `daily_calories` or any macro, treat it as the default (2,200 kcal / 165P / 220C / 70F) and inform the user the defaults are being used.

**Empty meal library**: If the library has zero meals, that's fine — generate everything from scratch. Do not treat an empty library as an error.
