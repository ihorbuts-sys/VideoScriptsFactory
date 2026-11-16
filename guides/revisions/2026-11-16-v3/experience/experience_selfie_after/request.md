# experience_selfie_after (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/after (subject experience; also visit).

Shot type **verdict**, level **easy**, front camera, portrait, about 5 s.

Research: reference_shots/venue_and_people.md section E (talking to camera); verdict_eye_level_v2 as template.

Scene: Front camera at arm's length, the creator rig right after the activity (towel over the shoulder is not approved - plain rig), the open floor behind. Template verdict_eye_level_v2 with the experience floor as background.

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

Level easy: no beats. Scene code `guides/blender_motion/drafts/experience_selfie.py`. Standing creator and open-palm
gesture as the published verdict_eye_level (2026-11-10), camera rule from verdict_eye_level_v2 (front 23 mm, 24 in /
0.60 m from the eyes at eye height, 5 deg to her right, 14.6 deg down, eyes one third from the top). Background: window,
floor plant, three approved dumbbells on the floor about 8-11 ft behind her; no table, cup or pendant. Export passed;
people checks passed; owner review pending.

## Rework r2 (owner review 2026-11-17: "remove plant")

Floor plant removed (left out like the table, cup and pendant); everything else unchanged. Previous draft archived in
`archive/r1_2026-11-16/` (render, export, sheet, record, request, scene code). Export passed; people checks passed
(scratch copy of `verify_p0_people.py` on this draft); hand and forearm stay 66 in (1.69 m) or more from every other
mesh. Frame diff against r1: only the plant strokes plus EEVEE line noise. Level easy: no beats.
