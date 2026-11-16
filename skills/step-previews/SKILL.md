---
name: step-previews
description: Writes and reviews the preview picture of every guided script step (9:16 hand-moulded plasticine illustration) so it shows, at a high level, the idea shared by all of the step's suggested shot guides - the same subject, objects and table layout, from an angle none of the guides contradicts. Use after the script composer has chosen a step's guides, when a guide changes, or to regenerate or review step pictures.
---

# Step previews

> Not used for catalog v3 (owner 2026-11-17, design 291:3905: steps have no pictures; the progress list shows an
> icon and the camera shows the guide carousel). Kept for the v2 catalog and as reference; do not generate v3 step
> pictures.

Repo root: `~/Documents/Development/VideoGuides`. A step's preview is the picture on the step card; the guide is the
line-art animation in the camera. A step suggests 2-3 guides; the preview stands for all of them: it shows the scene
they share (what is filmed and how it is set up), and the guides show the ways to film it. A preview with an object,
a layout or a camera that none of the guides uses teaches the wrong shot.

## Inputs per step

- The step in `scripts/_parts/<kind>.json`: `id`, `title`, `shotType`, level, `idea`, `camera`, position, direction.
- **All of the step's guides** (its `guides`, recommended first): each record in `guides/p0/plan.json` (or the
  draft's `record.json`): technique, camera, orientation, composition, the objects in `sourceSetup`, `invariant`;
  and each poster `guides/p0/renders/<guide id>_poster.png` (its target frame).
- Style: `previews/clay-3d/tools/plasticine_v2.py` (`WORLD`, `IDENTITIES`, `CONSTRAINTS` blocks, the fixed per-script
  notes) and the references in `previews/clay-3d/references/` (`plasticine-world.png`, `plasticine-food.png`, the
  creator, barista and friend references). The cast is fixed: creator, barista, friend with locs.

## Alignment rules (the preview stands for all of the step's guides)

1. The shared scene: the subject and the objects every guide of the step shows, in the layout they share (the shared
   example dish unless the step names a dish, on the plate and with the cutlery the per-dish place-setting rule in
   `STYLE.md` "Objects" gives it: no cutlery for pastry, pizza and bakery items, a dessert plate for desserts; the cup and fork where the guides put them; the same door, counter or
   board). An object only one guide uses stays out unless it is the step's subject. No extra hero objects.
2. The camera: the side and angle the guides share; when they differ (a 45 degree orbit, a napkin slide at plate
   height, an overhead rise), a neutral three-quarter view from the creator's side that shows everything the guides
   film and contradicts none of them. A step whose guides all use the front camera gives a front-camera preview (the
   creator facing the viewer); back-camera guides never show the creator's face unless a guide does.
3. The preview shows the scene at rest, not a move: no arrows, phone, viewfinder, grid or text.
4. Everything in `CONSTRAINTS` holds: visitor side only, at most two attached hands, plates at place settings, no
   text or logos, no pictured filming phone.

## Prompt

Write `previews/clay-3d/p0/<template id>_<step id>.prompt.txt` as the existing P0 prompts are written: the use case
line, the reference role (the plasticine master sets materials and palette only), `WORLD`, `IDENTITIES` (only when
people appear), `CONSTRAINTS`, then **EXACT SCENE** derived from the guide: camera position and angle in words
("straight above the plate, phone flat"; "seated in front, 45 degrees down"), the objects and their places as in
the posters, the subject's size in frame, who is visible. Attach the guides' posters (a contact strip of 2-3) as a
second reference with the role "shared objects, layout and camera side only; ignore the line-art look".

Generation runs in an image model that accepts references (the P0 set was generated with Codex `image_gen`); Claude
writes prompts and reviews results and does not invent pictures from code. Record each image in
`previews/clay-3d/p0/manifest.json` (asset, sha256, status, origin, prompt, review, hands) and bind it to the step.

## Review (every image)

- Next to the strip of the step's guide posters: the shared objects in the shared arrangement, a camera side and angle
  none of the guides contradicts, the same front/back camera. A mismatch is redone, not explained away.
- Style: plasticine materials throughout, the cast's faces and clothes as in the references, hands counted.
- The strip of a script's previews reads as one story in one style.
- Changing a step's guide list (added, removed or reordered) means re-checking the preview, and redoing it on a mismatch.

## Output

The image under `previews/clay-3d/p0/assets/`, the prompt file, the manifest entry, and a line per step in the
script's `NOTE.md` (preview file, the guides it stands for). New or changed images join `assets/manifest.json` via
`guide-publish`.
