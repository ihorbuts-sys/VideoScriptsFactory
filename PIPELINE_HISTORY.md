# Pipeline history (superseded notes; the current guide is README.md)

> **Start here (2026-11-10):** `WORKFLOW.md` (roles and skills), `STYLE.md` (the one style), `GUIDE_INDEX.md`,
> `OBJECTS.md`, `catalog/p0/RUNBOOK.md`. The sections below are history, newest first; where they disagree with
> `STYLE.md`, `STYLE.md` wins. "Rules for every agent" (watercolor sketches, baked alpha) is superseded.


## P0 line-art collection (10 November 2026)

[Play the 37 active P0 guides locally](http://127.0.0.1:8766/p0/index.html) ([public snapshot: 29 guides](https://loca-camera-guides.forgivingmacaw.chatgpt.site)): native white contours, dark underlay, restrained yellow light edges and local steam glow. All 111 active animation/selector/poster assets are published through the local API. Five person/selfie guides are restored with the canonical creator, plus three friend-filmed options. [Character guide report](catalog/p0/people-guides-report.md). Talking and chewing require facial controls that the model does not have. Choose **First visit** under Cafe or Restaurant; Food review is also mapped to the P0 types. Entrance, menu, pour and cup guides were updated in place. The new table spread, cocktail slide and pancake reveal are reusable under **Food review / Dish** and **Restaurant / First visit / Plate**. [Latest scene and grip corrections](catalog/p0/owner-corrections-report.md). Step pictures remain separate from overlays.

[Results, source directories, API routes, commands and checks](catalog/p0/README.md). Active Blender scenes and frames are in `catalog/p0/animations-light/`; API masters in `guides/p0/renders/`; step pictures and prompts in `previews/clay-3d/p0/`. Earlier experiments below remain available.

## Isolated model line-art study (4 November 2026)

The [supported-object collection](http://127.0.0.1:8766/lineart-study/objects/index.html) now places the cup on a saucer and adds a continuous coffee/pastry tray move and descending cake arc. Four eight-second clips pass 960 native frame checks. [The current inventory](catalog/lineart-study/objects/available-models.md) lists 44 newer Tripo object families, supplemental local meshes, three rigs and ten existing scene layouts.

The earlier [filled-cup orbit comparison](http://127.0.0.1:8766/lineart-study/orbit/index.html) adds coffee and a foam heart to hide the handle geometry inside the cup. Compare a steady 45° downward view with smooth 45° → 37° → 53° → 45° changes over a 90° orbit. Both eight-second clips passed all 480 frame checks. [Notes and reproducible commands](catalog/lineart-study/orbit/README.md).

Custom scene-building work is deferred. The current experiment renders the existing cup as native Grease Pencil contours on transparent pixels, with no shaded mesh surfaces. The CLI renderer is [lineart_render.py](model_refferences/objects/tools/lineart_render.py); inputs, camera math, version support and checks are documented in [the study notes](catalog/lineart-study/README.md). This experiment does not replace active guide/API artwork.

The renderer uses the installed Blender setup headlessly. It supports the modern Grease Pencil API in Blender 4.3+ and 5.x, bakes Line Art before disabling mesh render visibility, and emits 1080×1920 PNG RGBA, scene.blend and per-frame camera/safe-zone metadata. The white contour has a dark underlay; hidden dashed edges are optional. Global app-view opacity remains a separate decision from these raw stroke images.

## New camera-only commercial guides (2 November 2026)

[Play the three lessons](http://127.0.0.1:8766/commercial-core/index.html): pastry-display range, opened-pastry detail and a window-side room reveal. Three native scenes update five script steps, with no human rigs or hand manipulation. Existing models, color and 65% ghosts, separate viewfinder/level and API publication. Camera, embedded-browser, scope-preservation and typed checks passed. See [report and app steps](catalog/commercial-core/README.md).

## Current priority: practical commercial shots (2 November 2026)

Prioritize achievable object, food-detail and venue shots that teach a commercial filming purpose, staging, light and a repeatable phone move. Defer new character and hand-interaction work. A numeric contact or wrist check does not certify a natural-looking grip.

The owner rejected the coffee pickup and tong handling. Their step overrides and complete bakery sequence were withdrawn from the active API; prior guide versions are restored. Source scenes remain as rejected studies for inspection. The earlier display-selection guide is retained. See [withdrawal report](catalog/interaction-scenes/withdrawal/report.json).

Published camera-only batch: a readable pastry-display sweep, an already-opened pastry filling reveal, and a window-side dining-table/room reveal. No new paid models or animated hand manipulation.

## Canonical creator performances (30 October 2026)

[Play the creator scenes](http://127.0.0.1:8766/creator-scenes/index.html):
**First visit / Why come** and **Build a box / The budget**. Both reuse the
existing creator and her 65-bone rig, with natural head, chest and free-hand
gestures. Each has seven-second color and ghost variants for a six-second
capture. The default image-view opacity remains 65%, with separate viewfinder
and level. Other scripts sharing the guide IDs retain their existing artwork.

All 210 frames have checked face visibility, comfortable wrist angles, hand
scale and sole-to-floor contact. The original GLB is hash-verified and retained;
no paid generation or rigging was needed. Her original expression is preserved;
facial lip sync remains separate work. See [the creator report](catalog/creator-scenes/README.md).
The builder and validator are `build_creator_guides.py` and
`check_creator_performances.py` in `model_refferences/objects/tools/`.

## Primary food scenes (30 October 2026)

Three reviewed native scenes reuse the new primary-object library: the low
burger approach, the top-down brunch spread, and the descending dessert arc.
Each has a full-color film and an object-only glass APNG at 65% image-view
opacity. Background context is softer than the food. The brunch viewfinder
adds a Y down-angle target alongside X level; both remain separate UI.
See [the scene report](catalog/food-scenes/README.md) and
[play the collection](http://127.0.0.1:8766/food-scenes/index.html).

Select **Ten dollar run / Item two**, **Weekend brunch / The spread**, or
**Date night / The plate** in the app. The burger updates that table context
only; its shared handheld version is preserved. Every scene ends with a
deliberate cut to the following script step. No new paid models were needed.
Source: `model_refferences/objects/tools/build_primary_food_scenes.py`.
Packaging dependencies are pinned in `guide-packaging-requirements.txt` in
the same tools directory. These are individual takes, not new full scripts.

## Approved glass guide rollout (29 October 2026)

Use the approved `hologram-full-surface-view-opacity-v3` treatment for new live
filming guides. Reuse the calibrated Tripo models and canonical characters.
The exported image has transparent empty space and full-strength hero surfaces;
apply the global 65% opacity in the image view once. Supporting objects remain
slightly softer. Walls, floor and ceiling are excluded from the ghost, while
mounted props remain. Keep full-color video from the same camera and scene.
The preview places that video two seconds behind the guide and draws the
viewfinder and level separately. These delay settings are preview simulation,
not delayed live-camera capture.

The approved study is `catalog/coffee-hologram-study/`. For VS Code's embedded
browser use `http://127.0.0.1:8766/coffee-hologram-study/index.html` and the explicit
Play control. The first rollout batch is in `catalog/glass-rollout/coffee/`.
Every scene must retain its actual filming description, supported contacts,
public camera positions and meaningful subject transitions. Fixed lenses are
used where phone translation and pitch/yaw changes can demonstrate the shot.
Do not launch Blender UI unless requested. No new Tripo generation is needed
for the first coffee batch.

The Scriptwriter API and VideoEditorKit client now propagate `imageViewOpacity`.
Legacy baked-opacity images default to view opacity 1. New object-only glass
images default to view opacity 0.65. Earlier opacity instructions below describe
previous revisions and must not cause a second multiplier.

The coffee continuation is in `catalog/glass-rollout/coffee/`: a stationary
lights-on routine, the seated corner, and a connected room/desk/Wi-Fi route.
`catalog/glass-rollout/sequences/cafe-morning-ritual/` contains all four morning
steps in the glass style. It removes repeated cup-to-pastry handover frames and
uses explicit cuts at other shot boundaries. Full-script API responses carry
the same opacity metadata as individual guides. See
[the current report](catalog/glass-rollout/report.md) for verified counts.

The reusable laptop was reconstructed once from its existing four reference
views (40 Tripo credits), calibrated to face -Y, and rendered in all six
projections. Its original GLB remains untouched. The folded Wi-Fi card uses a
localized semantic mask to retain its symbol in the glass guide; no texture or
edge pass is applied across the whole scene. Keep only one native EEVEE render
process running. Export, browser testing and API publication may proceed as
each serial scene completes. Human performance replacements still need contact
and facial-pose review before publication.

## Standalone primary targets (29 October 2026)

The owner prioritized independently usable filming objects that can also support
static LiDAR-driven overlays. The authorized 645-credit wallet funded 16 primary
targets for 640 credits; 5 remain. Reuse these and existing assets before buying
more props. Food and tableware remain separate; do not bake them into rooms.
The new static component library is `catalog/primary-targets/`, with GLB/USDZ,
lightweight proxies, named anchors and six native projections per object.
API: `/v1/guide-objects` and `/v1/guide-objects/<id>`. These components have not
been validated against device LiDAR, human grips or moving mechanisms.
See [the report and prompt paths](model_refferences/tripo-cli/primary-targets-2026-10-29/report.md).

## Current owner-approved direction (28 October 2026)

Use local image-driven 3D reconstruction from the approved clay/plasticine art.
The owner accepted the TripoSR croissant trial and asked to continue with this
workflow. The first reusable prop pack and character studies are in
[model_refferences/objects/reconstructed.html](model_refferences/objects/reconstructed.html).
There are [full-color and ghost scene previews](catalog/clay-scenes/index.html).
The connected 12-second bar-to-table guide is published through the development
API, including its script-specific override and an optional `colorVideoURL`.
The library contains 13 reusable props, including a modular four-level pastry
rack with sixteen supported croissants. The coffee orbit remains an unpublished
base-shot proof; its character sip handover is still pending.

Human guide reconstruction is required using the approved creator, barista and
friend with sculpted locs. Character rigging, hands and object contact require
validation before replacing the old human guides. The earlier parametric prop
and character approximations are rejected. Preserve source images and original
neural meshes; use actual Blender geometry for consistent camera motion.
Publish ghost guides at 65% whole-overlay opacity, with faint context, fixed
feasible lighting and separate app viewfinder/level UI. Keep full-color renders
from the same scene for the alternate guide collection. Do not launch Blender
UI unless explicitly requested. Setup and limitations are in
[model_refferences/objects/local-reconstruction.md](model_refferences/objects/local-reconstruction.md).

## Earlier native guide pipeline (27 October 2026)

Continue with native Blender object/hand animation. Sprite generation is stopped, and new faces,
heads and full bodies are deferred. Publish at 65% whole-overlay opacity, keep context faint, lights fixed and camera
moves feasible for an ordinary phone. Do not launch Blender UI unless explicitly requested.
The current pipeline and render guard are documented in [guides/blender_motion/README.md](guides/blender_motion/README.md).
Earlier watercolor/image-generation instructions below describe the previous workflow.

Goal: a catalog of venue scripts with a preview image per step and a live guide per step, delivered as a PDF
collection (step previews plus guide previews, in two guide styles) and as kit data (`script_templates.json`,
step images, shot scenarios and overlays) that VideoEditorKit ships.

Four agents, run one after another where an arrow is shown, in parallel where not. Each agent reads its brief in
`briefs/`, uses the skill named there, and leaves everything it produces in the folder named there. Nothing is
handed over by chat.

```
01 Script researcher ──▶ 02 Step previews (Codex, images) ──┐
                     └─▶ 03 Live guides (two styles)      ──┴─▶ 04 Catalog PDF
```

## Folders

| Folder | Written by | Contents |
|---|---|---|
| `research/` | 01 | `categories_*.json` (the real category lists, already fetched), `venue_kinds.md` (the mapping of categories to script kinds), `best_practices/<kind>.md`, `menu_item_kinds.md`, `sources.md` |
| `scripts/` | 01 | `script_templates.json` in the kit's format, `shot_plan.json` (angle, move, transition per step), plus `scripts/<kind>/<template id>.md` with the reasoning behind each script |
| `previews/` | 02 | `<template id>_<step id>.png` (1080 x 1920) and `prompts.md` |
| `guides/` | 03 | `templates/*.json` (shot-overlay scenes), `scenarios/*.json` (compiled live scenarios), `overlays/schematic/*.png`, `overlays/3d/*.png` or `.usdz`, `coverage.md` |
| `catalog/` | 04 | `scripts-and-guides.pdf` and the HTML it was built from |

## Facts the agents must not re-derive

- Production categories (`research/categories_creator.graphql.loca.us.json`, 20 slugs): bakery, beauty,
  beauty-salon, business-services, clothing-shops, coffee, dining, entertainment, fast-food, food-and-drinks,
  food-and-drinks-family, food-truck, recreational-other, services, services-education, services-health,
  services-other, shopping, shopping-music, sport_health. The test environment differs; production is the source.
- The kit ships 5 script kinds today (`coffee`, `dining`, `bakery`, `craft-beer`, `beauty-salon`) and 10 scripts.
  `craft-beer` (Bar) is not a production category: either map it to a production slug or drop it.
- Script format: `VideoEditorKit/Sources/VideoScripts/Resources/script_templates.json` (`venueKinds`,
  `templates[]` with `steps[]`). Step fields: `id`, `title`, `shot` (wide, medium, close, detail, pov, selfie),
  `position`, `direction`, `seconds`, `prompter`, `captions[{text, script}]`, `pip`, `imageURL`, `overlays[]`.
  A step with `pip`, `selfie` or `close` is spoken on camera (lip sync); the rest are "just film" steps voiced later.
- Limits: an ad is 3 to 60 s; a step is 2 to 8 s; the whole script should land near 20 to 45 s so AI Edit has room.
- Food review: the kit already has `food-review`, which asks for a menu item from the venue's Loca menu. The
  researcher audits which dish kinds appear in menus so review scripts can be tailored per dish kind.
- Shot plan: the kit's step fields say what to film, not how the camera moves. The researcher adds
  `scripts/shot_plan.json`, one entry per step: `angle` (eye-level, low, high, top-down, over-shoulder, dutch,
  pov), `start` and `end` framing (wide, medium, close, detail), `move` (static, push-in, pull-out, pan, tilt,
  truck, orbit, whip, reveal-from-behind, rack-focus-stand-in), `seconds`, and `transitionOut` (cut, match-cut on
  the subject, whip, push-through, pull-back-reveal). Consecutive steps must chain: the end pose of step N is a
  sensible start for step N+1, or the transition names how they are joined. This is what makes the ads look
  commercial, and it is what the guides animate.
- Guides show three things with no text: the angle to shoot from, the move during the shot, and the hand-over to
  the next shot. All of it must be clear from watching the animation: the subject visibly changes size on a push-in
  or pull-out, its far side comes around on an orbit, its top appears on a tilt down, the frame flicks on a whip.
  The subject moves continuously between poses, never jumps. There are no per-step hints in the animation (no
  badges, timers, arrows): the app helps the creator take the starting pose, plays the animation, and gives only a
  faster/slower cue and one clock for the whole take.
- Guides: `Loca/.claude/skills/shot-overlay` renders schematic overlays from scene JSON;
  `Loca/.claude/skills/live-shot-guide` compiles those scenes into live scenarios the kit runs. The ghost take
  flow (how a guide plays) is described in `VideoEditorKit/docs/guided-take-flow.md`.

## Rules for every agent

- English only, no emoji, no Cyrillic in files.
- Guide artwork direction: use image generation for loose sketches with one translucent watercolor pigment.
  These images are source artwork for live guide animations. They do not replace `previews/` or
  `catalog/previews/`. Derive each guide from its existing description, scenario, camera path and guide strips.
  Script-preview illustrations do not specify the camera angle or motion and must not drive guide generation.
  The wash extends irregularly beyond the contour lines. Keep the approved pale pigment; do not darken it
  when adjusting opacity. The user explicitly authorizes programmatic opacity adjustment of the full image.
  Preserve all generated originals unchanged. After all keyframes have been generated, apply alpha 0.5 in a
  final batch export, preserving RGB, feathered edges and transparent background. Display the exported PNG
  without a second opacity multiplier.
  Do not draw or trace the illustration from code.
  Code may sequence and interpolate generated viewpoints. For zoom-only guides and held close-ups, the user
  requested rebuilding frames from one existing image to remove generation drift. Use a continuous crop/scale
  of that master at a fixed angle; retain the guide timing and stable viewfinder. Orbits and other viewpoint
  changes still require actual changing perspectives. Review angle, framing, motion direction and the
  final pose before publishing. The approved functional study is `guides/shot-proof/cup_eye_orbitr_cc/`;
  its source description, keyframes, animation and provenance are beside it. The new generation manifest is
  `guides/watercolor_motion/manifest.json`. The earlier `guides/watercolor/` scene batch is rejected.
  The tracked-subject caught state should tint the artwork yellow.
- Faces stay schematic. The P0 line-art creator keeps her mouth line (owner ruling 2026-11-10, replaces the earlier
  no-mouth rule); still no teeth or lip detail.
- When showing makeup or cosmetic application, use a more schematic drawing: simple face contours, minimal
  facial marks, flat accent areas for cosmetics and a clearly recognizable applicator/action. Avoid realistic
  skin texture, individual eyelashes, detailed eye rendering and glossy beauty-ad shading. Apply this to
  previews, guides and reused artwork.
- Show at most two visible hands in an image or animation frame, counted across all people. Partial hands
  count too. Use zero, one or two hands as needed; never add extra, duplicated or detached hands. Frame other
  people's hands out of the scene. Apply this check to generated and reused artwork.
- Camera viewpoints must be accessible to ordinary visitors. Never generate or reuse a view from behind a
  staff counter, inside a working kitchen, at a staff-only prep bench, behind a till, or in another restricted
  area. Staff activity may be shown from the customer side or through a public viewing window. Do not assume
  special access. If a script or shot plan conflicts, adapt the viewpoint before creating previews or guides;
  keep the entire camera move within visitor-accessible space.
- Prefer the venue's real words (dish names, service names) over marketing phrases; lines are spoken by a creator,
  so they must sound like one person talking, 8 to 14 words per spoken step.
- Every script step names what to film, what to say (or that nothing is said), the framing and a length.
- Prefer reusing existing project previews and sharing suitable images across script steps. Reuse requires
  a matching subject, viewpoint and starting framing; preserve meaningful product continuity within a script.
  Record canonical image references so later integration can share resources as well as artwork.
- Write what was decided and why next to what was produced; the next agent starts from the files, not from memory.

## Filming-guide composition corrections

Personal dishes belong at usable place settings, never at the dining table centre. Keep utensils and
glasses supported and coherent with that setting. The native pipeline enforces this through
`guides/blender_motion/table_composition.py`; saved scenes are checked with
`guides/blender_motion/verify_table_policy.py`. Preserve quiet, propped-phone holds where the script
calls for resting hands; avoid orbiting an isolated cropped forearm.
