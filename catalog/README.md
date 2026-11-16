# Catalog (agent 04)

`scripts-and-guides.pdf`: A4 landscape, one chapter per venue kind (title, production categories, five
best-practice lines, the kind's scripts), one page per script (title, summary, then one column per step:
the step picture, shot and shot-plan entry, the first on-screen text with its spoken line, where to stand,
the schematic guide strip and the 3D ghost strip with the guide id), and two appendices (menu item kinds with
the review script covering each; the guide coverage table).

Built by `build_catalog.py` (Python with Pillow; the strips in `strips/` are six evenly spaced frames of each
APNG in `../guides/overlays/schematic/`, `previews/` holds 270 x 480 copies of the step pictures) and rendered
with Chrome headless:

```sh
<python with Pillow> build_catalog.py
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf=scripts-and-guides.pdf --virtual-time-budget=20000 "file://$PWD/catalog.html"
```

The reasoning per script stays in `../scripts/<kind>/`, the research in `../research/`.

## Current verified build

The PDF has 76 pages, including exactly one page for each of 56 scripts. All 304 steps show their preview,
schematic strip and 3D strip: 912 placed images. HTML image paths were checked and all are present. The
appendices include all 11 review kinds and all 304 coverage rows. Sample pages were rendered with PyMuPDF
and reviewed for missing images and page breaks; see `pdf-check.json` and `checks/`.

This edition includes 96 reviewed watercolor animation previews at 50% alpha. Open `animations.html` for
playback, search, replay and starting-pose controls; `catalog.html` also plays each step's guide. Both work
from local files in a browser. The remaining 82 guides use their original schematic APNGs. The PDF uses
matching static frame strips and links to the browser player; PDF image strips do not animate.

`animations/<id>/guide.png` is the raw transparent artwork animation; `guide_with_guides.png` includes the
fixed viewfinder, thirds and horizon reference. Alpha is scaled by 0.5 after each clip's frames are composed,
with no CSS opacity multiplier. `strips/` now contains the 96 watercolor preview strips and 82 original
schematic strips, labelled in `strips/index.json`. Previous catalog strips are archived in
`backups/pre-animated-previews/strips/`. Canonical guide overlays and sensor scenarios are unchanged.

There are 102 guides with source artwork: 96 playable and six requiring revision. Another 76 lack
matching verified artwork. The original 62 generated/reused source sets remain identified in
`regeneration-report.md`; its original edition is archived under
`../guides/watercolor_motion/local-motion/baseline/`. The full-set export/publication guard still waits
for every guide; reviewed-subset previews do not wait for the unfinished set.

Build the playable previews with `guides/tools/guide_motion_render.py previews` in a Python environment
with Pillow, NumPy and OpenCV. Then run `build_playback.py`, `build_catalog.py` and Chrome PDF rendering.
`check_playback.py` verifies real APNG pixel changes and the hold/replay controls in local headless Chrome
(using websocket-client). `playback-check.json` and `animation-asset-check.json` record the checks.

The brunch-pour guide has a known legacy subject mismatch: its step and description specify sauce on a plate,
while the original schematic depicts a cup. Its 3D reference now reuses the existing plated-dessert model;
the previous 3D files are archived under `../guides/watercolor_motion/source-corrections/`. The catalog marks
the remaining schematic correction. Generated camera geometry is visually assessed, not measured against
physical camera poses. Device playback and live sensor matching were not verified.

## Stable zoom and held close-ups

On 2026-10-25, 26 zoom guides and 9 held close-ups were rebuilt from one existing generated image per
clip to remove object/texture drift. The source image is sampled directly for every frame; these clips
do not interpolate independently generated poses. Their timing, fixed viewfinder and 50% alpha remain.
This was the first stabilization pass. The local motion pass below extends it to pans, tilts and layers.

