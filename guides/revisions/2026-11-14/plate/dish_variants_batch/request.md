# Dish variants, batch (owner go-ahead 2026-11-14)

Pilot approved (plate_low_push_in__pastry, __pancakes, __pizza, __salad; decisions/drafts-2026-11-14.json). Owner
rulings: the pizza may be framed a little wider than the other dishes (camera refit for the pizza only is accepted);
go ahead with the batch for the dish guides that swap cleanly.

Build a batch mode first: one command renders every dish variant of a guide (and a list of guides) in parallel (4 at
a time on this Mac), reusing the pilot's dish settings from `guides/blender_motion/drafts/plate_dishes.py` (move the
per-dish placement into a small table keyed by dish, scaled to each guide's plate; no shared builder changes beyond
parameters defaulting to current behaviour; swap-family rule: template guides render the same, proved by a scratch
frame compare per template).

Dishes (same as the pilot): pastry, pancakes, pizza (flat 10 in, 8-cut with one pulled slice, round turned 30 deg,
solid cut faces; camera refit allowed for the pizza only, report how much), salad. Pasta stays the published render.

Guides (the pilot's "swap cleanly" list; confirm each from its scene code and poster before rendering, skip with a
one-line reason if the dish is out of frame or the swap does not read - guide-objects rule "re-render only visible"):
plate_low_push_in_v2, plate_high_orbit_v2, plate_rise_overhead_v2, plate_top_orbit, plate_tissue_slide,
handoff_plate_lands, handoff_plate_lands_v2, room_tilt_up_from_plate, verdict_high_plate_v2, plate_turntable (the dish
turns with the plate). Not the bite guides, not table_spread_orbit, not pancake_clear_path.

Per variant: draft folder `guides/revisions/2026-11-14/plate/dish_variants_batch/<guide>__<dish>/` with record.json
(copied from the template, `dish` set, US units), render, export (passed checks), sheet; one side-by-side sheet per
guide (pasta + 4 dishes). Then rebuild the drafts page: `python3 -I guides/tools/drafts_review_page.py 2026-11-14`.
Drafts only, no publish, no commit; archive anything replaced (never delete).

Report: per guide which dishes rendered or were skipped and why, any dish that reads poorly at that angle, camera
refits (pizza), render time, the batch command, and anything that needs an owner decision.

## Batch done 2026-11-14 (guide-animator)

Command: `$PY guides/blender_motion/dish_batch.py [guide ...] [--dishes ...] [--jobs 4]` (all 10 guides x 4 dishes by
default); `--compare-templates <scratch>` re-renders the templates and compares frames with the published ones.
Scene code: `drafts/dish_variants.py` (wraps each template, replaces the pasta on its plate, carried by the plate root,
turntable pivot, slide carrier or held plate); per-dish placement table `drafts/plate_dishes.PLACEMENT` (pilot values,
moved only; pilot scene hashes identical). `render_p0.py`: the plate_tissue_slide fit rule also applies to its `__dish`
ids (template unchanged). Results per variant: `batch.json`; per guide: `<guide>__dishes.png`.

38 rendered, export passed; 2 skipped:
- plate_tissue_slide__pizza: lens about 3 in above the table, the flat 10 in round is a sliver wider than the frame.
- verdict_high_plate_v2__pizza: the plate-size crust covers the rim where the waiter-grip thumb rests (about 3/8 in
  inside the crust); needs its own grip.

Swap-family check: all 10 templates re-rendered from current code vs published frames: 9 within EEVEE noise (at most
0.03% of pixels over 8 levels); room_tilt_up_from_plate 2.3% spread over the dense room frame, visually identical,
scene geometry hash unchanged by this work.

