# glass_sip_lift (new; catalog v3, owner go-ahead 2026-11-16)

Steps: drink-review/after (drinkKind iced and cold coffee; juices and smoothies; soft drinks and lemonades), title First sip.

Shot type **sip**, level **complex**, back camera, portrait, about 5 s.

Research: reference_shots/food_and_drink.md section 6 (first sip); glass_grasp.md (thenar, slide grasp); sip_cup_only as template.

Scene: Like sip_cup_only, with the approved drinking glass instead of the cup: the glass on the table, a hand (approved glass grasp from glass_slide_close__a) lifts it out of frame toward the mouth and sets it back. No straw (no approved straw; say if the iced kinds need one as an object request). Phone static at table height about 14 in away.

Beats:
- atSec 0: "Glass on the table, phone at table height."
- atSec 1.0: "Lift the glass out of frame and sip."
- atSec 3.5: "Set it back in the same spot."

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

Draft (guide-animator, 2026-11-16): this folder (record.json, render/, export/, sheet.png); scene code
`guides/blender_motion/drafts/glass_sip_lift.py`. Glass: the approved water glass (`geometry.glass`, tall straight
tumbler with a liquid line, no ice, no straw) as the hero. Grip: glass_slide_close's approved slide grasp (variant a,
`SLIDE_GRASP`, left hand) refitted to this glass's wall, with unchanged parameters. Phone in portrait, lens 5.5 in above
the table top, 14 in from the glass, 15 degrees right of straight on, 1x. The lift runs 1.0-2.3 s and leaves through
the top of the frame; the glass is out of frame from 2.3 to 3.5 s and set back 3.5-4.7 s. Beats above are kept as
written. Straw: not needed for the guide. The approved cocktail glass already carries a straw if the iced kinds should
show one, so no object request was written.

Rework (guide-animator, owner review 2026-11-17 "big thumb should be slightly lower, let move hand slightly lower as
well"): previous draft archived in `archive/2026-11-16-v1/` (record, request, render, export, sheet, scene code copy).
The approved slide grasp refit is kept (palm angle, wrist, pivot, fade, thenar unchanged); in
`drafts/glass_sip_lift.py` only the grip height drops from 0.06 to 0.055 m (about 1/4 in lower), the thumb lift from
0.35 to 0.2 (the thumb now sits below the rim instead of across it) and the forearm crop from 12 to 10 cm. Why the
hand drops only 1/4 in: at 0.05 m the little finger went 2 mm into the tabletop by the glass base, and the forearm's
cut end went 8 mm into the table, which drew a stray line. The shorter crop is hidden by the fade, which ends above it.
Clearance on every frame: glass 0.7 mm (grip contact), tabletop 3.2 mm, no vertex inside anything. Beats unchanged.
