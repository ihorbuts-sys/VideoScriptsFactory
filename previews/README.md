# Step previews

The export set covers 304 previews across 56 scripts using 276 unique illustrations: 252 generated
illustrations and 24 original project illustrations. Original project artwork serves 38 steps; 28 steps share
another step's illustration. Every step keeps its own PNG master and JPEG export for compatibility.
Open `index.html` to review scripts at card size and at 72 pixels high.

New requirement: every camera viewpoint must be accessible to ordinary visitors. Earlier image approvals
predate this constraint. The targeted review in `viewpoint-audit.md` flags existing staff-side views for
correction; this set is not yet cleared under the new rule. No images were regenerated during this policy
update. Export validation checks files and references, not physical visitor access.

At most two visible hands total per image, including partial hands and hands across all people. Use fewer
where possible, frame other hands out, and reject extra, duplicated or detached hands. This applies to future
generation and reuse; earlier image approvals do not certify compliance with this new requirement.

Makeup scenes use a more schematic treatment: simple face contours, minimal facial marks, flat accent areas
for cosmetics and a clear applicator/action. Avoid realistic skin texture, detailed eyes or lashes and glossy
beauty shading. Apply this style check to generated and reused images.

- `<template>_<step>.png`: 1080 x 1920 PNG master requested by the phase 02 brief.
- `<template>_<step>.jpg`: matching 1080 x 1920 JPEG with the catalog's exact imageURL filename.
- `prompts.md`: original prompt for retained images, actual generation prompt for new images.
- `manifest.json`: source path, source size, prompt, shot plan and review status for every step.
- `review.md`: coverage, replacements, rejected attempts and remaining missing images.
- `review-strips/`: one contact strip per script, including the small thumbnail scale.
- `validation.json`: export size, format and catalog coverage audit, produced by the validation command.
- `reuse-map.json`: the canonical illustration used by each step, including shared groups and source counts.
- `shared_catalog.json`: derived script catalog pointing to 276 canonical JPEG resources for later integration.
- `reuse-plan.json`: reviewed reuse choices and reasons, including rejected candidates.
- `reuse-audit/superseded/`: original exports and metadata preserved before applying reuse.

New scenes are generated with the built-in image_gen tool, one call per image. The existing
`bakery-fresh-batch_oven.jpg` in VideoEditorKit is both retained artwork and a style reference. The first newly generated
`bakery-fresh-batch_pick` used no reference. Original generated files remain in the image tool's output
directory, with paths recorded in the manifest. Retained images were upscaled from 720 x 1280.

Each preview depicts the starting framing and angle in `shot_plan.json`. Concrete venue and product
examples keep related steps coherent; these are recorded in `continuity.json` and the individual prompts.
Signs, tags, schedules and price lists use blank blocks and pictograms so the app can supply the real text.
Review checks both card size and 72-pixel strips. Rejected generations and their reasons stay in the manifest.

Prefer existing project artwork, then share reviewed illustrations when the subject, viewpoint and starting
framing fit. Do not share solely because two shots have the same framing. For example, the beer-review sip
and verdict retain their pint illustrations to keep the drink consistent. Reuse assignments copy canonical
exports under each step's existing filenames; use `shared_catalog.json` and only its referenced JPEGs to
bundle the smaller resource set. The research catalog remains unchanged.

`tools/preview_assets.py` requires Pillow. It performs export normalization and contact-strip assembly;
it does not draw or generate the scenes and does not call an image API. Run from any directory:

```sh
python3 tools/preview_assets.py report
python3 tools/preview_assets.py validate
```

To reapply the reviewed reuse plan, run `python3 tools/reuse_assets.py`, then regenerate the report and
validation. This helper normalizes original project images and copies reviewed exports; it generates no art.

The example assumes this previews folder is the working directory. Use a Python environment with Pillow.
To resume generation, read pending entries from the manifest, call the built-in image tool with their
recorded prompt, all mandatory constraints in `prompts.md` (visitor access, hand count and schematic makeup),
and style reference, then use
`accept --stem ID --source PATH`. Adapt any conflicting camera direction before generation and review the
actual viewpoint before approval. Accept images sequentially
so the manifest has a single writer. Review each script strip before using `approve --template ID`.
Regenerate the review page with `report` after approving. Rejected attempts belong in the entry's
`attempts` list with a reason before regeneration.

No kit resources or script catalog files are changed by this phase. The PNG masters and JPEG exports
are staged here for the later integration and PDF phases.
