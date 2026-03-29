# Daily Log JSON Schema

File: `data/logs/YYYY-MM-DD.json`

## Schema

```json
{
  "date": "2026-03-27",
  "entries": [
    {
      "id": "uuid-or-timestamp",
      "meal_slot": "breakfast",
      "logged_at": "2026-03-27T08:14:00",
      "name": "Scrambled eggs (2 large)",
      "calories": 182,
      "protein_g": 12,
      "carbs_g": 2,
      "fat_g": 14,
      "estimated": false,
      "notes": ""
    },
    {
      "id": "uuid-or-timestamp",
      "meal_slot": "breakfast",
      "logged_at": "2026-03-27T08:14:05",
      "name": "Whole wheat toast (1 slice)",
      "calories": 80,
      "protein_g": 4,
      "carbs_g": 15,
      "fat_g": 1,
      "estimated": false,
      "notes": ""
    },
    {
      "id": "uuid-or-timestamp",
      "meal_slot": "lunch",
      "logged_at": "2026-03-27T12:30:00",
      "name": "Grilled chicken breast (6 oz)",
      "calories": 280,
      "protein_g": 52,
      "carbs_g": 0,
      "fat_g": 6,
      "estimated": false,
      "notes": ""
    }
  ],
  "totals": {
    "calories": 542,
    "protein_g": 68,
    "carbs_g": 17,
    "fat_g": 21
  },
  "meal_slots": {
    "breakfast": { "calories": 262, "protein_g": 16, "carbs_g": 17, "fat_g": 15 },
    "lunch": { "calories": 280, "protein_g": 52, "carbs_g": 0, "fat_g": 6 },
    "dinner": { "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0 },
    "snack": { "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0 }
  }
}
```

## Field Definitions

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique entry identifier. Use ISO timestamp string if no UUID library available: `"2026-03-27T08:14:00"` |
| `meal_slot` | string | One of: `breakfast`, `lunch`, `dinner`, `snack` |
| `logged_at` | ISO 8601 | Timestamp when entry was logged |
| `estimated` | boolean | `true` if macros were estimated rather than looked up |
| `notes` | string | Optional user note (brand, restaurant, etc.) |

## Totals Maintenance

Always recompute `totals` and `meal_slots` by summing entries after any add/edit/delete. Never store deltas — always full recalculation.

## Weekly Log Aggregation

For weekly queries (fitness-dashboard skill), read all 7 daily files for the week. If a file is missing, treat that day as 0 kcal (don't fabricate data — just note the gap).
