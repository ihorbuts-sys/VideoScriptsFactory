# bowl_steam_overhead (new; catalog v3, owner go-ahead 2026-11-16)

Steps: dish-review/main (dishKind soups; bowls and sushi).

Shot type **plate**, level **complex**, back camera, portrait, about 5 s.

Research: commercial_shots.md steam-hold and flat-lay-reveal; reference_shots/food_and_drink.md sections 2 and 4.

Scene: The approved serving_bowl on the table at a place setting with the dessert spoon to the right (soup) - for bowls and sushi the same bowl, spoon swapped for nothing (state which variant you render: soup first). Phone flat about 14 in above the bowl, then a slow rise to about 22 in; faint steam strands only if they read from above (say which).

Beats:
- atSec 0: "Phone flat above the bowl, bowl in the middle."
- atSec 1.0: "Raise the phone straight up slowly; keep it flat."
- atSec 3.5: "Stop when the spoon is in frame."

Status: now.

Common rules (all v3 requests): approved objects only (OBJECTS.md inventory, plus the owner approvals of
2026-11-16: food truck, burger, cake_slice, serving_bowl, salon_chair, wall_shelf, display_case, serving_tray,
treatment_bed one-hole copy, hair_clipper, dumbbell, takeaway_cup, laptop, reception desk composition, dessert spoon,
teaspoon, dessert knife, paper wrap closed/opened, paper tray). Not available: t-shirt (owner regenerating), salon mirror
(candidate). A missing object: stop and write an OBJECTS.md request (guide-objects skill). Generic stand-ins (owner:
"as generic as possible"). Place setting per STYLE.md "Objects" (pastry, pizza, bakery and handhelds: no cutlery;
desserts: dessert plate; mains and salad: fork and knife 3/4 in clear). US units in every text (titles, beats,
directions). Line-art P0 style, 9:16, hero inside the 28% / 35% band. Draft only: no publish, no commit; report per the
guide-animator skill. Metadata in record.json: showsFace, needsHelper, guideVisibleToCreator, units "us", zoomHint.

Draft (guide-animator, 2026-11-16): `scripts/dish-review/dish-review/guides/bowl_steam_overhead/` (record.json, render/,
export/, sheet.png); scene code `guides/blender_motion/drafts/bowl_steam_overhead.py`. Soup variant rendered (dessert
spoon right, 3/4 in clear); steam left out (from straight above the strands project as two flat squiggles on the bowl
floor, not rising steam). Beats above kept as written; note: at 14 in the whole spoon is already in frame.
