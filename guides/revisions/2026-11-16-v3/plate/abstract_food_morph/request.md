# abstract_food_morph (pilot; owner 2026-11-17)

Owner: "Regarding dishes - still want to have additional generic guides with some abstract food (what if we make the
animation of changing the food on each plate) and they should be yellow, not white-shaped." Also on the bowl and spoon
drafts: "Add some food inside (yellow lighted generic shape)".

Goal: a generic dish guide for any dish kind, beside the per-dish versions (which stay). Pilot on one approved plate
move, then the owner decides how widely to use it.

- Move: plate_low_push_in_v2 (same camera, timing, table and place setting as the approved v2 dish versions; dinner
  plate with fork and knife 2 cm clear, per STYLE.md place setting for mains).
- Food: an abstract, generic food shape on the plate - a soft mound that reads as "a portion of food" without naming a
  dish (rounded heap with two or three smaller rounded pieces beside it, a sauce/garnish curve at most). Code-built,
  new builder used only by this guide (swap-family rule; existing guides render the same).
- Change the food during the loop: the food on the plate changes shape every ~1.2 s through 3-4 abstract forms
  (heap -> stack -> two pieces -> heap), each change a short soft morph or a fade swap (pick what reads best in line art;
  say which), ending on the start form so the first and last frames match.
- Color: the food is drawn in the yellow light-edge color (the P0 accent used for light cues), not the white line art;
  plate, cutlery and table stay white. If the renderer cannot color one object's lines, add the smallest per-object line
  color option (default off) and prove other guides render the same.
- Also render a still of each abstract form alone (for the owner to approve the shapes and the yellow).
- US units in text, drafts only, no publish, no commit; archive anything replaced.

Report: how the yellow is done, the morph method, frames per form, checks, and whether the same yellow abstract food
can drop into bowl_steam_overhead and spoon_lift_toward_lens (owner asked for it there too).

## Draft result (guide-animator, 2026-11-16)

- Draft: `record.json`, `render/`, `export/` (checks passed), `sheet.png`, `morph_strip.png` (every 3rd frame), form stills
  `stills.png` (+ `stills/<form>/still.png`). Easy guide: no beats. Not published, not promoted.
- Yellow: per-object line colour `p0_line_color` (RGB custom property) in `render_p0.py`, default off; the food keeps
  the hero role (opacity 1) in its own stroke object `P0 strokes / hero / colour ...`, coloured (1, .73, .17); the
  export's warm halo picks it up as for light cues. Proof other guides render the same: plate_low_push_in_v2,
  steam_low_backlit_v2, sip_friend_side_v2 re-rendered within EEVEE noise of the published frames (the steam guide
  shows the same 0.055% with the pre-edit renderer).
- Morph: soft vertex morph (shape keys, smoothstep over 6 frames = 0.4 s), changes 18 frames (1.2 s) apart at
  frames 23, 41, 59; the third form's spare pieces hide inside a bigger piece. Fade swap was not used: contour-only
  line art has no per-object fade.
- Place setting: mains row (dinner plate 11.9 in, fork and knife 3/4 in (2 cm) clear, knife added mirroring the fork, side plate kept).

## Owner review 2026-11-17, round 2

- Owner: "regarding abstract shape - let's have our pizza/dessert/croissants/etc changing". Replace the abstract blobs
  with our approved dishes cycling on the plate, all drawn in the same yellow (p0_line_color, hero role): pasta, cut
  pizza with the pulled slice (approved look), cake slice (dessert), croissant/pastry, pancakes, salad - same placement
  and scale as the approved dish versions (plate_dishes.PLACEMENT). About 0.8-1 s per dish, ending on the first dish so
  the loop is seamless. Different meshes cannot vertex-morph: use a short scale transition (outgoing dish shrinks to the
  plate centre, next one grows, ~0.25 s each) or another swap that reads in line art; say which.
- Plate and cutlery (assumed, owner to confirm): one dinner plate for the whole cycle and no cutlery, because the cycle
  includes pizza and pastry (no-cutlery rule) and swapping plates mid-loop would distract.
- Keep the camera, timing frame and checks; archive round 1 (never delete); rebuild the drafts page. Stills: one frame
  per dish in yellow on the plate (sheet).

## Draft result, round 2 (guide-animator, 2026-11-16)

- Draft: `record.json`, `render/`, `export/` (checks passed), `sheet.png`, `cycle_strip.png` (every 2nd move frame),
  dish stills `stills.png` (+ `stills/<dish>/still.png`, one per dish at the target camera). Easy guide: no beats.
  Round 1 archived in `archive/2026-11-16-r1/` (its record renamed `record.r1.json` so the drafts page shows one card).
- Cycle: pasta, pizza (cut, pulled slice), cake slice, croissant, pancakes, salad, back to pasta; all hero role, yellow
  through `p0_line_color` (render_p0.py unchanged since round 1). A dish comes round every 12 frames (0.8 s): 0.2 s
  shrink to the plate centre, 0.2 s growth, 4-5 frames full; pasta is full through the holds (first = last frame).
- Swap: scale transition about the plate centre (pivot empty per dish); a hidden dish waits 50 m above the table.
- Placement: plate_dishes.PLACEMENT and the v2 dish versions' safe-band slide (pancakes 0.89 in, salad 1.18 in toward
  the lens, as approved). Cake slice has no approved dish version: 0.6 of the source (about 3.3 x 3.8 in, 3.4 in
  tall), turned 180 deg, loaded with the approved dot cleanup (counter_case.library_model).
- Plate: one dinner plate (11.9 in), no cutlery, no side plate (the template fork is removed), as assumed.
