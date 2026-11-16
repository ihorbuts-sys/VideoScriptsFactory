# Guide request: verdict_plate_after_push

- Script and step: `food-review.verdict` and `first-visit.verdict`; the step is **easy** (spoken, no beats).
- Why: every verdict guide (`verdict_eye_level_v2`, `verdict_friend_eye_v2`, `verdict_high_plate_v2`,
  `verdict_propped_rear`) shows the creator's face. Linter rule L13 (handoff 2026-11-13): a step with a face guide
  also offers a face-free guide of the same level, so a creator who stays off camera can swipe to it.
- Shot type: `verdict`. Level: easy. Camera: back. Orientation: portrait. Length: 5 s. Trigger: motion.
- Move: seated, phone at chest height about 2 feet from the finished plate; one slow, even push-in of about 8 inches
  while the creator says the verdict off camera. 0.5 s holds at both ends.
- Target frame (end, also the poster): the finished plate fills the lower two thirds, fork resting across it, cup at
  the upper right; hero inside the 28% / 35% band.
- Objects: the shared example dish after eating (a few crumbs, sauce trace), fork, cup and saucer; no new model
  beyond a "finished" variant of the dish (procedural parameter, used only by this guide). No hands, no people.
- Template: `plate_low_push_in_v2` (the push-in move) on the dish family's objects.
- Metadata: showsFace false, needsHelper false, guideVisibleToCreator true, units us.
- Pending entry: `guides/p0/guide_levels.json` `pending`.
