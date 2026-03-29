# Macro Guidelines — Extended Reference

## Protein Targets by Goal

| Context | Protein per lb bodyweight |
|---------|--------------------------|
| Sedentary / general health | 0.6–0.8 g/lb |
| Active, maintaining | 0.8–1.0 g/lb |
| Cutting (preserving muscle) | 1.0–1.2 g/lb |
| Lean bulking | 0.8–1.0 g/lb |
| Athlete / heavy training | 1.0–1.4 g/lb |

Higher protein during a cut is muscle-preserving. Do not go below 0.7 g/lb unless the user explicitly requests it.

## Fat Minimums

Do not set dietary fat below 0.3 g/lb bodyweight — this is the minimum for hormonal health. Flag if a user's custom split puts fat below this floor.

## Carbs

Carbs fill the remainder after protein and fat are set. There is no minimum unless the user is on a ketogenic protocol (<50g/day). Carbs are the primary performance fuel — protect them during bulks and moderate active cuts.

## Fiber Target

Recommend (but don't track by default): 14g fiber per 1,000 kcal consumed. Mention when generating meal plans.

## Common Goal Presets

### Fat Loss (Cut)
- Deficit: 300–500 kcal below TDEE
- Protein: 1.0 g/lb (high, to preserve lean mass)
- Fat: 25–30% of total kcal
- Timeline: 0.5–1.0 lb fat loss per week

### Maintenance
- Calories: TDEE ± 0
- Protein: 0.8 g/lb
- Fat: 30% kcal
- Use when: transitioning between cut and bulk, recomp

### Lean Bulk
- Surplus: 150–300 kcal above TDEE
- Protein: 0.9 g/lb
- Fat: 25% kcal
- Timeline: 0.25–0.5 lb/week gain (mostly lean)

## Re-Calculation Triggers

Suggest recalculating targets when:
- Weight changes ≥5 lbs
- Activity level changes (new job, starting/stopping training program)
- Goal changes (cut → bulk, etc.)
- Every 8–12 weeks as a standard check-in

## Caloric Estimations

When body stats are not available, use these rough defaults (adult male, moderately active):
- Maintain: ~2,400–2,600 kcal
- Cut: ~1,900–2,200 kcal
- Bulk: ~2,700–3,000 kcal

Always flag these as estimates and prompt the user to provide stats for a precise calculation.