Camera: the template camera is kept (the template's own safe-band fit is applied first). Pizza refits (render_p0,
along the template's line of sight): plate_low_push_in_v2 and plate_turntable 11.3 in back/up (8 in up), plate_high_orbit_v2
11.9 in, handoff_plate_lands_v2 8.9 in, handoff_plate_lands 0.9 in; overhead guides and room_tilt none. Non-pizza:
pancakes slid 0.9 in toward the lens on the plate (low_push_in_v2, turntable), no refit; salad slid 1.2 in and still
needs a 1.1 in camera pull-back in low_push_in_v2 and turntable (owner decision).

Beats (unchanged from the templates; the dish does not change the move):
- plate_high_orbit_v2__*: 0 "Elbows on the table, plate in the middle of the frame." / 1.0 "Swing the phone around the
  plate at one even pace." / 3.0 "Keep the same distance until the plate is centred."
- plate_rise_overhead_v2__*: 0 "Stand, phone flat above the plate, plate filling the width." / 1.0 "Raise the phone
  straight up slowly; keep it flat." / 3.0 "Stop when the cup and fork are in frame."
- plate_top_orbit__*: 0 "Stand, phone flat above the plate, cup and fork in frame." / 1.0 "Turn the phone slowly around
  the plate; keep it flat." / 4.0 "Stop after an eighth of a turn, the fork upright on the left."
- plate_tissue_slide__*: 0 "Rest the phone's bottom edge on a napkin." / 1.0 "Slide it left to right along the near table
  edge." / 3.0 "Keep the lens on the dish; don't slide into it."

Owner decisions: (1) pizza refits of 9-12 in are much more than "a little wider" (the push ends wider than the pasta
version starts); accept, or a smaller pizza for these guides; (2) salad 1.1 in pull-back in two guides; (3) pancakes
read weakly overhead (rise, top orbit) and in the small held plate (verdict).

## Owner review 2026-11-15 (decisions/drafts-2026-11-14.json, read every comment)

Approved as they are: plate_rise_overhead_v2__salad, plate_tissue_slide__salad, plate_top_orbit__salad,
plate_turntable__salad. Every other variant is "needs work"; the comments reduce to a per-dish place setting. Build it
as one table (`PLACE_SETTING` beside `PLACEMENT` in drafts/plate_dishes.py) applied by dish_variants.py to every guide,
then re-render the needs-work variants with the batch command:

| Dish | Plate | Cutlery and side items |
|---|---|---|
| pastry | smaller dessert plate (about 8 in instead of the 11.8 in dinner plate) | none: no fork, knife, spoon or side plate |
| pizza | dinner plate as now | none: no fork, knife or spoon |
| pancakes | smaller dessert plate (about 8 in) | fork and knife kept, each moved 2 cm (3/4 in) further from the plate edge, re-aligned to the smaller plate |
| salad | dinner plate as now | fork and knife both present (room_tilt_up_from_plate__salad is missing the knife: fix), each 2 cm further from the plate |

Also:
- Pancakes from overhead (plate_rise_overhead_v2__pancakes, and check plate_top_orbit): "not obvious what is on the
  plate"; make the stack and topping read naturally from the top (edge layers or a visible offset stack, syrup drip
  over the edge, berries/butter that read from above). Approved objects only; if it needs a new topping shape, say so.
- verdict_high_plate_v2 (all dish variants): owner doubts the shot itself: "no one will pick the plate with the dish to
  show it closer; maybe better just to put the plate on the table so it's in the shot". Render the dish variants with
  the plate resting on the table in frame (creator unchanged, no held plate, no waiter grip), and report whether the
  published pasta template should change the same way (owner decides; do not touch the published template). The
  pizza variant then needs no grip either: render it too.
- plate_tissue_slide__pizza stays skipped (lens too low).
- Pizza camera refits: no comment from the owner on framing; keep as rendered, list them again.
- Template guides and approved variants must render the same (swap-family check). Archive every replaced variant
  (never delete); rebuild the drafts page.

## Owner review rework done 2026-11-15 (guide-animator)

Command: `$PY guides/blender_motion/dish_batch.py [guide ...] [--dishes ...] [--jobs 4]`. Owner-approved variants
(the four salads above) are never re-rendered or archived; `--compare-templates <scratch>` now also re-renders them and
compares with their draft frames. Every replaced variant is in `archive/guides/2026-11-14/dish_variants_batch/`
(logged in `archive/guides/2026-11-14/ARCHIVE.json`).

Scene code: `drafts/plate_dishes.PLACE_SETTING` (pastry and `dessert`: about 8 in dessert plate, no cutlery and no
side plate; pizza: dinner plate, no cutlery; pancakes: dessert plate, fork and knife 3/4 in (2 cm) clear; salad:
dinner plate, fork and knife 2 cm clear). `drafts/dish_variants.py` applies it: the dessert plate is the approved
dinner plate scaled 0.673; a missing knife is added mirroring the fork (room_tilt, low_push_in_v2, high_orbit_v2,
tissue_slide, turntable, verdict); "2 cm clear" is measured from the plate edge to the nearest point of each piece (the
coordinator's STYLE rule; in the overhead guides this brings the cutlery in from the template's 1 1/2 in); a piece
closer than 3/8 in to the cup, saucer or glass slides toward the diner (room_tilt salad knife 1.2 in, overhead
pancakes knife 0.2 in). Rim grips (turntable, handoff_plate_lands_v2) follow the smaller rim: 1.9 in in, 0.1-0.4 in
down. Triangle dots follow the moved cutlery, or move to the plate rim where cutlery was removed.

