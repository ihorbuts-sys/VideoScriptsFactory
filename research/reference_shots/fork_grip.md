# Holding a fork while eating: grips and finger placement (2026-11-12)

Why: owner note on bite_selfie_eye_v2 (round 5, 2026-11-11): "fork holding still doesn't look natural - investigate how
thumb, index and other fingers are positioned when holding the fork". Used by
`guides/blender_motion/drafts/people_v2.py` (spec `grip='tripod'`, `TRIPOD_*`, `tripod_hold`). The rejected round-2c
version (fork rolled 66.5 deg and locked to a generic fist) is not reused.

## Sources

| Ref | Source | URL | Status |
|---|---|---|---|
| FG1 | Wikipedia, Eating utensil etiquette (American and Continental styles, hidden handle) | https://en.wikipedia.org/wiki/Eating_utensil_etiquette | opened |
| FG2 | The OT Toolbox, How to hold a spoon and fork (occupational therapy feeding guidance) | https://www.theottoolbox.com/tag/feeding-evaluation/ | opened (first 100k characters) |
| FG3 | Growing Hands-On Kids, Pencil grasp development: the tripod grasp | https://www.growinghandsonkids.com/the-tripod-grasp.html | opened |
| FG4 | Gentleman's Gazette, How to eat with fork and knife | https://gentlemansgazette.com/eat-fork-knife-etiquette | opened |
| FG5 | Dynamic tripod descriptions: pencil pinched by thumb and index pads, resting on the lateral DIP joint of the middle finger (OT Mom Learning Activities, correct pencil grasp; gripping-aid patent text) | https://www.ot-mom-learning-activities.com/correct-pencil-grasp.html | search-only (snippets) |
| FG6 | Pencil grasp development summaries (static vs dynamic tripod; ring and little finger flexed and stable) | https://www.theottoolbox.com/2026/03/03/ | search-only (snippets) |
| FG7 | wikiHow, Hold a Fork (Continental: index where handle meets the tines, handle end in the palm crease) | https://kiwix.lema.org/wikihow_en_maxi_2023-03/Hold-a-Fork | search-only (page returned 401; snippet only) |
| FG8 | Drawing references for hands holding utensils (Proko "Hands holding stuff"; Posemy hand-holding guide) | https://www.proko.com/course-lesson/hands-holding-stuff-n-things | search-only (generic: no utensil-specific finger detail; photograph your own hand) |

## Findings

- Two grips (FG1, FG4, FG7):
  - Continental, tines down ("hidden handle"): fork in the left hand, the handle runs along the palm and its end sits in
    the palm crease, the index finger lies along the back of the handle near the neck, thumb and the other fingers wrap
    the handle. It is a cutting / spearing grip; food goes to the mouth tines down in Britain, tines up elsewhere (FG4).
  - American / pencil, tines up: "held much like a spoon or a pen" (FG1); "the shank is extended between your thumb,
    index and middle finger", "the hand is curved gently around the handle", "the tines are up when you put it in your
    mouth" (FG4). Continental eaters use the same pencil hold in the left hand for tines-up food (FG4).
- Finger placement in the pencil hold (FG2 fork and spoon, FG3 and FG5 tripod):
  - Middle finger: "the neck of the fork rests on the lateral side of the middle finger or the pad of the middle
    finger" (FG2); the tool rests on the side of the middle finger's last joint (FG5). It is the support underneath.
  - Index: pad rests "over the top of the neck" and guides (FG2, spoon); index and thumb pads pinch (FG3, FG5).
  - Thumb: "stabilizes the narrow part of the fork handle" (FG2), pad against the handle opposite the index (FG5).
  - Ring and little fingers: curled into the palm for stability, not touching the tool (FG3, FG6).
  - Web space between thumb and index open and round (FG3).
  - Handle end: "above the back of the hand, and not under the thumb web space into the palm"; a handle end under the
    palm pulls the hand into a primitive fist (gross) grasp (FG2).
  - Wrist: "slightly pronated and slightly flexed" (FG2).
- Drawing (FG8): no utensil-specific rule beyond drawing the object first and fitting the fingers to it.

## Grip chosen for bite_selfie_eye_v2 (judgement marked)

- Pencil (tripod) hold, tines up (FG1, FG2, FG4): she carries wound spaghetti on the tines to her lips; the
  tines-down hidden-handle grip is for cutting and spearing, and its handle-in-palm reads as the primitive fist the round-5
  note objects to (FG2). Left hand, as before (the right hand holds the phone).
- Where on the handle: the owner's mid-handle point is kept (pinch about 133 mm from the tine tips); the 67 mm of handle
  behind it runs back over the thumb web and out above the index knuckle (FG2 "above the back of the hand").
- Placements built on the rig (each finger closes until its skin is 0.5 mm off the metal, bisection, `close_finger`):
  - Middle: MCP 40 deg, PIP 50, DIP 16 (judgement); the handle's underside rests on the top of its distal phalanx,
    5 mm ahead of the pinch (FG2, FG5). Gap 0.5 mm.
  - Index: closes onto the handle's inside face from the dorsal side, MCP 21 deg, PIP 19, DIP 7 (solved). Gap 0.55 mm.
  - Thumb: pad on the palm-side edge of the handle at the pinch, its base aimed 12 mm radial so the web stays open
    (FG2, FG3). Gap 0.5 mm.
  - Ring and little: curled under the middle finger, MCP 48 / 52 deg (judgement, FG3, FG6), 28 and 55 mm clear of the fork.
  - Fork in the hand frame (judgement, tuned on the rig so the handle clears the index knuckle and lies in the web): handle
    axis toward the tines (forward .57, radial -.50, palm .62); inside face toward the index (radial .8, dorsal .6), the
    hand turned 40 deg about the handle so the fork is tines up at the lips with the radial side of the hand up.
  - Wrist: 12-40 deg between hand and forearm over the lift (limit 45; FG2 "slightly flexed", eating_arm_kinematics ER1-ER3).
- The grip is held the same on every frame (no roll in the fingers was needed; the solver may roll the handle up to
  30 deg only if the wrist would pass its limit). The fork over the plate is set by the hand (tines down and in toward
  the plate centre); it turns into the owner-approved tines-to-lips angle on the way up.
