# Blender guide rollout

> **Superseded in part (2026-11-10):** published P0 guides keep `alphaFactor` 1 (the app applies 65% / 30%), not
> baked 65% opacity, and the active pipeline is `render_p0.py` + `export_p0.py`. See `../../STYLE.md` and
> `../../catalog/p0/RUNBOOK.md`.


The live development API now serves 139 reviewed Blender object/hand guides. The initial rollout added 109
object guides; the latest cinematic revision regenerated 33 existing native guides. The 39 people-dependent guides retain their previous artwork and are deferred at the
owner's request. Do not generate faces, heads or full bodies until the owner explicitly resumes them.
Close-up hands remain allowed when they explain an action; at most two may appear in a frame.

There are 173 contextual object-step animations, including 32 explicit transitions into the actual next object
shot. The complete object-only `cafe-morning-ritual` sequence plays for 20.667 seconds. The other
55 full-script sequences await deferred people steps. Original script preview pictures and canonical
scene/scenario definitions are preserved.

Published overlays use 65% whole-image opacity, including their lines; context is fainter.
`api/opacity_assets.py` derives this once from preserved engineering masters.
Lighting and lenses stay fixed. No unnecessary walls, bloom, moving bar lights or inaccessible camera
positions are added. Camera movement uses an ordinary phone: supported holds, short leans, wrist turns,
small steps and reachable heights. A propped phone or helper supports actions that use both hands.

`scene_plans.py` and the scene-family modules review the source description, script contexts,
composition, contacts, lighting and phone feasibility before rendering. `assets.py`, `venue_assets.py`
and `food_assets.py` provide reusable native models. Source-specific actions preserve coherent props,
real perspective, occlusion and actual contact rather than independent generated frames.

`people-policy.json` and the render gate enforce the current people deferral. `rollout.py` handles
bounded background jobs. `verify_rollout.py` checks every exported frame range, including zero visible
people, hand counts, camera reach/travel and fixed lights/lenses. `accept_review.py` binds an explicit
visual review to the exported image hash; do not call it before reviewing the source and images.

`assemble_contexts.py` reuses reviewed frames for the actual per-step object handover. It does not apply
another opacity pass. `build_context_gallery.py` and `build_gallery.py` update the local review pages.
`../tools/build_bundle.py` stages immutable API assets; `../../api/publish_reviewed_assets.py` publishes
the index atomically after copying every referenced file. API scenario adaptations reconcile native
camera angles while leaving canonical source scenarios unchanged.

Review entry points:

- `../../catalog/animations.html`: all 178 guides, defaulting to the 139 Blender object guides.
- `../../catalog/context-animations/index.html`: actual object handovers by script step.
- `../../catalog/blender-regeneration-report.md`: completed/deferred IDs and verification limits.
- `../../api/context-live-api-check.json`: contextual endpoints and asset integrity.

Preview policy: render and verify in the background. Do not open or switch Blender UI unless the user
explicitly requests it. Existing saved Blender projects remain intact; six older projects retain their
archived people stages, while the published animations stop before those stages.

The connected bar/table revision is implemented in `bar_transition.py`: one room, one camera and a
12-second low-truck → aisle turn → high-table lean. `assemble_contexts.py` prefers the reviewed
`continuous_handover` over appending a separate shot. `catalog/context-animations/frame-sources.json`
(relative to the ScriptsAndGuides root) reuses the same table frames for the next script step.

The [27 October revision report](../../catalog/cinematic-revision/report.md) lists all 33 regenerated
guides, continuous handovers, model licenses and verification. `real_hands.py` and the CC0 models in
`vendor/` supply reusable anatomical hands and the detailed acoustic guitar.
`project_gliding_light.py` reads saved projects without modifying them and projects depth-tested
view-dependent highlights before `export_shot.py` composites the preserved master.
Published viewfinders are separate UI: `gallery_ui.py` attaches browser reference controls, while
the camera app renders the live gravity levels. Do not bake that UI into published media.

## Owner composition rules

Personal plates with food must sit at a usable place setting, away from the table centre.
Keep the full plate, cup and cutlery supported. `table_composition.py` enforces this after scene
construction; `verify_table_policy.py` checks saved native scenes and active contextual variants.
Do not confuse the subject’s position in the picture with its physical position on the table.

`hands_during_top_hold` now follows the owner's close-up massage correction: keep the phone fixed
while one anatomical practitioner hand presses, glides and releases over a cropped curved surface.
The proxy surface replaces a complete back model. Keep the forearm end outside the picture,
maintain palm contact and avoid orbiting the camera or pivoting the arm around the wrist.

The cafe follow-up is implemented in `cafe_first_visit.py`. `assemble_contexts.py` ends ordinary cuts
at the owning step, limits independent whip landings to 0.6 seconds, and preserves native connected
camera travel. It no longer appends a complete next animation by default. The morning cup and pastry
reuse consecutive frames from one physical table scene. See [the cafe review](../../catalog/cafe-review/index.html).
