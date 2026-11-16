# handheld_hold_turn (new; catalog v3, owner go-ahead 2026-11-16)

Steps: dish-review/main (dishKind handhelds; pastry and bakery).

Shot type **plate**, level **complex**, back camera, portrait, about 5 s.

Research: brief scripts/food-review/food-review/requests/handheld_hold_turn.md; commercial_shots.md hero-push and cut-reveal.

Scene: Follow the existing brief: the burger (approved) held in two hands in its opened paper wrap, turned slowly a quarter turn toward the lens, phone static at chest height about 16 in away. Two attached hands at most.

Beats:
- atSec 0: "Hold it up in both hands, wrap open."
- atSec 1.0: "Turn it slowly toward the phone."
- atSec 3.5: "Stop when the cut side faces you."

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

## Animator result 2026-11-16: blocked on object requests (no draft rendered)

- Hands: the two-hand hold and quarter turn is a new grip. The CC0 hands are approved only in their three
  owner-requested grips (bite_pip_dish fork, glass_slide_close, pancake_clear_path); the brief itself marks the hold
  as "a new grip that needs approval". Request row added to `OBJECTS.md` (two hands holding the opened wrap).
- Cut side: `assets.paper_wrap(opened=True)` is rotationally symmetric (lathe sleeve, filling, bun dome), so a quarter
  turn changes nothing on screen and there is no cut face; the Tripo `burger` is whole and has no wrap. Request row
  added to `OBJECTS.md` (cut variant of the opened wrap), with the alternative of dropping the cut from the beats.
- Brief vs request (owner decides): the brief says one hand at most, far side, and the food is lowered to the tray
  at 3.5 s; this request says two hands, no tray, stop with the cut side facing the lens.
- Planned once approved: template `glass_slide_close` (closest hand-holding table guide), phone static at chest
  height about 16 in from the wrap, opened wrap as hero, no cutlery (handheld place setting), no tray in frame.
