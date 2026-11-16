---
name: object-renderer
description: Renders Loca guide objects alone in the approved P0 line-art style (Blender background) - every object in the library, one object, or a candidate model awaiting the owner's approval - and refreshes the objects web page. Use when objects are added, changed or requested, when the owner wants to see a model in line art before approving it, or for the brand-style object audit. Runs as the object-renderer agent; never approves, generates or edits a model.
---

# Object renderer

Repo root: `~/Documents/Development/VideoGuides`; in Blender commands use the real path
`/Users/ihor.buts/Documents/Development/Loca/.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/ScriptsAndGuides` (scripts
resolve paths from their own location). Blender 5.2.3 at `/Applications/Blender.app`, background mode only.

## Inputs

- `OBJECTS.md` section 1: 1a approved in P0 (code builders in `guides/blender_motion/assets.py`, `venue_assets.py`,
  `food_assets.py`, `geometry.py`, `p0_table_compositions.py`, `p0_scenes.py`; outside models named in the row;
  the creator rig; the CC0 hands in their three approved grips), 1b line-art studies, 1c library models
  (`model_refferences/objects/<name>/`, preferring `tripo-generated/review`, then `scene-ready`, then `functional`),
  1d rejected (never rendered unless the owner asks), and the requests table.
- `STYLE.md` (the line-art look) and `skills/guide-objects/SKILL.md` (the standard and the request flow).

## Scope per run

The prompt names one: `all` (the whole inventory), an object id, a section (approved / study / library), or a
candidate model path from an `OBJECTS.md` request (for a Tripo result, its folder under
`model_refferences/objects/<name>/tripo-generated/`, produced per `skills/guide-objects/SKILL.md` "Generating") (the line-art test render the owner approves before a model is
used).

## Method

1. Render with `python3 guides/tools/render_objects.py <scope> [--jobs 4] [--id NAME]` (scope: `all`, `approved`,
   `study`, `library`, one or more object ids, or a model path: a .blend/.glb file or a folder holding `asset.blend`,
   `model.blend` or a .glb; `--id` names a candidate, default `candidate_<model name>`). It runs one Blender
   background process per object, imports the guides' line-art setup (`lineart_render.strokes_setup`, contour only,
   role opacity and yellow light-edge cues as in `render_p0.py`) and never changes it. Each object alone, centred,
   three-quarter view 30 degrees down (50 mm lens), on the P0 player's dark stage colour #24352d, 1080x1080 PNG;
   a second view for flat objects (thinnest side under 20% of the next): `_top.png` when it lies flat (card, plate,
   tray), `_front.png` when it stands upright (menu board, window, door). The object list (ids, OBJECTS.md row,
   status, source) is the registry at the top of the script; add a row there when `OBJECTS.md` gains an object.
   Library, study and candidate models are prepared in memory as the 4 Nov study did (weld, normals, small bevel),
   then get the dot cleanup (owner review 2026-11-11): `clean_scan_mesh` (weld, loose parts under 2% of the model's
   diagonal removed) and `drop_short_strokes` (line-art strokes under 12 px removed), both in `render_objects.py`
   with their defaults in `SCAN_PREP`, importable by a guide scene. Voxel remesh, smooth and decimate are available
   but off by default (they melted panel and rim lines on the 11 Nov test set); a registry row overrides any value
   with `prep=dict(...)`, or `prep=False` to skip the cleanup. Try values with `--prep '<json>' --out <folder>`
   (test PNGs only, index untouched) before putting them in the registry. When a re-render replaces a published
   render for comparison, move the old file to `<id>_before.png` (`<id>_top_before.png` for a second view) first;
   the objects page shows before and after side by side for any render that has one. Logs and
   per-object results go to `$RENDER_OBJECTS_SCRATCH` (default `/private/tmp/render_objects`). A full run takes
   about 17 minutes with 5 jobs.
2. Work on in-memory copies only: never save, remesh, regenerate, reconstruct, buy or download a model. A model
   that fails to load or render is recorded with the reason and the run continues.
3. Look at every render (open the PNG): the whole object in frame, contours readable, not black or empty. Fix the
   framing per object; a poor line-art look is reported, not fixed by changing the model.
4. The script writes `guides/review/objects_renders/<id>.png` (+ `_top.png` or `_front.png`) and merges
   `guides/review/objects_renders/index.json` (a partial run replaces only its own ids): id, section, row, source
   path or builder, status from `OBJECTS.md`, bounding-box size in metres, face count, files, notes or errors, and
   an `approval` field. Study, library and candidate renders are test renders, never approvals.
5. Regenerate the page: `python3 guides/tools/objects_page.py` -> `guides/review/objects.html` (served by the
   `guides/` http.server on 8770 at `/review/objects.html`; do not restart it).
6. A candidate for a request: add the render path to that request's row in `OBJECTS.md`; the decision column stays
   the owner's.

## Hard limits

Never edit `render_p0.py`, `p0_scenes.py` or any builder's behaviour for guides (a shared-setup refactor must prove
two guide renders unchanged frame by frame); never touch `guides/p0/renders/`, `catalog/p0/animations-light/`, the
registry, the Scriptwriter server or Loca app code; never approve a model; never commit; no emoji.

## Report

Counts per section, failures with reasons, objects whose line-art look is poor (not to approve), runtime, files
written.
