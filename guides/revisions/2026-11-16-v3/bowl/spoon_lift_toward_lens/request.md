# spoon_lift_toward_lens (new; catalog v3, owner go-ahead 2026-11-16)

Steps: dish-review/after (dishKind soups; bowls and sushi), title First spoonful.

Shot type **bite**, level **complex**, back camera, portrait, about 5 s.

Research: reference_shots/food_and_drink.md section 5 (first bite, lift toward the lens); eating_arm_kinematics.md (elbow low).

Scene: Seated at the bowl; one hand (approved CC0 pinch grip, as the fork guide) lifts a spoonful from the bowl toward the lens and holds; the other hand holds the phone (not drawn). Phone at chest height about 14 in from the bowl. Spoon: the approved dessert spoon. Hand-contact checks as in the fork guides. If the pinch grip on a spoon needs a new pose the owner has not approved, stop and report.

Beats:
- atSec 0: "Phone low over the bowl, spoon in the soup."
- atSec 1.0: "Lift the spoon slowly toward the phone."
- atSec 3.5: "Hold it just in front of the lens."

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

Beats as rendered (the lift runs 1.0 s to 3.5 s, then holds):
- atSec 0: "Phone low over the bowl, spoon in the soup."
- atSec 1.0: "Lift the spoon slowly toward the phone."
- atSec 3.5: "Hold it just in front of the lens."

Scene code: `guides/blender_motion/drafts/spoon_lift_toward_lens.py` (template bite_pip_dish_v2; bowl loader shared
with `drafts/bowl_steam_overhead.py`). Grip: the bite_pip_dish_v2 fork pinch, same pose, side, orientation and
attachment relative to the utensil; no new pose. The bowl is drawn as support (alpha .60): at 14 in the whole bowl
and the held spoon cannot both sit in the hero band. The bowl is drawn empty (no approved soup surface); the
serving_bowl shows small contour dots from this angle (the approved render's speckle filter is not in render_p0).
