---
name: macro-targets
description: >
  Use this skill when the user says "set my macros", "update my calorie goal",
  "change my protein target", "set my macro targets", "update my nutrition goals",
  "what are my current targets", "show my macro goals", "recalculate my macros",
  "I want to bulk / cut / maintain", or provides new weight/height/activity level
  and wants updated nutrition targets. Also trigger when the user asks
  "how many calories should I eat" or wants to calculate TDEE or BMR.
metadata:
  version: "0.1.0"
---

## Macro Targets

Set, calculate, and update daily calorie and macronutrient targets. Targets are stored in `data/targets.json` and referenced by all other skills in this plugin.

### Data Path

- `data/targets.json` — the single source of truth for all daily targets

### Calculating Targets from Scratch

When the user wants to calculate their targets, collect:
1. **Sex** (biological, for BMR formula)
2. **Age**
3. **Height**
4. **Weight**
5. **Activity level**: sedentary / lightly active / moderately active / very active / athlete
6. **Goal**: cut (lose fat) / maintain / lean bulk (gain muscle)

Use the **Mifflin-St Jeor BMR** formula:

```
Male:   BMR = 10×weight_kg + 6.25×height_cm - 5×age + 5
Female: BMR = 10×weight_kg + 6.25×height_cm - 5×age - 161
```

TDEE = BMR × activity multiplier:

| Activity Level | Multiplier |
|---------------|------------|
| Sedentary | 1.2 |
| Lightly active (1-3 days/wk) | 1.375 |
| Moderately active (3-5 days/wk) | 1.55 |
| Very active (6-7 days/wk) | 1.725 |
| Athlete (2x/day training) | 1.9 |

Goal adjustments:
- **Cut**: TDEE − 300 to −500 kcal (default −350)
- **Maintain**: TDEE ± 0
- **Lean bulk**: TDEE + 150 to +300 kcal (default +200)

### Macro Split Calculation

After calorie target is set, calculate macros using these defaults (override if user specifies):

| Goal | Protein | Fat | Carbs |
|------|---------|-----|-------|
| Cut | 1.0 g/lb bodyweight | 25% of total kcal | remainder |
| Maintain | 0.8 g/lb bodyweight | 30% of total kcal | remainder |
| Lean Bulk | 0.9 g/lb bodyweight | 25% of total kcal | remainder |

Macro calorie math: Protein = 4 kcal/g, Carbs = 4 kcal/g, Fat = 9 kcal/g.

Always show the full breakdown before saving:

```
Calculated targets:

  Daily calories:  2,200 kcal
  Protein:         165g  (660 kcal / 30%)
  Carbohydrates:   220g  (880 kcal / 40%)
  Fat:             74g   (666 kcal / 30%)

  BMR:   1,820 kcal
  TDEE:  2,500 kcal
  Goal:  Cut (−300 kcal)
```

Ask for confirmation before writing.

### Manual Override

If the user provides specific numbers directly ("set calories to 2,400, protein 180g, carbs 240g, fat 80g"), skip the calculation and write those values directly. Validate that macros sum to within ±50 kcal of the total. If they don't, flag the discrepancy and ask which to adjust.

### Updating a Single Target

If the user changes only one value ("increase my protein to 180g"), read the existing file, update only that field, recalculate carbs to compensate if needed (keep fat constant unless user specifies), and confirm.

### File Write

Write to `data/targets.json` using the schema:
```json
{
  "daily_calories": 2200,
  "macros": {
    "protein_g": 165,
    "carbs_g": 220,
    "fat_g": 74
  },
  "goal": "cut",
  "tdee": 2500,
  "bmr": 1820,
  "body_stats": {
    "weight_lbs": 185,
    "height_in": 71,
    "age": 28,
    "sex": "male",
    "activity_level": "moderately active"
  },
  "updated_at": "2026-03-27"
}
```

After saving, confirm: "Targets saved. All skills are now using these values."

See `references/macro-guidelines.md` for sport-specific recommendations.
