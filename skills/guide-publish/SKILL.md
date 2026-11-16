---
name: guide-publish
description: Promotes owner-approved draft shot guides into Loca's active P0 set and publishes guides and scripts to the Scriptwriter development server with a staging diff, API checks and a byte comparison. Use only after the owner approves the drafts or the scripts; never on an agent's own decision.
---

# Guide publish

Repo root: `~/Documents/Development/VideoGuides`. Commands and paths: `catalog/p0/RUNBOOK.md`.
`PY=/private/tmp/loca-p0-people-venv/bin/python3`.

## Promote an approved draft guide

1. Registry: add the guide to `guides/tools/p0_catalog.py` (`additions` with its template, or a brief section in
   `briefs/p0_animations.md`), update the guide-count asserts, add its level and beats to
   `guides/p0/guide_levels.json` and remove it from `pending`.
2. Render in place: `render_p0.py --id <id> --out catalog/p0/animations-light/<id>` then `export_p0.py
   catalog/p0/animations-light/<id>` (writes `guides/p0/renders/`). Compare with the approved draft frames; they must
   match within render noise.
3. Checks: `$PY guides/tools/build_guides.py check --profile p0`, `verify_p0_scene.py` (and `verify_p0_people.py`)
   in Blender.
4. `python3 guides/tools/asset_manifest.py write`, `python3 guides/tools/guide_index.py`.

## Publish

1. Scripts changed: `$PY -I scripts/tools/check_scripts.py --merge` (writes `scripts/script_templates.json`).
2. Stage: `$PY guides/tools/build_bundle.py --out <scratch>/p0-stage --profile p0`; diff `catalog.json` and
   `shot_types.json` against `~/Documents/Development/Scriptwriter/catalog/`; only the intended guides and scripts may
   differ. Then `$PY api/check_api.py --bundle <scratch>/p0-stage --report <scratch>/stage-check.json`.
3. Live: `$PY guides/tools/build_bundle.py --profile p0`, then `check_api.py --base-url http://127.0.0.1:8765
   --token-file ~/Documents/Development/Scriptwriter/.token --bundle ~/Documents/Development/Scriptwriter/catalog`.
4. Byte check: every served P0 file's sha256 equals `guides/p0/renders/` (RUNBOOK snippet). Report counts.
5. Keep a copy of the replaced renders until the owner confirms on the device. Commit only when the owner says so.