Pancakes overhead (rise_overhead_v2, top_orbit): the approved stack's own parts rearranged
(`plate_dishes.OVERHEAD_PANCAKES`): layers offset in turn so each rim shows as a crescent, three syrup drips over the
visible edge, cream and berry off-centre, two more of the approved berries on the top layer. No new shape.

verdict_high_plate_v2 (all four dishes, pizza included): plate resting on the table in front of her, 3 3/4 in to her
right of the table axis, so the dinner plate is 2 1/4 in clear of her left forearm resting on the table and the fork fits in
between (1 in clear); no held plate, no waiter grip; she keeps the template nod (`people_v2` spec flag `nod`, default
off). The plate shows only in the bottom quarter of the frame, cut by the frame edge, inside the bottom 35% the editor
keeps clear: the selfie camera and face band leave no room for a plate on the table higher in frame. Recommendation:
do not change the published pasta template this way (owner decides); if the shot stays, a held plate or a higher,
steeper lens is needed.

Swap-family check (all templates and the four approved variants re-rendered from the final code): templates within
EEVEE noise (at most 0.036% of pixels over 8 levels; room_tilt_up_from_plate 2.3%, the same as 2026-11-14); approved
variants 0 to 0.017% (tissue_slide salad bit-identical).

Results: 39 rendered and passed export (35 needs-work plus verdict pizza, now rendered), 4 approved kept,
plate_tissue_slide__pizza still skipped (lens too low). Pizza refits unchanged: low_push_in_v2 and turntable 11.3 in,
high_orbit_v2 11.9 in, handoff_plate_lands_v2 8.9 in, handoff_plate_lands 0.9 in, overhead and room_tilt none.
Salad in low_push_in_v2 still needs its 1.2 in pull-back (open owner decision from 2026-11-14).

Beats unchanged from the templates (see the 2026-11-14 section).

## Owner review 2026-11-16 (decisions/drafts-2026-11-14.json): two variants reworked (guide-animator)

Every other variant is approved. Re-rendered with the batch command, one guide at a time:
`$PY guides/blender_motion/dish_batch.py handoff_plate_lands_v2 --dishes pizza`, then
`... verdict_high_plate_v2 --dishes pancakes`. The replaced drafts are in `archive/guides/2026-11-14/dish_variants_batch/`
(`handoff_plate_lands_v2__pizza_135103`, `verdict_high_plate_v2__pancakes_135224`, logged in ARCHIVE.json).

