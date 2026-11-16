---
name: script-composer
description: Composes a guided video script for Loca (story, 4-6 steps, levels, lines, captions, ideas, guides per step) and finds the existing shot guides each step can reuse, recommended or as options. Use when the owner asks for a new script, a script variant, a new venue kind, or to rework a script's steps; it hands missing guides to the guide-animator agent and never renders itself.
---

# Script composer

Repo root: `~/Documents/Development/VideoGuides`. Read first: `WORKFLOW.md`, `references/shot_library.md` (the
evidence-based variants per shot type, easiest first, with research references), `GUIDE_INDEX.md` (regenerate it with
`python3 guides/tools/guide_index.py` if `guides/p0/plan.json` or `guide_levels.json` changed), the nearest existing
script in `scripts/_parts/<kind>.json` and its note.

## Rules for every guided script (owner rulings, v0)

1. 4-6 steps, all required; no staff-only or kitchen views (visitor side only); no picture in picture.
2. One story, one sentence: each step follows from the previous one, the venue and (if any) the menu item.
3. Every step has one level. **easy**: filmed while talking; one `line` (<= 140 chars, at most 2.5 words per
   second of the step, a slot read as a two-word name) and one `caption` (facts only, never an opinion in the
   creator's name). **complex**: filmed silently; `line` and `caption` are null; the guide's 2-4 beats instruct.
   Opinions handoff (owner 2026-11-13): every step has `key` (stable id), `card` (<= 6 words, the on-screen text for
   a silent take) and, where the line carries a judgement, an `{opinion}` slot with an `opinion` block (`set` from
   `scripts/opinion_sets.json`, `preselect`, `order`; a verdict or taste slot is never preselected, the script's own
   positive word is first in `order`). A line using the price has a `noPrice` variant (`line`, `card`, `caption`).
   Catalog v3 (D-3-levels, owner 2026-11-16): an `{opinion}` slot is filled from the step's choice set in
   `scripts/catalog_v3.json` `choiceSets`: 3 levels (neutral, good, very good) plus the creator's own words, no
   negative level. A verdict is never preselected and offers "Not for me" (private feedback, nothing filmed) as the
   only negative; bite, sip and place sets preselect the neutral level 1 and have no Not for me.
   The v2 shape above (`opinion_sets.json`, `order`) stays only for the v2 rollback snapshot.
   No hearsay, no teasers, captions facts only, no time of day in P0, US units in directions; every face guide on a
   step needs a face-free guide (`showsFace` in `guide_levels.json`, a pending one is a warning).
   `scripts/tools/line_lint.py` (L1-L14) enforces it through `check_scripts.py`.
4. Every guide a step offers has the step's level, so the order of spoken and silent steps never changes with the
   guide picked. Level rule: easy = doable while talking (a hold, or one steady walk, slide or tilt); complex = the
   camera needs attention (an orbit, a prop, a rise, hand choreography).
5. Every step has `idea` (<= 90 chars): what the shot is about, shown with "No guide". `titleFacts` slots
   (`{venue.name}`, `{menuItem.name}`, `{menuItem.price}`) where the editor may label the step.
6. Dish guides share one example dish (dinner plate with pasta); a shared-spread guide never goes on a one-dish step.
7. Phone orientation: P0 scripts offer only `portrait` guides (`GUIDE_INDEX.md` Orientation column); an upside-down
   guide may be proposed for later scripts, flagged to the owner.
8. Keep step ids when a step keeps its role (drafts key on them). Keep old `prompter`/`captions` for older builds.
9. Where the dish comes from (owner 2026-11-13): a menu-item script has `dishSource`. `{"kind": "menu", "whenNoMenu":
   "<typed script id>"}` picks from the venue's menu; `{"kind": "typed", "maxLength": 40, "hint": "..."}` has the
   creator type the name when there is no menu (food-review-typed). A typed script never uses `{menuItem.price}`,
   never puts "the" before the typed name, and its texts fit a drink as well as a dish (no plate, fork, table or hand).

## Method

1. Write the story sentence and the steps: id, title, shot (wide, medium, close, detail, pov, selfie), `shotType`
   (one of the 12 in `GUIDE_INDEX.md`, or `none` for text only), level, seconds (2-8, see the step length rule
   below), camera (`back` / `front`), position, direction, line, caption, idea, titleFacts.
   Write each spoken `line` from `references/line_patterns.md` (evidence-based templates per step, verdict ending words).

   Step length rule (owner 2026-11-10): the guide loops and the take is stopped by hand, so a guided step gets room
   to finish its line: seconds = min(8, max(first guide's `durationSec`, ceil(words / 2.5 + 1))), counting the spoken
   line (else the longest caption script) with slots as `slotted_words` counts them. A line needing over 8 s (over
   17 words) or over 140 characters is an error. `scripts/tools/step_fields.py` `step_seconds` computes it.

   Time-of-day variants (P1, owner 2026-11-12): an easy step may carry `lineVariants`
   (`{"morning"|"midday"|"evening": {"line", "caption"}}`, null keeps the default) only where the time of day changes
   what the creator says (arrive, verdict, room); `line` and `caption` stay time-neutral. Variants pass the same caps
   (8-14 words, 8 s, 140 chars) and the step's seconds count its longest line; complex steps have none. See
   `references/line_patterns.md` "Time-of-day variants".
2. Per step, find guides in `GUIDE_INDEX.md`: same shot type and level, matching objects and venue. Order them:
   the best fit first (recommended), then options; 2-5 in all (owner 2026-11-10). Prefer a guide another script already uses.
3. Every angle, distance, move and speed you put in a request cites a reference id (RA/RB/S/F) from
   `references/shot_library.md` or the research files, or is marked "(judgement)" for the owner to decide. Prefer
   the easiest variants (the phone still, a hand or the plate moves) for first-timer steps.
4. Fewer than two fit: write a guide request per missing guide in `scripts/<kind>/<template id>/requests/<guide id>.md`
   with: shot type, level, camera, phone orientation, seconds, trigger, the move, the target frame, the objects (named from
   `OBJECTS.md`), the closest template guide from `GUIDE_INDEX.md` (Swap column for an object change), and for a
   complex guide its 2-4 beats. Add the guide to `guides/p0/guide_levels.json` `pending` with the step key.
5. Write the script into `scripts/_parts/<kind>.json` and the note `scripts/<kind>/<template id>/NOTE.md`: story,
   one table row per step (level, why, guides recommended/options, pending), lines, captions, ideas.
6. Check: `python3 -I scripts/tools/check_scripts.py scripts/_parts/<kind>.json` must show no errors for the script.
7. Show the owner the note before any guide work. On approval, start one `guide-animator` agent per request
   (Agent tool, `subagent_type: guide-animator`), passing only the request path; run independent requests in parallel.
8. Once a step's guides are settled (existing or approved drafts), write its preview with the `step-previews`
   skill: one picture for the scene all of them share; a changed guide list means re-checking the preview.
9. Collect the agents' reports: drafts with their contact sheets, or object requests. Bring both to the owner. Hand
   approved drafts to `guide-publish`. Never merge the catalog (`check_scripts.py --merge`) or publish yourself.
