# Brief 03: live guides in two styles

Skills to load, in this order: `live-guide-authoring` (`Loca/.claude/skills/live-guide-authoring/SKILL.md`),
then `shot-overlay` and `live-shot-guide` as it tells you to.
Input: `ScriptsAndGuides/scripts/script_templates.json` and `scripts/shot_plan.json` from agent 01.
Output folder: `ScriptsAndGuides/guides/`.

## What a guide must show

A guide is a short animation a creator watches, then copies with the phone. With no text it must make three
things obvious: the angle to shoot from, the camera move during the shot, and how this shot hands over to the
next one. The subject is the storyteller: it grows when the camera pushes in, shrinks when it pulls out, shows
its far side on an orbit, shows its top on a tilt down, streaks on a whip. The viewfinder frame moves with it.

The subject moves continuously between poses. It is never cut or teleported to a new position or angle: a change
of angle is shown as the subject turning and the frame travelling there over 1 to 2 s, a change of size as the
subject scaling, a change of place as it sliding. If a guide shows two angles, the animation travels from the
first to the second; the creator sees the path, not two pictures.

There are no per-step hints inside the animation: no icon badges, no hold timers, no edge glows, no arrows that
appear and disappear per move. A guide is a starting pose plus one continuous animation. The app helps the
creator take the starting pose (the ghost at its first frame until the subject is framed), then plays the whole
animation; the only live feedback is a faster or slower cue when the creator's pace drifts and one clock for the
whole animation. So the animation must be self-explanatory end to end.

## What to deliver

1. A shot guide for every step of every script, built from the step's shot-plan entry (`angle`, `start`, `end`,
   `move`, `transitionOut`). Reuse one of the 60 existing guides where angle, move and framing match
   (`VideoEditorKit/Sources/VideoScripts/ShotScenarios/`, coverage in
   `Loca/.claude/skills/live-shot-guide/references/template-coverage.md`); author a new scene for anything else.
   Set each step's `overlays` in a copy of `script_templates.json` saved as `guides/script_templates.json`.
   Where `transitionOut` is not a plain cut, the guide's last second shows the hand-over (the subject filling
   the frame for a push-through, the frame flicking off for a whip) and the next step's guide starts from that
   pose.
2. Two visual styles of every guide:
   - `guides/overlays/schematic/`: the hand-drawn-looking schematic overlays the `shot-overlay` skill renders
     (APNG, 9:16), with a theme file for the look chosen.
   - `guides/overlays/3d/`: the 3D scene for the same shot: the subject model (the kit draws cups, plates, glasses,
     pastries, people, storefronts, rooms, taps, ovens, cases, menus, plants and lamps procedurally in
     `VideoEditorKit/Sources/VideoCaptureKit/GhostSubjectView.swift`), the camera path of the move, and a
     rendered preview strip (PNG) per guide. New subjects go in as `.usdz` plus a note on size in metres and the
     point the camera looks at.
3. `guides/scenarios/*.json`: the compiled live scenarios for every new scene (`compile_template.py`), run
   through `simulate.py`; the healthy numbers are listed in the live-shot-guide skill.
4. `guides/coverage.md`: per script step, the guide used, its style assets, whether it was reused or new, and
   anything the ghost cannot verify (the subject's own action, absolute height).

## How to work

- Updated art direction: generate the artwork with image_gen as a loose sketch with one translucent
  watercolor pigment spilling beyond its contours. Keep the approved pale pigment, omit mouths, and preview
  opacity changes without darkening the pigment. The user authorizes programmatic alpha adjustment of the
  full generated image; the current study saves 50% opacity in the PNG and applies no extra display opacity.
  Do not construct or trace the illustration in code.
  Review one generated image before expanding to all guides. Code can animate the approved artwork and
  apply the yellow tint when the tracked subject is caught. See `catalog/style-study/README.md` for the
  current generated sample and provenance. Earlier primitive-based rendering instructions do not override
  this direction.
- Keep makeup scenes schematic: simple facial contours and minimal feature marks, with the applicator and
  application action clear. Avoid realistic skin texture, detailed lashes or eyes and glossy beauty shading.
- Show at most two visible hands total in any animation frame, including partial hands and hands across
  different people. Apply this to reused guides too; avoid extra, duplicated or detached hands.
- Follow the visitor-access rule in the pipeline README. The whole camera path must stay in space accessible
  to ordinary visitors. Adapt any staff-side starting pose or move before authoring a guide and record the
  change; a preview or existing guide is not evidence that a restricted viewpoint is acceptable.
- The guide plays as a ghost on the scene's clock (see `VideoEditorKit/docs/guided-take-flow.md`): design moves
  that a first-time creator can follow in one go, 2 to 4 s each, no more than two moves per shot.
- A shot is a starting pose, one move, one hold, then the hand-over, as one animation. Longer stories are
  several steps; the chain across steps is in the shot plan, keep it.
- Scenes still compile into steps, but only as the simulator's and the tests' form and as the keyframes of the
  ghost path; the app plays one continuous path and scores the take as one curve, naming the move during the worst
  stretch in its single tip. Keep every move in a scene a single named move. Author scenes without `label`
  annotations and with `aspect_label: false` in the focus style; existing scenes reused for guides get their
  labels removed.
- Check every animation for jumps: play it frame by frame; any frame where the subject's size, position or
  orientation changes by more than the move's speed allows is a defect to fix with intermediate keyframes.
- Keep the visual language of the existing guides (white lines, yellow accents) unless the theme is changed for
  the whole set.

## Done when

Every step has `overlays`, every overlay exists in both styles, every animation moves the subject continuously
(no jump between poses), every new scenario simulates healthy, and `coverage.md` has no empty rows.
