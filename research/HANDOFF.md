# Handoff from 01 (script researcher)

Date: 2026-10-24. Everything below is in files; start from them, not from this summary.

## Done

| Deliverable | File(s) |
|---|---|
| Category mapping: 20 production slugs to 9 kinds, 2 slugs without scripts, priority order | `research/venue_kinds.md` |
| Best practices per kind (hooks, shot orders, lengths, name/offer placement, what visitors want, what to avoid, script ideas) | `research/best_practices/<kind>.md` (9 files) |
| Commercial shot vocabulary: angles, moves (with speeds), transitions, 20 named patterns, chaining rules, phone limits | `research/commercial_shots.md` |
| Sources (F = food kinds, N = non-food kinds, S = shots) | `research/sources.md` |
| Menu audit: all 17 production venues with a published menu, 11 review kinds | `research/menu_item_kinds.md` |
| Catalog in the kit format: 9 kinds, 56 scripts, 304 steps | `scripts/script_templates.json` |
| Shot plan: one entry per step | `scripts/shot_plan.json` |
| Reasoning per script | `scripts/<kind>/<template id>.md` (food reviews in `scripts/food-review/`) |
| Overlay names the 10 old scripts used, per step | `scripts/existing_overlays.json` |
| Checker (format, limits, chaining, filler) and kit test | `scripts/tools/check_scripts.py`, `scripts/tools/kit_test.sh` |

Source of truth for the catalog: `scripts/_parts/<kind>.json`. `python3 -I scripts/tools/check_scripts.py --merge`
rebuilds `script_templates.json` and `shot_plan.json` from them and checks the result (0 errors, 0 warnings at
handoff). Edit a part, then merge; never edit the merged files by hand.

Scripts per kind (first kind listed; some scripts also list a second kind, so the app shows more per kind):

| Kind | Scripts | Shown in the app |
|---|---|---|
| coffee | cafe-first-visit, cafe-morning-ritual, cafe-before-opening, cafe-seasonal-drink, cafe-work-spot, food-review, food-review-drink | 8 |
| bakery | bakery-fresh-batch, bakery-morning-shift, bakery-sell-out, bakery-box, bakery-ask-the-baker, food-review-sweet | 9 |
| dining | restaurant-date-night, restaurant-chef-pick, restaurant-family-table, restaurant-weekend-brunch, restaurant-room-tour, restaurant-lunch-deal, food-review-table | 14 |
| fast-food | quick-order-rate, quick-truck-find, quick-budget-run, quick-late-night, quick-the-build, food-review-handheld | 9 |
| entertainment | bar-night-out, bar-tasting, bar-happy-hour, night-live-music, fun-first-try, fun-group-challenge, food-review-pour | 9 |
| beauty-salon | salon-transformation, salon-quick-tour, salon-fade, salon-nail-set, salon-brows, salon-meet-stylist | 7 |
| sport_health | fit-first-class, fit-gym-tour, fit-sauna-session, fit-coach-move, fit-treatment, fit-first-appointment | 6 |
| shopping | shop-find-of-the-day, shop-try-on, shop-budget-challenge, shop-owner-pick, shop-music-demo, shop-tour | 6 |
| services | pro-before-after, pro-meet-the-owner, pro-first-lesson, pro-quick-tip, pro-what-it-costs | 5 |

All scripts total 20 to 30 s, have 4 to 7 steps of 2 to 8 s, and use 1 to 3 deliberate transitions.

## Validation

`scripts/tools/kit_test.sh <scratch dir>` copies VideoEditorKit to a scratch folder, puts the catalog in, and runs
`swift test --filter VideoScriptsTests` twice:

- Run A, catalog as is: 18 of 21 pass. The 3 that fail are expected and can only pass after agents 02 and 03:
  `everyBundledStepHasALocalIllustration` (266 of 304 step images do not exist yet),
  `everyShotOverlayAStepNamesIsBundled` and `everyShotOverlayAStepNamesHasALiveGuide` (every `overlays` is empty
  by design, and the tests require at least one).
- Run B, same catalog with a stand-in image per missing file and one existing overlay per step: 21 of 21 pass.
  So the JSON decodes, every kind has scripts, `food-review` still features a menu item for coffee, dining and
  bakery, and pagination works.

