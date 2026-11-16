# truck_across_street (new; catalog v3, owner go-ahead 2026-11-16)

Steps: dish-review/arrive, drink-review/arrive, venue-review/arrive (serviceKind truck).

Shot type **entrance**, level **easy**, back camera, portrait, about 5 s.

Research: reference_shots/venue_and_people.md section A (arrival); commercial_shots.md facade-pull-back (substitute: walk forward).

Scene: The approved food truck at its approved scale (3.0 m tall, about 4.7 m long), service window side to the lens, seen from across the street (about 30 ft); phone at eye level, slow walk forward about 3 ft. No people.

Status: after truck cache.

Common rules (all v3 requests): approved objects only (OBJECTS.md inventory, plus the owner approvals of
2026-11-16: food truck, burger, cake_slice, serving_bowl, salon_chair, wall_shelf, display_case, serving_tray,
treatment_bed one-hole copy, hair_clipper, dumbbell, takeaway_cup, laptop, reception desk composition, dessert spoon,
teaspoon, dessert knife, paper wrap closed/opened, paper tray). Not available: t-shirt (owner regenerating), salon mirror
(candidate). A missing object: stop and write an OBJECTS.md request (guide-objects skill). Generic stand-ins (owner:
"as generic as possible"). Place setting per STYLE.md "Objects" (pastry, pizza, bakery and handhelds: no cutlery;
desserts: dessert plate; mains and salad: fork and knife 3/4 in clear). US units in every text (titles, beats,
directions). Line-art P0 style, 9:16, hero inside the 28% / 35% band. Draft only: no publish, no commit; report per the
guide-animator skill. Metadata in record.json: showsFace, needsHelper, guideVisibleToCreator, units "us", zoomHint.

## Rework r2 (guide-animator, owner review 2026-11-17)

Owner: "put cooker inside, let's make the silhouette more distinct". v1 archived in `archive/2026-11-16-v1/` (record,
render, export, sheet, scene code). Same move and timing (3 ft walk from 30 ft, 5 s). Easy guide: no beats.
- Cook: the approved barista rig in the counter_edge_to_pass_v2 working pose (`barista.add`, same hold raised with his
  floor), inside the truck behind the window, in profile facing the pots, swirling the milk pitcher; supporting
  opacity. Shared setup: `guides/blender_motion/drafts/truck_cook.py`.
- Silhouette: the truck's outer contour (native Line Art silhouette, group filter) stays at full opacity, interior
  contours drawn at half of it; strokes under 12 px (stray dots) removed per frame. Both are per guide: the draft wraps
  `lineart_render.strokes_setup` inside its own Blender run, so shared defaults are unchanged.
- Open for the owner: the pitcher in a food truck (it is part of the approved pose); the interior share 0.5
  (judgement).
