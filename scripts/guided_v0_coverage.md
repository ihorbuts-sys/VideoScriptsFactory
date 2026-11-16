# Guided v0 coverage (2026-11-10)

Level rule and beats: `guides/p0/guide_levels.json`. Active guides at the step's level / pending guides with specs.

| Script | Step | Kinds | Level | Active guides | Pending |
|---|---|---|---|---|---|
| food-review | arrive | coffee, dining, bakery, fast-food | easy | 3 | - |
| food-review | order | coffee, dining, bakery, fast-food | easy | 2 | - |
| food-review | dish | coffee, dining, bakery, fast-food | complex | 2 | plate_rise_overhead |
| food-review | bite | coffee, dining, bakery, fast-food | easy | 3 | - |
| food-review | verdict | coffee, dining, bakery, fast-food | easy | 3 | - |
| first-visit | entrance | coffee, dining | easy | 3 | - |
| first-visit | counter | coffee | easy | 2 | - |
| first-visit | menu | dining | easy | 2 | - |
| first-visit | drink | coffee | complex | 2 | - |
| first-visit | plate | dining | complex | 2 | plate_rise_overhead |
| first-visit | sip | coffee | easy | 3 | - |
| first-visit | forkful | dining | easy | 3 | - |
| first-visit | room | dining | complex | 2 | - |
| first-visit | verdict | coffee, dining | easy | 3 | - |
| food-review-drink | order | coffee, bakery, dining, fast-food | easy | 2 | - |
| food-review-drink | pour | coffee, bakery, dining, fast-food | easy | 2 | - |
| food-review-drink | cup | coffee, bakery, dining, fast-food | complex | 2 | - |
| food-review-drink | sip | coffee, bakery, dining, fast-food | easy | 3 | - |
| food-review-drink | verdict | coffee, bakery, dining, fast-food | easy | 3 | - |
| food-review-pour | build | entertainment, dining | easy | 1 | tap_pour_low |
| food-review-pour | glass | entertainment, dining | complex | 1 | glass_raise_light |
| food-review-pour | sip | entertainment, dining | easy | 3 | - |
| food-review-pour | verdict | entertainment, dining | easy | 3 | - |
| food-review-sweet | case | bakery, coffee, dining | easy | 0 | case_slide_to_item, case_hold_shelf |
| food-review-sweet | break | bakery, coffee, dining | complex | 2 | plate_rise_overhead |
| food-review-sweet | taste | bakery, coffee, dining | easy | 3 | - |
| food-review-sweet | verdict | bakery, coffee, dining | easy | 3 | - |
| food-review-handheld | window | fast-food, dining, entertainment | easy | 3 | - |
| food-review-handheld | cut | fast-food, dining, entertainment | complex | 2 | plate_rise_overhead |
| food-review-handheld | bite | fast-food, dining, entertainment | easy | 3 | - |
| food-review-handheld | verdict | fast-food, dining, entertainment | easy | 3 | - |
| food-review-table | spread | dining, fast-food | complex | 2 | - |
| food-review-table | action | dining, fast-food | easy | 0 | grill_low_hold, plate_moment_low_hold |
| food-review-table | how | dining, fast-food | easy | 1 | table_talk_front |
| food-review-table | bite | dining, fast-food | easy | 3 | - |
| food-review-table | verdict | dining, fast-food | easy | 3 | - |

Steps below two active guides: 5 (food-review-pour.build, food-review-pour.glass, food-review-sweet.case, food-review-table.action, food-review-table.how). They need the pending guides before the step is shippable.
Pending guides: 8 (plate_rise_overhead, tap_pour_low, glass_raise_light, case_slide_to_item, case_hold_shelf, grill_low_hold, table_talk_front, plate_moment_low_hold).
