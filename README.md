# VideoScriptsFactor: content production for Loca Video Studio

This repository produces the content the Loca app's guided video studio shows: the scripts (steps, text versions,
opinion and amenity choices), the animated shot guides, and the 3D objects the guides are drawn from. The app and the
backend only deliver this content; this repo is where it is written, checked, reviewed and published.

Product and data contract: the backend doc https://claude.ai/artifact/NJqhqCnNRdy4E3UZ6Gok8A (tabs PRD inputs,
English, API contract, Decisions).

## What is where

| Folder or file | What it holds |
|---|---|
| `skills/`, `agents/` | Written instructions for each production job (script composer, guide animator, guide objects, object renderer, guide publish). Plain documents: people can follow them, and Claude Code runs them as skills and agents. `step-previews` is no longer used (the design has no step pictures). |
| `scripts/_parts/v3/` | The source of catalog version 3: the four review kinds, steps, text versions, variants, choice sets, kind and subject tables. |
| `scripts/catalog_v3.json` | The built catalog, the file the backend serves. |
| `scripts/versions/` | Snapshots of earlier catalog versions and `restore.py` for rollback (dry run by default). |
| `scripts/tools/` | Checks (`check_scripts.py --v3`, line rules, tests) and `sync_media.sh` for media. |
| `research/` | Best practices, spoken-line research, commercial shot vocabulary, sources, the v3 design record and the guide work list. |
| `guides/blender_motion/` | Scene code for every guide (Blender, line-art style). |
| `guides/tools/` | Export, checks, review pages and the review server. |
| `guides/p0/` | The published guide set: registry, levels, labels, export checks. |
| `guides/revisions/<day>/` | Drafts under review: request, record, contact sheet, export. |
| `scriptwriter/` | The AI script writer server (it writes text versions on request with the same rules) and its menu bar app. |
| `STYLE.md` | The one visual style, place settings per dish, units. |
| `OBJECTS.md` | The object library: approved objects, candidates, open requests and the owner's decisions. |
| `GUIDE_INDEX.md`, `WORKFLOW.md` | The guide index and the roles. |
| `media_manifest.json` | Every media file with its size, checksum and place on Drive. |

## Media lives on Google Drive

Git keeps text only. Animations, posters, 3D models and music are in the Drive folder VideoScriptsFactor-media,
listed in `media_manifest.json` with checksums:

```
music/                         tracks and music data
guides/apng/<guide_id>.png     animated PNG (iOS)
guides/webp/<guide_id>.webp    animated WebP (Android)
guides/posters/<guide_id>.png  poster frames
models/<object>/...            3D models needed to re-render (approved only)
object-approvals/...           line-art approval renders (optional)
```

```
scripts/tools/sync_media.sh download     # get everything into this checkout, checksums verified
scripts/tools/sync_media.sh status       # what is missing or extra on Drive
scripts/tools/sync_media.sh upload --dry-run
scripts/tools/sync_media.sh upload       # makes the WebP files, uploads, verifies
```

The script only ever writes inside that Drive folder. It prints the rclone setup if rclone is not configured.

## Prerequisites

- Python 3 (with Pillow for media upload).
- Blender 5.2 LTS, run in background mode only.
- rclone with a Google Drive remote named `gdrive` (see `sync_media.sh`).
- Claude Code, to run the skills and agents.
- For new 3D models: a Tripo account. Before every paid run, estimate the credits with a dry run and get the owner's
  go-ahead; no model is generated or bought without an owner decision.

## How content is made

Texts:
1. Compose or change steps and text versions in `scripts/_parts/v3/` (script composer skill).
2. Build and check: `python3 -I scripts/tools/check_scripts.py --v3 --merge` must report 0 errors.
3. Owner review of the texts.
4. Publish a new catalog version (guide publish skill); the previous version stays restorable.

Animations:
1. A guide request (what to film, which step, objects, camera) in `guides/revisions/<day>/<group>/<id>/request.md`.
2. Every new object is approved by the owner from a line-art render first (object renderer, `OBJECTS.md`).
3. The guide animator builds the draft: scene code, render, export checks, contact sheet.
4. Owner review on the drafts page: approve, needs work or reject, with comments.
5. Publish the approved guides (guide publish skill), then upload media (`sync_media.sh upload`).

## Review pages

```
python3 -I guides/tools/review_server.py      # serves on http://127.0.0.1:8770
```

- `/review/objects.html`: objects, candidates and open requests with pictures.
- `/revisions/<day>/drafts.html`: draft guides with approve, needs work, reject and comments.
- `/review/scripts.html`: scripts and their guides.

Decisions are saved in `guides/review/decisions/`.

## Rules that always hold

- No prefilled opinions: a judgement only comes from the creator's choice (3 levels: neutral, good, very good,
  plus their own words; Not for me on verdicts is the private way out for a bad experience). Nothing is preselected on a verdict.
- Every text passes the line checks (no hearsay, no teasers, captions are facts only, timing fits the step).
- US units in every text. No emoji anywhere.
- Place settings follow `STYLE.md` (desserts on a dessert plate; pastry, pizza and bakery items with no cutlery).
- Nothing is published without the owner's approval.
- Replaced versions are archived, never deleted.

## Versioning and rollback

Each catalog version is snapshotted under `scripts/versions/<version>/` with checksums.
`python3 -I scripts/versions/restore.py <version>` shows what would change; add `--apply` to restore.

## Handoff acceptance

The receiving team takes over when it has, on its own and with the checks passing:
1. added one new text version to a step and published it in a new catalog version that can be rolled back, and
2. produced one new guide end to end: request, draft, owner approval, publish, media upload.

Older pipeline notes are in `PIPELINE_HISTORY.md`.
