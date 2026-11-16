# plate_low_push_in dish variants (pilot; owner go-ahead 2026-11-14)

Owner: "use dynamic asset of different dishes for animation" -> option A, one render per dish kind; pilot on one
plate guide before the rest (about 10 dish guides x 5 dishes).

Guide: the plate_low_push_in version served on the P0 food-review dish step (check `guides/p0/promoted.json` and the
step's `guides`: `plate_low_push_in` or `plate_low_push_in_v2`; use the served one and say which).

Variants (same move, camera, light, timing, table and props; only the dish on the plate changes):
- pasta: the current published render (no re-render; reference only).
- pastry: the procedural `pastry` (two-half croissant) from `assets.py`, on the same plate.
- pancakes: the procedural pancake stack from `p0_table_compositions.py`, scaled to the plate.
- pizza: one or two slices of the approved Tripo pizza (`slice_round`), on the plate.
- salad: the approved Tripo salad portion, on the plate.
No burger (line art not approved). No new models, no Tripo, approved objects only (guide-objects skill).

Rules: the dish is a parameter used only by the new variant ids (`plate_low_push_in__pastry` and so on); the template
guide renders the same, proved by re-rendering it to scratch and comparing frames. Keep the dish's framing (hero
rows at the target frame) within a few percent of the pasta version; scale each dish to read as a real portion on a
0.30 m plate. US units in any text. Drafts only, no publish, no commit.

Output per variant in this folder: export/<id>.png (looping guide), poster, record.json (copied from the template,
with `dish` set), contact sheet; plus one side-by-side sheet of all five target frames. Then rebuild the drafts page:
`python3 -I guides/tools/drafts_review_page.py 2026-11-14`.

Also report: render time per variant (to size the batch mode), any dish that does not read at this angle, and
which other dish guides would swap cleanly versus need their own move (bite guides).

## Owner review 2026-11-14 (drafts-2026-11-14.json)

- Approved: plate_low_push_in__pancakes, plate_low_push_in__pastry, plate_low_push_in__salad (leave them as they are).
- Needs work: plate_low_push_in__pizza - "put full pizza model which we have. This one doesn't look obvious."
  Re-render only the pizza variant with the whole approved Tripo pizza (uncut round, no pulled slice), scaled to sit
  on the 0.30 m plate as a real small pizza, same camera and timing; archive the slice version in
  archive/guides/<date>/ (never delete); rebuild the drafts page so the pizza card returns for review.

Re-render done 2026-11-14: whole uncut Tripo pizza, scale 0.62 (7.4 in personal pizza; 8 in and larger pushed the
near crust under the bottom hero row and made render_p0 pull the camera back), centred 3 cm behind the plate centre,
template camera unchanged, export passed. Slice version archived in archive/guides/2026-11-14/ (ARCHIVE.json).

## Owner review 2026-11-14, round 2

- plate_low_push_in__pizza: "the pizza should be cut with one shifted slice (we have on some shots such pizza)".
  Use the same cut pizza as table_spread_orbit (`p0_table_compositions.slice_round`, 8 slices, one pulled out),
  the whole round on the plate (not two slices), at the size that fits the fixed camera (about 7.4 in, as round 1),
  pulled slice toward the lens so it reads at this low angle. Same camera and timing. Archive the uncut version
  (never delete) and rebuild the drafts page so the pizza card returns. This matches the OBJECTS.md owner note.

Re-render done 2026-11-14 (round 2): the Tripo pizza cut by `slice_round` (8 slices, as table_spread_orbit), slice
pulled toward the lens by 0.022 of the source (about 1/2 in), crust lifted 0.006 m; scale 0.62 (7.4 in), centred 3 cm
behind the plate centre as round 1. Template camera unchanged (target hero rows 0.361 to 0.532, round 1 0.360 to
0.532); a longer pull or moving the round further back either pulled the camera back about 1 cm or lifted the pizza
onto the plate rim. Export passed. Uncut version archived in archive/guides/2026-11-14/plate_low_push_in__pizza_uncut
(ARCHIVE.json round 2).

## Owner review 2026-11-14, round 3

- Owner: "I don't see the pulled slice." Confirmed on the poster: the 1/2 in pull reads only as a segment of the
  near crust; no gap shows.
  Make the pulled slice obvious at this angle: a clearly visible gap (empty table/plate showing between the slice
  and the pizza along both cut edges, at least about 15 px wide on the 405 px poster) and the slice clearly outside
  the round's outline. Options to combine, in this order: pull at an angle (front-right, about -50 to -60 deg) so a
  side gap faces the lens; a longer pull (2-3x); a smaller pizza (down to about 6.5 in) or a small shift back to keep
  the crust inside the hero band; only if none works, a camera refit of at most 2 cm (say so). Probe single frames,
  compare posters, pick the clearest; archive round 2 (never delete); rebuild the drafts page.
- Owner addition (round 3): "Let's slightly rotate the pizza to make it obvious." Turn the whole round about 20-35 deg
  so the pulled slice and its cut gap face the lens at an angle; prefer this over shrinking the pizza or a camera refit.

