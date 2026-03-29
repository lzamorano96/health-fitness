# Meal Plan JSON Schema

File: `data/meal-plans/YYYY-WNN.json`
Naming: ISO 8601 week — e.g., `2026-W13.json` for the week of March 23, 2026.

## Schema

```json
{
  "week": "2026-W13",
  "generated_at": "2026-03-27T10:00:00",
  "targets": {
    "calories": 2200,
    "protein_g": 165,
    "carbs_g": 220,
    "fat_g": 70
  },
  "days": [
    {
      "date": "2026-03-23",
      "day_name": "Monday",
      "meals": {
        "breakfast": {
          "name": "Greek yogurt parfait",
          "calories": 380,
          "protein_g": 28,
          "carbs_g": 42,
          "fat_g": 9,
          "prep_friendly": true,
          "ingredients": [
            { "item": "Greek yogurt (plain, 2%)", "quantity": 1, "unit": "cup" },
            { "item": "mixed berries", "quantity": 0.5, "unit": "cup" },
            { "item": "granola", "quantity": 0.25, "unit": "cup" },
            { "item": "honey", "quantity": 1, "unit": "tsp" }
          ]
        },
        "lunch": { ... },
        "dinner": { ... },
        "snack": { ... }
      },
      "totals": {
        "calories": 2195,
        "protein_g": 162,
        "carbs_g": 218,
        "fat_g": 71
      }
    }
  ],
  "weekly_summary": {
    "avg_daily_calories": 2198,
    "avg_protein_g": 163,
    "avg_carbs_g": 219,
    "avg_fat_g": 70,
    "prep_friendly_meals": 12
  }
}
```

## Meals Library Schema

File: `data/meals-library.json`

Stores all meals ever used. Append new meals; never remove unless user asks.

```json
{
  "meals": [
    {
      "id": "greek-yogurt-parfait",
      "name": "Greek yogurt parfait",
      "meal_type": "breakfast",
      "calories": 380,
      "protein_g": 28,
      "carbs_g": 42,
      "fat_g": 9,
      "prep_friendly": true,
      "prep_time_min": 5,
      "ingredients": [
        { "item": "Greek yogurt (plain, 2%)", "quantity": 1, "unit": "cup" },
        { "item": "mixed berries", "quantity": 0.5, "unit": "cup" },
        { "item": "granola", "quantity": 0.25, "unit": "cup" },
        { "item": "honey", "quantity": 1, "unit": "tsp" }
      ],
      "last_used": "2026-W13"
    }
  ]
}
```

## Targets File

File: `data/targets.json`

```json
{
  "daily_calories": 2200,
  "macros": {
    "protein_g": 165,
    "carbs_g": 220,
    "fat_g": 70
  },
  "updated_at": "2026-03-27"
}
```
