# experience_floor_pan (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/place (subject experience: gym, entertainment, recreational, events).

Shot type **room**, level **easy**, back camera, portrait, about 5 s.

Research: commercial_shots.md room-pan (gym floor); best_practices/sport_health.md and entertainment.md.

Scene: A generic open floor: plain walls, a window, two benches (procedural blocks are fine as a generic stand-in only if they are the approved table/bench primitives; otherwise stop), dumbbells (approved) on the floor in a row. Phone at chest height, slow pan right across the floor.

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

## Draft (guide-animator, 2026-11-16)

Draft: `record.json`, `render/`, `export/`, `sheet.png` in this folder; scene `guides/blender_motion/drafts/experience_floor.py`
(template `room_bar_pan`). Export check passed. Level easy: no beats.
Assumed: benches are the approved long tabletop block (`G.block`, 0.025 bevel) at bench size, 14 x 47 in, solid to
the floor, top 18 in; contour-only line art draws it as a box outline, not a slatted bench (the legacy procedural
bench stays rejected). Walls are not drawn (STYLE "Drawing"); the window frame marks the far wall. Shot type mapped
to `room-from-table` (no plain `room` type in the registry).

## Rework r2 (owner review 2026-11-17: "let's make each dumbbell bigger and bigger")

The row is now lightest to heaviest like a gym rack: four uniform scaled copies of the approved dumbbell, 1x to 1.8x
(12.6 to 22.7 in long, each about 22% larger), 2.4 in apart, about 8.5 ft (2.6 m) ahead, centred on the end-of-pan
view so the whole row fits the target frame. Six growing copies did not fit the frame width (probe), so the row has
four. The right bench moved 8 in (0.2 m) further back to stay clear of the largest dumbbell. Camera, pan, window and
left bench unchanged. Previous draft archived in `archive/r1_2026-11-16/`. Export passed. Level easy: no beats.

## Rework r3 (owner review 2026-11-16 14:49-14:52: "turn each dumbbell 90 degrees and add a pair for each (exact size)")

Each dumbbell is turned 90 deg about the vertical axis, so its handle points toward the camera, and has an identical
twin (same scale) beside it: four pairs, lightest to heaviest (1x to 1.8x, 12.6 to 22.7 in long), the two of a pair
1.6 in (4 cm) apart, pairs 6 in (15 cm) apart, the row about 6.5 ft (1.97 m) wide, still about 8.5 ft (2.6 m) ahead
and centred on the end-of-pan view line, so it fits the target frame as before. Camera, pan, window and benches
unchanged. Seen end-on from chest height the front plate hides most of the handle, so each dumbbell reads as two
plates one behind the other. Previous draft archived in `archive/r2_2026-11-16/` (record renamed `record.r2.json`;
r1's to `record.r1.json`). Level easy: no beats.