The kit's own resource was not changed. Copy `scripts/script_templates.json` over
`VideoEditorKit/Sources/VideoScripts/Resources/script_templates.json` once images and overlays exist.

## Uncertain, or decided by judgement

- **Kinds.** `craft-beer` is replaced by `entertainment` ("Going out"), which covers bars and activity venues.
  `services-other` and `recreational-other` get no scripts. Business-services is a weak fit for `services`.
- **Lines are generic on purpose.** Bundled lines must be true at every venue of a kind, so they point at facts
  ("here is when they open", "the price is on screen") instead of stating them. The facts sweep removed
  invented hours, durations, prices, order contents, fixed scores, gendered pronouns for staff, and `$__`
  slots; the checker now rejects staff pronouns, `$__`, clock times and fixed "N out of ten" scores. Budget
  premises a creator sets ("ten dollars at this counter") stay. The development AI writer
  (`ScriptWriting.swift`) is where venue facts belong.
- **Thin menu sample.** Only 18 of 648 production venues publish a menu (one is a demo); coffee, bakery and fast
  food have 1 or 2 each. The review kinds lean on dining menus that sell the same items.
- **Phone-hard shots** kept, with directions that make them easy: flat-lay-reveal (stand, rise slowly), the
  barber holding the phone in `salon-fade/blend`, propped-phone class steps in `fit-*`. See each .md.
- **Best practices** rest partly on vendor and agency blogs, marked as directional in `sources.md`. Shot lengths
  and move speeds are mostly judgement, marked so.
- **Token list.** The README lists `pan`, `tilt`, `truck`, `orbit` without direction and adds
  `rack-focus-stand-in`. The shot plan uses the skill's directional tokens (`pan-left`, `tilt-down`,
  `orbit-right`...) and no `rack-focus-stand-in`. The README line should be updated to match.

## For agent 02 (step previews)

- 304 images, `<template id>_<step id>.jpg` (the README says `.png` in `previews/`; the kit and the JSON use
  `.jpg`). 38 exist in `VideoEditorKit/Sources/VideoScripts/Resources/StepPreviews` and still match a step id
  of a kept script; regenerate them only if the step changed (`direction` and the shot plan say what is in
  frame). The other 266 are new, including the six `food-review*` scripts, which used to borrow other scripts'
  images.
- A step's picture is its start pose: `shot_plan.json` `angle` and `start` framing, with the subject named in
  `direction`. Selfie steps show the creator from the front camera.
- People: the creator, staff who agreed, friends; never other customers' faces. No before/after of bodies.

## For agent 03 (live guides)

- Animate from `shot_plan.json`: `angle`, `start` to `end` framing, `move`, `seconds`, and the join
  (`transitionOut`) into the next step's `start`. `reads` says in one line what must visibly change.
- Moves used: static 150, push-in 85, pull-out 20, reveal-from-behind 11, truck-right 10, pan-right 9,
  tilt-down 9, orbit-right 3, truck-left 2, whip 2, pan-left 2, orbit-left 1. Joins: cut 233, match-cut 26,
  whip 22, push-through 17, pull-back-reveal 6. Angles: eye-level 131, high 78, top-down 31, low 30, pov 21,
  over-shoulder 13.
- 86 steps are selfies (front camera) and 4 are `close` (the creator close to the lens); these are spoken
  steps where the guide should stay out of the face.
- `scripts/existing_overlays.json` lists the 43 overlay names the old scripts used per step; many of the 60
  existing overlays will match patterns in `commercial_shots.md` (for example `latte_art_topdown` is
  pour-detail from top-down, `pov_door_entry` is door-push-through).
- Fill each step's `overlays` in `scripts/_parts/<kind>.json`, then merge and run the kit test; Run A then has
  to pass the two overlay tests.

## For the Loca app (outside this task)

- `VideoStudio.venueKind(for:)` in `Packages/ApplicationDomain/.../EarnTab/VideoStudio/VideoStudio.swift` maps
  only coffee, bakery, beauty-salon, dining. It needs the 9 kinds, the aliases and the priority order in
  `venue_kinds.md`; today a fast-food or food-truck venue gets dining scripts and every non-food venue gets a
  custom script only.
- Picking a food-review variant from the menu item's section title (keyword groups in `menu_item_kinds.md`)
  would let the app choose the right review for the picked dish; today the creator picks by title.
