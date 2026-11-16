# Description-based watercolor guide animation

These are source keyframes for live shot guides. Script-preview JPEGs are not changed.

For every guide, `manifest.json` records the existing description, live steps, camera reference, motion
windows, six keyframe times and generation prompt. The guide's original schematic animation and 3D strip
specify framing and movement. The approved cup-height orbit supplies only the watercolor style.

`originals/` preserves generated atlases or single held poses without opacity changes. `references/` contains the existing guide's
six sampled camera views. `frames/` holds cropped generated viewpoints at the guide's common scale.
`review/` contains six-view strips for checking angle, framing, direction, perspective and destination.

The generated scene must stay continuous. A following shot mentioned after "cut to" is not another pose
inside the current guide. Camera motion must be visible in the subject: true changing views on an orbit,
changing size on a push, movement in the opposite direction on a pan, or progressive uncovering on a reveal.
Do not substitute a moving or scaling flat scene for generated perspective changes.

Use one pale blue watercolor pigment, loose sketch contours and irregular wash beyond the lines. No mouths;
at most two visible hands per animation frame. Camera positions stay accessible to ordinary visitors.

## Export sequence

1. Generate all six-view atlases with the built-in image generation tool.
2. Save originals and prompts with `tools/guide_keyframes.py accept`.
3. Run `tools/guide_motion_render.py stage` and `contact`; review every guide against its description.
4. After all generation and reviews, run `tools/guide_motion_render.py finalize` as one final export batch.
5. Review playback before `tools/guide_motion_render.py publish` updates the canonical schematic assets.

The final export interpolates generated viewpoints with bidirectional optical flow, preserves the existing
start hold, motion windows, end hold and fade, and exports 405 x 720 APNGs at 15 fps. All frames are composed
before alpha is scaled by 0.5 exactly once. RGB values are unchanged by that alpha pass. Do not add CSS or
native-view opacity on top of the exported assets.

`rendered/<id>/guide.png` is the transparent artwork animation. `guide_with_guides.png` includes fixed
viewfinder/composition lines for standalone review; the raw guide leaves that UI to the app. `strip.png`
shows six animation samples with those fixed guides on a dark background for the catalog.

Publication archives the original schematic exports first. It does not change script-preview images,
compiled sensor scenarios or 3D camera specifications. Device playback and live sensor matching need a
separate device check; a browser or PDF review does not verify them.

The old `../watercolor/` scene batch is rejected and must not be published.

## Current status

There are 96 playable watercolor previews: 92 use deterministic fixed-art camera/cutout animation, and
four retain genuine changing-view keyframes for orbits or a head turn. Source artwork exists for 102
guides; six require revision and 76 still need matching verified artwork. All 178 guides were audited in
`../../catalog/local-motion-audit.md`. The exact original 62 source sets remain marked in the current
`../../catalog/regeneration-report.md`; the initial 62/178 report and manifest are preserved in
`local-motion/baseline/`.

The initial atlas-generation batch stopped on an image-generation quota. `generation-status.json` and
`review/findings.json` describe that historical batch. The later local motion pass uses 12 selected new
source resources (13 outputs including one color correction) and individually audited reusable paintings.
Its prompts and immutable generated originals are in `local-motion/prompts/` and `local-motion/originals/`.
It generates artwork once and makes the animation frames locally. No API fallback was used.

The old `../watercolor/` animated scene batch remains rejected. Individual original paintings can be
reused after checking the named subject, camera angle, visitor access, mouths and total visible hands.
No canonical overlay publication has run. The catalog uses 96 watercolor strips and 82 original
schematic strips. All 789 snapshotted source preview/catalog/scenario inputs remain unchanged.

## Local camera and cutout animation

`tools/local_motion.py plan` configures the latest 57 rebuilt guides; `previews` exports that subset.
`tools/guide_motion_render.py previews` exports all 96 reviewed guides. `stage` saves actual sampled
camera/cutout keyframes for local-motion entries, rather than six identical copies of the master.

`rendering.method` selects `single_source_crop`, `layered_animation`, or the prior changing-view method.
Immutable layer hashes and explicit transforms make frame identity deterministic. Foreground layers hide
the background painting before compositing; all frames are composed before alpha is multiplied by 0.5
once. The browser has no extra opacity multiplier. Fixed horizon, thirds and viewfinder guides remain.

Use a wide master for pans, a tall master for tilts, separate foreground/background layers for reveals,
and separate rigid props for clinking or parallax. Match the source timing and direction. A genuine orbit
or actor turn needs consistent perspective/pose artwork; never simulate it by flipping or sliding one
flat painting. `local-motion/assets/` contains derived crops and cutouts; source originals are untouched.

The brunch-pour source still requires a resource-height plate master. Its old illustration was rejected
because it looks down onto the plate. Camera-only guides hold independent fingers/working actions; the
gallery and audit identify these limits. Device playback and physical sensor matching are unverified.

## Stable zoom and held close-ups

On 2026-10-25, 26 zoom guides and 9 held close-ups were rebuilt from one existing generated image per
clip to remove object/texture drift. The source image is sampled directly for every frame; these clips
do not interpolate independently generated poses. Their timing, fixed viewfinder and 50% alpha remain.
The local camera/cutout pass above extends this first stabilization pass.

Run `guides/tools/stable_zoom.py` from the ScriptsAndGuides root (or `tools/stable_zoom.py` from guides) to
prepare the 35 masters and crop plans, then rebuild previews and the catalogs. The exact IDs, master hashes,
source cell selections and crop extents are in `catalog/stable-zoom-report.json`; the readable report is
`catalog/stable-zoom-report.md`. Previous exports are in `catalog/backups/pre-stable-zoom/animations/`.

Static close-ups hold their source pose. Independent subject actions are not synthesized in these clips.
Tight surface crops inherit the existing source resolution. Compiled live-sensor scenarios are unchanged.
