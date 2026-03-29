# HEB Integration — Meal Plan Grocery Export

## How the Handoff Works

After generating or confirming a weekly meal plan, extract all ingredients from every meal in the plan. Deduplicate and merge quantities for identical items, then pass the list to the `heb-list-builder` skill.

## Step-by-Step

**1. Extract ingredients**

Iterate over all 7 days × all meal slots in the plan JSON. Collect every ingredient object:
```
{ "item": "chicken breast", "quantity": 1.5, "unit": "lb" }
```

**2. Merge duplicates**

Group by normalized item name (lowercase, stripped). Sum quantities when units match. When units differ (e.g., "1 cup" vs "200g"), keep separate line items — do not convert.

**3. Format as plain text**

Output one item per line:
```
3 lb chicken breast
1.5 lb salmon fillet
6 large eggs
2 cup Greek yogurt (plain, 2%)
1 cup mixed berries
...
```

**4. Hand off to heb-list-builder**

Pass the formatted list with this exact instruction:

> "Build my HEB list from these meal plan ingredients: [paste list]"

The heb-list-builder skill will handle deduplication against any existing master list and produce the final order-ready list.

## Notes

- Pantry staples (salt, pepper, olive oil, garlic) are included — the user may already have them but it's better to surface them.
- Produce quantities should be in whole units when practical (e.g., "3 avocados" not "1.5 cups diced avocado") — adjust during extraction when the meal calls for partial produce.
- If the user has a master HEB list saved, the heb-list-builder skill will merge and deduplicate automatically.
