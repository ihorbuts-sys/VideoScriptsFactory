# Guides (agent 03)

## Watercolor live-guide artwork

The approved replacement style uses image_gen artwork with loose monochrome watercolor washes, no mouths,
two visible hands maximum, visitor-accessible viewpoints and alpha scaled by 0.5 programmatically. These are
artwork layers for live guide animations, not replacements for the script previews.

Work is staged in `watercolor_motion/`: each guide's exact description, source camera path and keyframe times
are in `manifest.json`; untouched generated six-view atlases are in `originals/`. Reference atlases come from
the existing guide animation and 3D strip. Script-preview scenes do not specify camera geometry.
Apply 50% alpha only in the final batch after all keyframes have been generated. Preserve RGB and originals.
The approved functional study is `shot-proof/cup_eye_orbitr_cc/` and `../catalog/style-study/index.html`.
Code may crop cells and interpolate generated viewpoints; it must not invent perspective by moving a flat
scene. Check angle, framing, movement direction, perspective and destination before publication.

```sh
python3 tools/guide_keyframes.py plan
python3 tools/guide_keyframes.py accept GUIDE_ID GENERATED_PNG
```

The earlier `watercolor/` batch was rejected because scene illustrations failed to teach the prescribed
angles and moves. Do not publish that batch or rerun its planner. Its renderer and asset acceptance commands
reject that manifest. The canonical schematic and 3D assets still contain the original exports until the new
guide-specific set passes review. Native sensor scenarios and script-preview JPEGs remain source inputs.

One live guide per script step, in two visual styles, for the 56 scripts and 304 steps of
`scripts/script_templates.json`. Everything here is generated from `tools/`; edit the tools, not the outputs.

| Output | What it is |
|---|---|
| `script_templates.json` | The catalog with every step's `overlays` set (one guide id per step). Copy over the kit's resource together with `templates/`, `overlays/schematic/*.png` and `scenarios/`. |
| `templates/<id>.json` | Scene source (shot-overlay format) per guide: elements, 25% white fills, 9:16 camera timeline, no annotations, `live` block with the pinned steps. Reused kit scenes are copied here with labels, motion hints, instruction glyphs and timed accent hint lines removed and their kit steps pinned. |
| `overlays/schematic/<id>.png`, `<id>_strip.png` | The schematic style: shared-palette APNG at 405 x 720, 15 fps, white lines and yellow accents (the kit's own theme, `style` block in every scene), plus a 6-frame strip. |
| `overlays/3d/<id>.json`, `<id>_strip.png` | The 3D style: which subject model, its size in metres, the look-at point, and the camera keyframes at every step boundary (distance, elevation, azimuth, yaw, pitch, lateral offset); a wireframe preview at the start, middle and end of each move. |
| `overlays/3d/models/*.usdz`, `index.json` | Subjects the kit's `GhostSubjectView` lacks, as USD primitives in metres with footprint and look-at, validated with `usdchecker`. |
| `scenarios/<id>.json` | Compiled live scenarios (`compile_template.py` with the shot-overlay primitives for the ghost). |
| `coverage.md` | Per step: guide, style assets, reused or new, angle, move, hand-over, jump check, simulation, what the ghost cannot verify. Per guide: the compiled step chain and build notes. |
| `compile_report.md`, `compile_check.md`, `kit_check.txt`, `jump_check.json`, `simulation.txt`, `build_notes.json` | Check outputs (see below). |

## Decisions

- **One guide per step.** The shot plan fixes the move, so no step offers a choice; steps with the same subject
  and shot signature share a guide (178 guides for 304 steps).
- **Reuse only on an exact fit** of subject, angle, framing, move and hand-over: 14 kit scenes qualify
  (`tools/catalog.py`, `REUSE`). Near fits that differ in direction, hand-over or subject got a generated scene.
- **No viewfinder frame in the artwork.** The kit's `check.py` requires `focus: null`, `mask: 0`: the app draws the
  fixed viewfinder. The subject carries the move: it grows on a push-in, slides on a pan or truck, lifts on a tilt
  down, turns on an orbit (seven cross-faded poses 10 degrees apart), streaks and leaves on a whip.
- **Hand-overs.** A `push-through` ends with the subject's plain surface filling the frame; a `whip` ends with a flick
  off to the right and streak lines; `match-cut` and `pull-back-reveal` need nothing beyond the subject ending
  centred, so they share the plain scene (the next step's own start framing is the detail). `reveal-from-behind`
  is drawn as a truck out from behind a foreground blocker (a plant, a wall edge, or the creator's cup).
- **Timings.** Start pose 1.2 s (the ghost's frame step), one move of 1.8 to 3.2 s, a hold, the hand-over; 4.7 to
  7.0 s per scene within the step's own length.
- **Subject actions** (a pour, a tear, hands at work) are drawn on as elements appearing, never as a cut; the
  scenario carries them as timed `still` steps. Two reused scenes (`before_front_back`, `pastry_tear_open`)
  swap the subject drawing for the action itself; that is the subject turning or tearing, not the camera.
- **Tilt bands** per angle: top-down 85, high 45, eye-level 0, low -12, pov 10, over-shoulder 20 degrees; selfie
  from above 30. They are pinned in every `live` step, so the compiler's text heuristics are not relied on.

## Rebuild

Python with Pillow and NumPy (`GUIDES_PY`), ffmpeg, and the Pixar USD tools (`usdzip`, `usdchecker`).

```sh
cd guides/tools
python3 catalog.py                                   # the step -> guide table
python3 build_guides.py templates                    # scenes + script_templates.json
GUIDES_PY=/path/to/python build_guides.py render     # schematic APNGs and strips
GUIDES_PY=... python3 build_guides.py compile        # scenarios + compile_report.md + compile_check.md
GUIDES_PY=... python3 build_guides.py check          # the kit's check.py over every scene
GUIDES_PY=... python3 build_guides.py jumpcheck      # jump_check.json
GUIDES_PY=... python3 build_guides.py simulate       # simulation.txt
/path/to/python render_3d.py                         # 3D specs, strips, usdz models
python3 coverage.py                                  # coverage.md
```
