# P0 guides: exact commands (verified 2026-11-10)

Run from `Loca/.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/ScriptsAndGuides`. `PY=/private/tmp/loca-p0-people-venv/bin/python3`
(volatile: recreate from `model_refferences/objects/tools/guide-packaging-requirements.txt` if /private/tmp was cleared).
Blender 5.2.3 LTS at `/Applications/Blender.app/Contents/MacOS/Blender`.

## Render one guide

    Blender -b --python-exit-code 1 -P guides/blender_motion/render_p0.py -- --id <id> --out <dir> [--replace]

`--out catalog/p0/animations-light/<id> --replace` overwrites the active scene and frames; use a scratch `--out` to
compare first. 90 frames take about one minute. Then `guides/blender_motion/export_p0.py` writes
`guides/p0/renders/<id>.png`, `_selector.png`, `_poster.png`, `_checks.json`.

## Publish

    $PY guides/tools/build_bundle.py --out <staging dir> --profile p0      # staging, about 12 s, 2.1 GB
    $PY api/check_api.py --bundle <staging dir> --report <report.json>      # real handlers on the staged bundle
    $PY guides/tools/build_bundle.py --profile p0                           # live: Scriptwriter/catalog
    $PY api/check_api.py --base-url http://127.0.0.1:8765 \
        --token-file ~/Documents/Development/Scriptwriter/.token \
        --bundle ~/Documents/Development/Scriptwriter/catalog --report <report.json>

`build_bundle.py` builds catalog.json from `scripts/script_templates.json` (the merged catalog, `check_scripts.py
--merge`), so publishing also republishes the scripts. Diff staging against live before the live build.

## Reproducibility check (2026-11-10)

- `plate_high_orbit` re-rendered from the current code matches the published frames (no frame bit-identical, at most
  0.03% of pixels differ by more than 8 levels: EEVEE noise).
- `bite_selfie_eye` did not (the 13:57 `p0_people.py` edit). Owner chose the current code; all 8 character guides
  were re-rendered, fixed and published on 2026-11-10 (below), so renders and code match again.

## Character fixes (2026-11-10, owner-reviewed)

- Cup grips: the thumb rides above the hooked index (`grip_digits`, cup only); the cup reaches the lips.
- `sip_friend_side`: the free right forearm rests on the near table edge with the hand hanging 60 degrees below
  level, palm upright, fingers in a relaxed curl toward the palm; the character fade starts at 0.88 m for this guide
  (`p0_supported_right_hand`) so the forearm stays drawn; equal poses give equal frames (held start and end).
- `bite_friend_three_quarter`: the resting fork hand sits lower and flatter, rising into the bite angle.
- Checks: `verify_p0_people.py`, `build_guides.py check --profile p0`, staged and live `check_api.py`, all 111
  served files equal to the local renders by sha256.

## Promote and archive (2026-11-10)

- Approved drafts join through `guides/p0/promoted.json` (`guides`: id -> source, decision, `after`, record;
  `archived`: old id -> replacedBy). `p0_catalog.registry()` places each one right after its `after` guide and marks
  the archived ids `availability: archived`; shot types, `build_bundle.py`, `check_p0.py`, `verify_p0_scene.py`,
  `verify_p0_people.py` and `p0_gallery.py` skip archived ids.
- Files: copy the draft `render/` to `catalog/p0/animations-light/<id>/`, then
  `$PY -I guides/blender_motion/export_p0.py catalog/p0/animations-light/<id>`; levels in `guide_levels.json`.
- Archive: `archive/guides/<date>/<id>/renders/` and `animations-light/`; `ARCHIVE.json` lists every move. Restore =
  move back and remove the id from `promoted.json` `archived`.
- `build_guides.py check --profile p0` works again: `scenes.py` imports `guides/tools/primitives.py`, a copy of the
  retired shot-overlay skill's module.
- Step length (owner 2026-11-10): `step_fields.step_seconds` gives a guided step's seconds (first guide's loop or the
  line's time plus 1 s, at most 8); write the result into the part's step and shotPlan `seconds` when a guide list
  or line changes, then `check_scripts.py`. Scriptwriter `server.py` repeats the rule for written steps; restart the
  server after changing it (`nohup /opt/homebrew/bin/python3 server.py --port 8765 >> ~/Library/Logs/scriptwriter-server.log 2>&1 &`).
- Byte check after a live build: sha256 of every `overlays/p0/` file named in the served `shot_types.json` equals
  `guides/p0/renders/<name>`.

## Re-render promotion and publish (2026-11-12)

- Same id re-rendered: an entry in `promoted.json` `guides` whose id already exists in the registry replaces that
  record in place (`decision: rerender` for brief/addition guides; promoted records keep their entry with `source`,
  `previousSource`, `revisedOn`). The replaced files move to `archive/guides/<date>/<id>/renders/` and
  `animations-light/` (`ARCHIVE.json`: from, to, sha256); restore = move back and restore `promoted.json`.
- New guides offered only by the steps that name them: `"inherited": false` in their `guide_levels.json` level keeps
  them out of the shot type's inherited first-five (`step_fields.inherited_guides`, used by check_scripts and
  build_bundle). Delete the flag to let a guide join inherited steps. The Scriptwriter server's written-step
  suggestions still take the shot type's first five from `shot_types.json`.
- Per-guide character fade: a scene module may set `state['character_stroke_opacity']`, a callable taking the
  character stroke points in world space (N x 3) and returning a per-point factor; `render_p0.py` multiplies it into
  the baked opacity after the height fade and writes `character_peak_opacity` into each `performance_checks` row
  that has a `frame`. No callable = unchanged output. `entrance_friend_static` uses it for the 1.5 m fade past the door.
- `verify_p0_scene.py` and `verify_p0_people.py` still stop on the first guide that breaks their old-library
  expectations (menu_board_tilt_up_v2 lens 48 mm, unchanged by this round; a back-camera person guide outside the 0.8-1.5 m face
  distance), known since 2026-11-10; their reports
  are not rewritten when they stop.
- Publish order used: re-export every approved render to scratch and compare bytes with its export, spot re-render,
  promote, `p0_catalog.py` (plan.json), parts + `check_scripts.py` (parts, then `--merge`), `build_guides.py check`,
  `asset_manifest.py write`, `guide_index.py`, stage, staged `check_api.py`, diff against live and the pre-preview
  catalog, live build with a backup of every overwritten live file, live `check_api.py`, byte check (disk and HTTP),
  `script_review_page.py`.

## P0 scope (2026-11-12)

- `scripts/p0_scope.json` `hiddenUntil` lists scripts kept out of the P0 catalog (the 5 food-review variants until
  P1); `build_bundle.py --profile p0` drops them with their steps and keyed records. Release one = delete its id and
  rebuild; the parts and guides were never removed.
