# experience_gear_up (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/before (subject experience).

Shot type **detail**, level **complex**, back camera, portrait, about 5 s.

Research: commercial_shots.md pov-pick; best_practices/sport_health.md (gear, briefing).

Scene: POV: a hand (approved CC0 grip) reaches in and picks up a dumbbell (approved) from the floor rack; phone at chest height looking down about 30 deg. Generic gear: the dumbbell stands for any gear (helmet, racket) until per-kind props exist.

Beats:
- atSec 0: "Phone pointed at the gear."
- atSec 1.0: "Reach in and pick it up."
- atSec 3.5: "Hold it up in front of the lens."

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

- Hands: picking up the dumbbell is a new grip. The CC0 hands are approved only in their three owner-requested grips
  (bite_pip_dish fork, glass_slide_close, pancake_clear_path). The `real_hands.py` `wrap` power grasp is fitted to an
  upright glass, not to a thin horizontal handle that lifts with the hand. Request row added to `OBJECTS.md` (one hand
  picking up the dumbbell).
- Floor rack: no approved dumbbell rack. The legacy `venue_assets.rack(kind='dumbbell')` was never rendered in P0 line
  art, and its procedural dumbbell was rejected on 2026-11-11. Request row added to `OBJECTS.md` (dumbbell floor rack).
  The alternative is to drop the rack: the dumbbells rest on the floor with one faint floor edge line.
- The dumbbell itself (Tripo, 12.6 in long) is approved 2026-11-16 and fits the request.
- Planned once approved: template glass_slide_close (closest guide where a CC0 hand holds an object), portrait, phone
  static at chest height about 4.3 ft, pitched down about 30 deg, dumbbell about 2 ft ahead. The hand enters from the
  bottom edge at 1.0 s, lifts the dumbbell from 3.5 s and holds it about 14 in from the lens. The target frame is the
  dumbbell resting on the rack, so the first frame equals the last: the hand puts it back during the 7 end frames, or
  the owner picks a held target. Metadata: showsFace false, needsHelper false, guideVisibleToCreator true, units "us",
  zoomHint none. These are judgement numbers, not yet checked against `references/framing.md`.
- Beats as requested (2 to 4, ascending, each under 70 characters): 0 "Phone pointed at the gear.", 1.0 "Reach in and pick
  it up.", 3.5 "Hold it up in front of the lens."
