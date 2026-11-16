---
name: guide-objects
description: The object library and style gate for Loca's shot guides - which 3D objects exist in the approved line-art style, which guides share an object builder (swap families), how to vary an object on an existing animation, and how to request a missing model from the owner. Use before composing or animating a guide that needs a specific prop, food, drink, furniture, hand or person, and for any brand-style audit of objects.
---

# Guide objects

Repo root: `~/Documents/Development/VideoGuides`. Sources: `OBJECTS.md` (inventory, audit, requests), `STYLE.md`
"Objects" and "People and hands", `GUIDE_INDEX.md` (Objects and Swap columns), `assets/manifest.json` (pinned files).

## The standard (owner ruling 2026-11-10)

The code-built P0 set (`guides/blender_motion/assets.py`, `venue_assets.py`, `food_assets.py`, `geometry.py`, the
builders in `p0_scenes.py`) plus the outside pieces in active guides: milk pitcher, gooseneck kettle, Tripo pizza and
salad, the canonical creator rig, the CC0 para hands. Everything else (about 40 Tripo families, 13 TripoSR clay
props, the 4 Nov line-art study objects) is unverified in this style until the owner approves a line-art render.

## Swapping an object on an existing move

The guides in a swap family share one builder (`guides/tools/guide_index.py` FAMILIES): changing that builder changes
the whole family. A variant (another cup shape, another dish on the same plate) is a new builder or a parameter used
only by the new guide id; the family's template guide and the others keep rendering the same, which the animator
proves by re-rendering them to scratch and comparing frames.

## Which guides to re-render after an object change (owner rule 2026-11-11)

Re-render only the guides where the changed object is in frame and the change is noticeable at that guide's
distance and angle: close compositions and table-scale shots, yes; exteriors, far interiors, shots where the object
is out of frame or covered (a table ring under a cup on its saucer, a machine-top change in a shot that never shows
the machine top), no. Decide per guide from its poster and target frame (object visible? change larger than a few
pixels?) before rendering, and list the skipped guides with one-line reasons in the report; the owner should never
have to review a before/after with no visible difference.

## Place setting per dish (owner rule 2026-11-15)

The plate and cutlery follow the dish, as `STYLE.md` "Objects" states and `PLACE_SETTING` in
`guides/blender_motion/drafts/plate_dishes.py` implements: desserts on a dessert plate (about 8 in) with a dessert
spoon and dessert knife beside it when those are approved; pastry, pizza and every bakery item with no knife, spoon or
fork; mains and salad on the dinner plate with fork and knife 2 cm clear of the edge; pancakes on the dessert plate
with fork and knife. A new dish kind gets a row in that table, approved by the owner, before any render.

## Requesting a model

Add a row to the `OBJECTS.md` requests table: object, the guide that needs it, why the existing set does not cover it,
the nearest existing object, a suggestion (code-built shape, existing Tripo model to approve, new Tripo
generation). The owner decides and records the decision in the row; an approved model gets one line-art test render (the `object-renderer` agent),
the owner approves it, and then it is added to `assets/manifest.json` (`guides/tools/asset_manifest.py write`) and
to the inventory. No agent spends credits, generates or reconstructs a model without that decision.

## Generating an approved model (only after the owner's decision in the request row)

- Code-built (procedural, like `fork` or `plain_card`): build it in the owning assets module as a new builder used
  only by the new guide; no credits.
- Tripo: follow the `tripo-cli` skill (`/opt/homebrew/lib/node_modules/tripo-cli/skill/SKILL.md`) and the project
  record `model_refferences/tripo-cli/README.md`. Run Tripo commands from `~/Documents/Development/VideoEditorKit`
  (the project's `.tripo/context.json` lives there), with `TRIPO_CLIENT_APP=claude`.
- Credit estimate before every run (owner rule 2026-11-11, so credits can be bought first): before any paid command,
  dry-run every planned command (`--dry-run --json`, no network, no credits) and give the owner one table: object,
  command, model, each step with its `generation_credits_estimate`, the steps the CLI does not estimate (P1, legacy
  models, `--then` chain steps such as texture, rig, retarget: list them as "not estimated" with the list price from
  `tripo docs --topic commands/generate` / `commands/process` when it states one), the total, the current
  `tripo balance --json` and the shortfall. Raw numbers, no rounding. Nothing is submitted until the owner confirms
  the balance covers it; a run that would need more than the estimate stops and re-estimates. Prefer image input from
  approved reference art (`model_refferences/objects/<name>/design*`). Never `tripo redo`, retry or switch models
  without asking; on exit 6 or 7 recover the existing task id as the README says. Record the task id, credits spent
  and the balance in the README's ledger (`current-balance.json`) and the object's folder
  `model_refferences/objects/<name>/tripo-generated/`.
- Tripo Studio, by hand (owner, 2026-11-11: about 3200 Studio credits, a wallet separate from the API one): for each
  object prepare a hand-off in `model_refferences/objects/<name>/tripo-studio/request.md` - the prompt, the
  reference images to upload (approved art first), the settings to pick, the target size in metres and the face
  budget, what to download (GLB) and where to save it (`.../tripo-studio/<date>/`). The owner generates, saves the file
  and notes the credits spent; record them in the README ledger under a separate Studio wallet line. The request row
  in `OBJECTS.md` says which path (API or Studio) each object takes; the estimate table above lists both wallets.
- Then the `object-renderer` agent renders the candidate in line art; the owner approves that render before the
  model is used in any guide, and only then does it join the inventory and `assets/manifest.json`.

## Audit

Re-run the audit when objects change: inventory with source and status, line-art render check per object, the usage
map per guide, gaps against the current scripts. Mark judgement as such; keep `OBJECTS.md` current.