Run `guides/tools/stable_zoom.py` from the ScriptsAndGuides root (or `tools/stable_zoom.py` from guides) to
prepare the 35 masters and crop plans, then rebuild previews and the catalogs. The exact IDs, master hashes,
source cell selections and crop extents are in `catalog/stable-zoom-report.json`; the readable report is
`catalog/stable-zoom-report.md`. Previous exports are in `catalog/backups/pre-stable-zoom/animations/`.

Static close-ups hold their source pose. Independent subject actions are not synthesized in these clips.
Tight surface crops inherit the existing source resolution. Compiled live-sensor scenarios are unchanged.

## Local camera and cutout animation

The latest pass rebuilt 57 guides, adding 46 playable previews. Of the 96 watercolor previews, 92 now
use fixed artwork with local camera windows or rigid cutout layers. Four retain genuine changing-view
keyframes for orbits and a head turn. `local-motion-audit.md` and its JSON companion cover all 178 IDs,
including the exact reasons for deferring missing masters, action layers or perspective artwork.

Mechanics include right/left pans, crop zooms, vertical tilts, ten layered foreground reveals, glass-flight
parallax, two-hand clinking, lowering a glass onto the countertop, and raising a glass in front of a face.
The low bar uses one wide public-side painting; the camera crop moves right by 75 pixels so the same
painted bar moves left. Foreground masks hide background paint before the final global opacity pass.

Twelve selected AI-painted resources (13 outputs including one monochrome correction) are in
`../guides/watercolor_motion/local-motion/originals/`; exact prompts are in the adjacent `prompts/`.
Matching legacy paintings are reused individually. The rejected old scene-animation exports are never
published. Previous preview exports are archived in `backups/pre-local-motion/animations/`.

From ScriptsAndGuides, run:

```sh
<python with Pillow, NumPy and OpenCV> guides/tools/local_motion.py plan
<python with Pillow, NumPy and OpenCV> guides/tools/local_motion.py previews
<python with Pillow> catalog/build_playback.py
<python with Pillow> catalog/build_catalog.py
<python> catalog/report_local_motion.py
```

`check_local_motion.py` checks exported alpha, source preservation, local media paths, timing, deterministic
paint samples, foreground occlusion and the bar's motion direction. `check_playback.py --guide bar_low_truckr_mm`
checks actual browser playback and controls. Physical camera calibration and device sensor matching remain
unverified. Camera-only holds do not animate independent finger, pouring, steam or working actions; those
limits are shown in the gallery and audit. Image-plane motion is not a reconstruction of a new 3D view.

## Development API

All 178 guides are served by the development API, using the 96 reviewed watercolor animations and 82
original schematics. The existing per-step endpoint remains supported; `/v1/guides` lists every guide and
`/v1/guides/{id}` returns one. See [API setup and verification](../api/README.md).

## Composition and static-take audit

[Interactive audit](composition-audit.html), [written findings](composition-audit.md) and
[per-guide JSON](composition-audit.json) cover all 178 guides and their 304 script assignments.
The interactive page filters priorities, techniques/shot families and motion states, and plays current
animations for comparison. Recommendations describe both the actual footage and future guide artwork.
No animation, sensor scenario or API data was changed by this audit.

The review uses 15 contact sheets and five timed samples from every APNG. Among the 96 watercolor clips,
24 held takes have identical samples: 15 omit a described action (23 script steps), and nine are useful
intentional holds. Original schematics have 21 identical and nine low-change candidates; 22 need clearer
subject-action treatment and eight are intentional holds. Pixel changes in schematic guidance graphics
are not proof of a real subject action. Sparse samples can miss cyclic motion.

`measure_guide_motion.py` produces `checks/composition/motion-measurements.json`;
`build_composition_audit.py` publishes this reviewed snapshot and the curated recommendations. Review new
artwork and update the editorial findings before reusing these recommendations after asset changes.
`checks/composition/audit-check.json` and `browser-check.json` record coverage, source preservation,
local media paths, filtering and existing-animation preview checks.