Re-render done 2026-11-14 (round 3): the round turned 30 deg (in its mesh, so render_p0's per-slice bounding boxes stay
axis-aligned; turning the root pulled the camera back about 4 cm), slice pulled front-right (-60 deg) by 0.066 of the
source (3x round 2, about 1 5/8 in), its crust resting on the plate rim (lift 0.014); round shifted 1.5 cm left so the
slice stays in frame; scale 0.62 (7.4 in) and 2 cm behind the plate centre as before. Template camera unchanged
(target hero rows 0.359 to 0.535). Near cut gap on the poster: 15 px at the top of the crust widening to 36 px at the
plate (ray-cast per pixel row); the far cut gap is hidden behind the slice at this camera height (about 18 deg above
the plate) and cannot show without a higher camera. Export passed. Round 2 archived in
archive/guides/2026-11-14/plate_low_push_in__pizza_cut_small_pull (ARCHIVE.json round 3).

## Owner review 2026-11-14, round 4

- Owner: "the slice of pizza looks hollow." Cause (to confirm): `slice_round` cuts the Tripo mesh in memory without
  closing the cut faces, so at this low angle the open sides of the pulled slice and the round show as empty shells.
  Close every cut face (cap the cross-sections, e.g. bisect with fill / fill holes) and give the cut face a solid
  read in line art: the crust base line and one cheese/sauce layer line on the cross-section, no interior lines.
  Add it as a parameter of `slice_round` defaulting to the current behaviour, used only by this variant (swap-family
  rule), so table_spread_orbit renders the same; prove it by a scratch frame compare. Also say whether
  table_spread_orbit shows the same hollow look where its pulled slice is visible (do not change it; report only).
  Keep round 3's rotation, pull and camera. Archive round 3 (never delete); rebuild the drafts page.

Re-render done 2026-11-14 (round 4): cause confirmed with a correction: the cuts were not open (`slice_round` already
ran one fill, 0 boundary edges per slice) but that single fill spanned both cut planes as one folded face of about
540 vertices, whose fold drew as a box-like inner line on the pulled slice. New `slice_round(..., solid_cut=False)`
parameter, used only by this variant: one flat cap per cut plane, and on the four faces bordering the pulled slice's
gap a crust-side outline plus a crust line and a sauce/cheese line (thin tubes at 45% and 72% of the inner thickness;
contour-only line art does not draw the fold between a cut face and the crust wall, so the outline closes the face).
table_spread_orbit: scene geometry hash identical before and after, frames within EEVEE noise (0.013% of pixels over
8 levels, 135 frames); it does not show the hollow look (the camera is high, the cut faces are thin slivers). Round 3
rotation, pull, scale and camera kept (target hero rows 0.359 to 0.535, unchanged). Export passed. Round 3 archived
in archive/guides/2026-11-14/plate_low_push_in__pizza_open_cut (ARCHIVE.json round 4).

## Owner review 2026-11-14, round 5

- Owner: "let's try make the whole pizza flatter and biggest (almost as plate size)".
  Flatter: about 1.2-1.5 cm total height (crust rim a little higher than the centre), keep the round 4 solid cut faces
  and layer lines (re-place the lines for the new thickness). Bigger: about 10-11 in across on the 0.30 m (11.8 in)
  plate, crust just inside the plate rim. Keep the 30 deg rotation and a clearly visible pulled slice with its gap
  (re-tune the pull for the new size). The owner asked for this size, so size wins over "same camera": if the hero band
  needs it, let render_p0 refit the camera, and report exactly how much it moved (distance and height) and whether the
  move still reads like the template. Archive round 4 (never delete); rebuild the drafts page.

Re-render done 2026-11-14 (round 5): the Tripo pizza flattened in its mesh (height share 0.21 at the centre rising to
0.26 at the crust, smoothstep between 0.095 and 0.125 m of the source radius): 1.18 cm at the centre, 1.47 cm at the
crust rim. Uniform scale 0.847 (10 in), centred on the plate, crust 0.13 m from the centre, inside the 0.15 m rim; the
flat round rests on the plate's rim slope (base 1.8 cm above the table, 0.9 cm above the well), not draped. Round 4's
30 deg turn, -60 deg pull direction and solid cut faces kept; the cut-face lines place themselves from the new face
(45% / 72%). Pull 0.055 of the source (4.7 cm, about 1 7/8 in); the pulled slice's crust tilts 7.6 deg onto the rim
instead of lifting the round. Near cut gap on the poster: about 14 px at the top widening to about 22 px at the crust
(alpha row scan). Camera refit by render_p0: target from (0, -0.300, 0.901) to (0, -0.409, 0.924), 10.9 cm back and
2.2 cm up along the template's own line of sight (11.6 deg down to the same aim point), distance 0.306 to 0.417 m
(+36%); start 24 cm farther and 4.9 cm higher; same lens, path shape and timing. Export passed. Round 4 archived in
archive/guides/2026-11-14/plate_low_push_in__pizza_solid_cut (ARCHIVE.json round 5).