- handoff_plate_lands_v2__pizza ("make fade for the other hand of the end"): the pizza refit (8.9 in back) showed the
  server's whole forearm down to its cut end, about 15 1/2 in from the grip, while the template's frame edge crops it
  at 10-12 in. The forearm now fades out 12 1/2 in from the grip (`dish_variants.HAND_FADE`, read by render_p0 as the
  hand's `p0_grip_fade`; hands without it keep the old radii). Hand pose, path and timing unchanged; the hand still
  leaves through the top edge about 6 frames later than in the template (wider frame; out of frame by frame 60 instead of 54).
- verdict_high_plate_v2__pancakes ("fork and knife on the opposite side, from the reviewer's point of view"): fork and
  knife swap sides of the dessert plate as seen in the exported (mirrored) frame: fork on the right, knife on the
  left (her right and left), both still 2 cm (3/4 in) clear of the plate edge; the knife is 2 3/4 in clear of her
  resting hand (`dish_variants.SWAPPED_CUTLERY`).

Swap-family check: handoff_plate_lands_v2 and verdict_high_plate_v2 re-rendered from the final code vs the published
frames (scratch): within EEVEE noise (at most 0.015% and 0.006% of pixels over 8 levels). Beats unchanged (the template's).

## Owner 2026-11-17: generic cycling version for every food guide

Owner: "abstract_food_morph - let's generate all food guides in such way (additionally)". The round 2 pilot
(guides/revisions/2026-11-16-v3/plate/abstract_food_morph: approved dishes cycling on one dinner plate, all drawn in
yellow via p0_line_color, scale swap, 0.8 s per dish, loop ends on pasta, no cutlery) becomes a `generic` dish version
for each guide that already has dish versions here.

- Add `generic` to the batch tool as a dish: the cycle from drafts/abstract_food_morph.py (reuse it, do not copy it),
  placed on whatever carries the dish in each template (plate root, turntable pivot, slide carrier, held/table plate).
- Guides: the 10 templates of this batch (plate_low_push_in_v2 already has the pilot; reuse it as its generic version,
  no re-render). Skip a guide with a one-line reason if the cycle does not read there (e.g. dish too small or out of
  frame most of the clip).
- Before running: update dish_batch.APPROVED to every variant the owner has approved (decisions/drafts-2026-11-14.json:
  all approve choices) so nothing approved is re-rendered or archived; run only `--dishes generic`.
- Keep each template's camera; if a dish in the cycle overflows the band, use the approved per-dish slide, never a
  per-dish camera move inside one clip.
- Drafts only, archive replaced files, rebuild the drafts page for 2026-11-14; record per guide in batch.json.

## Generic versions done 2026-11-16 (guide-animator)

Command: `$PY guides/blender_motion/dish_batch.py --dishes generic` (all 10 templates; `generic` is not in the default
dish list). 9 rendered and passed export, 13 min 38 s wall for the batch (3-8 min per guide, 4 at a time);
plate_low_push_in_v2 reuses the pilot (`dish_batch.REUSED`, not re-rendered); none skipped. Per variant:
`<guide>__generic/` with record.json (`dish: generic`, title "(any dish)"), render, export, `sheet.png`,
`cycle_strip.png` (every 2nd move frame). Per guide: `<guide>__dishes.png` now shows pasta plus every version (generic
column: target on top, middle frame below); the previous sheets are archived (`archive/guides/2026-11-14/dish_variants_batch/*__dishes_1511*.png`, ARCHIVE.json).

- Scene code: `drafts/abstract_food_morph.py` now builds `<template>__generic` with the pilot's own code (the same
  build function, template as a parameter; the pilot path is unchanged: re-rendered within EEVEE noise of its draft
  frames, 75 frames, 8 bit-identical, at most 0.046% of pixels over 8 levels). dish_variants.py, plate_dishes.py and
  render_p0.py are untouched, so templates and approved variants render as before.
- `dish_batch.APPROVED` = every approve choice in decisions/drafts-2026-11-14.json (37 batch ids; the two reworked
  needs-work variants stay out); none was re-rendered or archived.
- Cycle: pasta, pizza, cake slice, croissant, pancakes, salad, back to pasta; 0.2 s shrink + 0.2 s growth, each middle
  dish full 4-5 frames (about 0.8 s per dish). The 5 s (plate_top_orbit) and 6 s (verdict) clips keep 0.8 s per dish
  and give the spare time to pasta at the start and end of the move (7 + 7 and 15 + 14 frames).
- plate_tissue_slide: pizza is left out of the cycle (its dish version is skipped, lens too low).
- Overhead guides use the approved overhead pancake arrangement.
- Camera: every template camera kept exactly (0 mm against the published target). Approved per-dish slide only
  (keep_in_band, as the dish versions): plate_turntable cake 1.2 in, pancakes 0.9 in, salad 1.2 in toward the lens.
- Band overflow during the cycle (no per-dish camera move; owner to judge): pizza in plate_turntable (bottom row 0.10),
  plate_high_orbit_v2 (0.15), handoff_plate_lands_v2 (0.23), handoff_plate_lands (0.35, marginal); cake and salad in
  plate_turntable top 0.736 / 0.733 after the 1.2 in slide (band 0.714). Same pizza case as the approved pilot.
- Roles: the food keeps the template pasta's role: hero everywhere, support in room_tilt_up_from_plate and
  verdict_high_plate_v2 (the plate is below the band by design there).
- Place setting: one dinner plate, no cutlery, no side plate for the whole cycle (as the pilot); plate_high_orbit_v2
  loses its side plate.
- Reads weakly: the cake slice in plate_tissue_slide (lens near table height, its scan dots show on the layered side);
  handoff_plate_lands_v2 changes the dish while the server's hand is still over the plate.

Beats unchanged from the templates (see the 2026-11-14 section).
