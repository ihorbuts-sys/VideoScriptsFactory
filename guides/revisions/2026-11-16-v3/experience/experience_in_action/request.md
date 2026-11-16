# experience_in_action (new; catalog v3, owner go-ahead 2026-11-16)

Steps: venue-review/main (subject experience).

Shot type **room**, level **complex**, back camera, portrait, about 5 s.

Research: commercial_shots.md room-pan and pov; best_practices/sport_health.md and entertainment.md (action wide then POV).

Scene: A friend films the creator rig in motion on the open floor (lifting the dumbbell overhead, one rep), wide then a slow push to medium. needsHelper true. Generic motion; no other people.

Beats:
- atSec 0: "Wide: the whole move in frame."
- atSec 1.5: "Walk in slowly as the move repeats."
- atSec 4.0: "Stop at waist-up."

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

## Object request (guide-animator, 2026-11-16) - stopped before the draft

Blocked on a person pose and a grip, not on a model. The creator rig and the dumbbell are both approved, but no approved
creator pose lifts an arm above the shoulder and no approved creator grip holds a dumbbell (approved creator grips: cup
for sip, fork for bite, and the open-palm verdict gestures; coordinator rule: new grips or new person poses mean stop).

Requested (row added to `OBJECTS.md` Requests, 2026-11-16): the canonical creator, standing, one hand closed around the
dumbbell handle (fingers wrapped, thumb over), one rep from shoulder rack to overhead lockout and back in about 4 s,
free arm relaxed, feet planted. Nearest existing: `p0_people.py` `grip_digits(kind='cup')` and the CC0 `real_hands.py`
power grasp. Suggestion: a `handle` kind in `grip_digits` plus an overhead path on the existing `ArmPose` solve; line-art
stills at rack, mid-press and lockout, wide and waist-up, from a friend's chest-height back camera, for owner approval.

Planned once approved: template `entrance_friend_static` (friend-held back camera on the creator), camera from wide (full
body) with a slow push to waist-up, no other people, no floor or walls beyond one floor edge if needed. The beats above
stand as written.
