---
name: guide-animator
description: Builds one animated shot guide for Loca in the approved P0 line-art style from a guide request, as a draft in the script's folder - template choice, object check, scene code, Blender render, export, checks and a contact sheet. Use inside the guide-animator agent for one request at a time; it stops with an object request when a model is missing and never publishes.
---

# Guide animator

Repo root: `~/Documents/Development/VideoGuides`. Read first: the request file you were given, `STYLE.md`,
`references/framing.md` (camera numbers with research references),
`OBJECTS.md`, `GUIDE_INDEX.md`, `catalog/p0/RUNBOOK.md`. Environment: Blender 5.2.3 at
`/Applications/Blender.app/Contents/MacOS/Blender` (background only, never the UI unless the owner asks), Python
`PY=/private/tmp/loca-p0-people-venv/bin/python3` (recreate from
`model_refferences/objects/tools/guide-packaging-requirements.txt` if missing).

## 1. Template

Pick the active guide closest to the request: same move first, then the same object family (`GUIDE_INDEX.md` Swap
column: cup, dish, glass). Its record is in `guides/p0/plan.json`; its scene code is the `gid` branch in
`guides/blender_motion/p0_scenes.py` (people: `p0_people.py`, shared tables: `p0_table_compositions.py`).

## 2. Objects - stop if any is missing

List every object the frame needs (hero, support, background, hands, people). Each must be in the code-built P0 set
or an approved outside piece (`OBJECTS.md`, `STYLE.md` "Objects"). A missing object, or a model never rendered in
line art: add a row to the `OBJECTS.md` requests table (object, for which guide, why, the nearest existing object,
your suggestion) and to the request file, then stop and report. Never generate, buy, reconstruct or download a model,
and never substitute a different-looking object without saying so.

Place setting: a dish follows the per-dish place-setting rule in `STYLE.md` "Objects" (owner rule 2026-11-15):
desserts on a dessert plate with a dessert spoon and knife when approved; pastry, pizza and bakery items with no
cutlery; mains and salad with fork and knife 2 cm clear of the plate. List the place setting you used in the report.

## 3. Draft

Work in `scripts/<kind>/<template id>/guides/<guide id>/`:
1. `record.json`: copy the template's record from `guides/p0/plan.json`; set `id`, `title`, `shotType`, `technique`,
   `durationSec`, `startTrigger`, `invariant`, `camera`, `composition`, `phoneOrientation` (`portrait` or
   `portraitUpsideDown`, from the request; see `STYLE.md` "Phone orientation"), and `sourceScene` = the template id.
   The camera height must be reachable in that orientation; an upside-down guide's first beat says to turn the phone.
2. Scene code: add a branch for the new id next to the template's branch, reusing its builders; change only what the
   request asks (object, camera path, timing). Do not change shared builders the active guides use. If you must,
   re-render every guide that uses that builder to a scratch folder and compare frames (RUNBOOK reproducibility
   check); report any guide that changes.
3. Render: `Blender -b --python-exit-code 1 -P guides/blender_motion/render_p0.py -- --id <guide id> --record
   <folder>/record.json --out <folder>/render` (a `--probe target` single frame first is cheaper while composing).
4. Export: `$PY guides/blender_motion/export_p0.py <folder>/render --out <folder>/export`: its asserts are the gate
   (clock and holds, first frame = last frame, hero band, alpha, hands, people). For people guides also run the
   checks of `verify_p0_people.py` on the draft scene.
5. Hands (any guide with a hand): check a 2x crop of each hand at the start and middle frames (it must read as a 3D
   hand, not a flat shape or two thin forearm lines) and measure the minimum distance per frame between the hand skin
   and every plate, glass, cup, table or counter mesh (no vertex inside); report both. `STYLE.md` "People and hands".
6. Contact sheet: five frames (start, 25%, middle, 75%, end) on a dark ground, `<folder>/sheet.png`.
7. Complex guides: write the 2-4 beats (`atSec` ascending and below `durationSec`, <= 70 chars, imperative, one action
   each) into the request; easy guides have none.

## 4. Report

Return: the folder, `sheet.png`, the export check line, the beats, the camera numbers you used with their reference
ids or "(judgement)", every assumption about objects or placement, and
anything you could not do. The owner reviews; promotion and publishing belong to `guide-publish`.
