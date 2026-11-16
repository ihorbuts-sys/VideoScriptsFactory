# truck_window_handoff (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/main (serviceKind truck); also dish-review/order as an option.

Shot type **handoff**, level **easy**, back camera, portrait, about 5 s.

Research: reference_shots/food_and_drink.md section 8 (hand-off); best_practices/fast-food.md (window to car).

Scene: The paper tray with the closed paper wrap slides out onto the truck's window counter toward the lens; static phone at eye level. No hands unless an approved grip fits (say which).

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

## Draft (guide-animator, 2026-11-16)

Draft rendered in this folder (`record.json`, `render/`, `export/`, `sheet.png`); scene code
`guides/blender_motion/drafts/truck_window_handoff.py`. Easy guide: no beats. Grip: the approved palm-down slide pose of
handoff_counter_cup_v2 (as reused by venue_order_arrives), fingertips on the paper tray's back rim instead of the saucer
rim; no new grip. The cache's window ledge is only about 6 in deep with a sill hump behind it, so the 0.36 x 0.27 m
(14 x 10.6 in) tray rests on the sill crest and the ledge edge, tilted about 12 deg toward the lens, and slides only
about 5 in (the longest slide on which the tray stays supported). Owner to confirm the tilt and the short slide.

## Rework r2 (guide-animator, owner review 2026-11-17)

Owner: "can it be the cooker (we can use barista) who gives us the order?" v1 archived in `archive/2026-11-16-v1/`.
Same static camera and 5 s. Easy guide: no beats.
- The cook: the approved barista rig in the serve pose of counter_hand_receive (`barista.add_serve`), no new arm pose.
  He stands inside the truck behind the window facing the lens, leans over the sill and slides the tray with his own
  right hand (palm down, fingers closed onto the back rim), left hand resting palm down on the sill. He lets go, straightens
  up, turns away and walks out of the window to the left (gone before 75%). The detached CC0 slide hand of v1 is
  removed.
- Template values moved with the truck, in memory for this guide only: his floor 0.11 m above the street (the
  template counter-to-floor height under the tray landing); left rest 3 cm higher (sill hump); middle knuckle 5 mm
  higher; walk straight left (the template diagonal would cross the inner counter), step back 4 cm, 2.2 m walk (the
  template's 1.1 m/s over this 5 s guide); release at u 0.50 (the pose's own clock: it straightens up from u 0.52,
  so the v1 release at 0.55 dragged the gripping hand back over the rim).
- Tray: starts at y -0.975 (already at the landing tilt of about 12 deg) instead of on the sill crest at 6 deg, so
  there is no tilt snap mid-slide; the slide is about 4.5 in (v1 5.3 in).
- Dots: truck strokes under 12 px removed per frame, this guide only.
- Open for the owner: the cook's face is toward the lens while serving (the owner exception of counter_hand_receive);
  the top of his hair is cropped by the frame edge while he leans in.

## Rework r3 (guide-animator, owner review 2026-11-16 14:51)

Owner: "barista should slide the order slightly faster". r2 archived in `archive/2026-11-16-r2/` (`record.r2.json`,
request, render, export, sheet, scene code copy). Same camera, cook, tray path and 5 s. Easy guide: no beats.
- Slide: u 0.06-0.37 (0.3-1.85 s, 1.55 s) instead of u 0.06-0.50 (2.2 s): 30% shorter, same 4.5 in path and ease.
- Release: the serve pose's after-release clock (hand lift, straighten up, turn, walk) moves 0.06 earlier, in memory for
  this guide only (`SERVE_SHIFT_U`); the hand now lifts off the rim for 0.35 s before he straightens up (r2: 0.1 s).
  The r2 one-frame finger dip (2.4 mm into the tray rim, frame 48) is gone: deepest hand-to-tray contact on any frame
  0.42 mm (fingertip pads on the rim during the push, r2 had 0.2 mm there). He is out of the window earlier (walk ends
  at u 0.92), so the empty-ledge hold before the loop is longer.
- Still open (carried from r2, now 1 frame instead of 2): at frame 51, as he turns, his left hand's fingers pass up to
  2 cm into the sill hump (z 1.05 m, just above the fade floor); in the frame it reads as fingers behind the sill line.
  The fix belongs in the shared serve pose's left-hand lowering (`barista.add_serve`), not changed here.
