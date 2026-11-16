# venue_order_arrives (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/main (generic fallback; product subjects dineIn, counter).

Shot type **handoff**, level **easy**, back camera, portrait, about 4 s.

Research: reference_shots/food_and_drink.md section 8 (hand-off); handoff_counter_cup_v2 as template.

Scene: Reuse handoff_counter_cup_v2: the takeaway_cup (approved) set down on the counter edge toward the lens; static phone. Generic: no dish identity.

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

Rework (guide-animator, owner review 2026-11-17 "can it be the barista's hand (hold the cup more naturally)"): previous
draft archived in `archive/2026-11-16-v1/` (record, request, render, export, sheet, scene code copy). The palm-down
fingertip slide is replaced by glass_slide_close's approved slide grasp (`T.SLIDE_GRASP`: CC0 wrap, left hand, wrist
40/15, axis pivot, thenar pad, 2 mm contact gap unchanged), fitted to the takeaway cup's wall (lathe hull of the scan)
at 3 in up the body and turned to the staff side: palm on the cup's right, fingers across the front with their backs
and knuckles toward the lens, thumb behind, forearm back to the right over the counter (the barista's left hand, from
his side). Changed from the slide grasp: fade 9 cm toward the elbow (was 6) and crop 14 cm (was 12) so his forearm
reads; contact 1 mm further off the hull. Release: the same grasp solved 14 mm off the wall is a shape key; the hand
opens over 0.4 s, then withdraws up and back out of the frame's top right. Camera 13 deg further right than the
template (yaw -5) so the back of the hand faces the lens. No sleeve: no approved sleeve or barista arm pose holds a cup
(the barista rig is approved at rest, at the pitcher and in the saucer serve only). Clearance on every frame: cup
1.4 mm, counter 6.5 mm, no vertex inside. Easy guide, no beats.

## Rework r3 (guide-animator, owner review 2026-11-16 14:52)

Owner: "can we mirror the hand with a cup (literally)?" r2 archived in `archive/2026-11-16-r2/` (`record.r2.json`,
request, render, export, sheet, scene code copy). Camera, counter, light edge and timing unchanged. Easy guide: no beats.
- Mirror plane: the camera's vertical view plane (view direction 95 deg from +X). The same approved slide grasp
  (`T.SLIDE_GRASP` on the CC0 rig, fade 9 cm, crop 14 cm, 1 mm extra contact gap) is solved on the rig's other arm:
  the barista's right hand, palm on the cup's left (210 deg, was -20 deg), fingers across the front with their backs
  toward the lens, forearm back to the left; it enters from the screen left.
- The carry path (18 in from the far side) and the withdrawal (up and back) are mirrored with it: the hand leaves by
  the frame's top left. The takeaway cup itself is not mirrored (a near-lathe; its few scan marks stay where they were).
- Hand checks: cup 1.2 mm, counter 6.5 mm minimum on every frame; no skin vertex inside the cup by signed distance or
  by a three-ray majority parity (a single diagonal-ray parity count flags one vertex at 1.2 mm off the surface, a scan
  gap artefact).
