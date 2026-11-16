# Guide style (P0 line art)

The one style every new shot guide follows. Where this file and code disagree, the code named in brackets is what
renders; fix whichever is wrong and keep both in step. Older styles (watercolor sketches, schematic overlays, glass
hologram, clay colour, 25% white fills, baked 65% opacity) are retired and must not be used.

## Output

- APNG 405 x 720, 15 fps, transparent, `alphaFactor` 1. The app applies 65% opacity before recording and 30% while
  recording; never bake opacity into the file. A 120 x 213 selector loop and a poster (frame 0, the target frame)
  go with every guide. [render_p0.py, export_p0.py]
- Clock: 8 frames on the target, an optional 15-frame setup beat (props only), the move (`durationSec`), 7 frames on
  the target; the first frame equals the last and the poster. [render_p0.py, export_p0.py]
- Alpha coverage under 35% per frame. [export_p0.py]

## Drawing

- Native Blender line art: white contour 3 px over a black underlay 5 px at 55% alpha, contour only (no creases),
  constant pixel width. [lineart_render.py strokes_setup, render_p0.py contour_only]
- No shaded or filled surfaces, no walls, floor or ceiling unless one edge explains the framing, no text, labels,
  arrows, phone glyphs or viewfinder; the app draws the sight, the grid and the caption. [render_p0.py]
- Opacity by role: hero 1, character 1, hand .65, support .60, important background .76, foreground .36, background
  .20, structure .24, lighting cue .55, drink contents .72. Hero clearest, context faintest. [p0_scenes.py ROLE_ALPHA]
- Yellow light edges (1, .73, .17) only on chosen source-facing rims; a warm halo 0.65 px at 10% (steam 1.5 px at
  28%), colour (255, 202, 72). [render_p0.py, export_p0.py]

## Framing and motion

- The hero sits inside the top 28% / bottom 35% band at the target frame (the editor keeps the bottom 35% and top
  14% clear at export). [render_p0.py, export_p0.py]
- Objects are present from frame 1; only the camera moves, except actions inside the scene (a pour, a hand, steam)
  that keep real contact. The file ends on the target: no whip streaks, no push-through, no next-step object.
- Every camera position is a phone in a hand, on a table or on a napkin; camera speed at most 1.3 m/s (selfie
  .25). [check_p0.py]
- Visitor side only: no kitchen, pass, till or behind-the-counter position; staff hands may enter from the far side.
  [check_p0.py]
- A `triangle` composition draws three faint 6 px dots at the target frame.

## Phone orientation

- Every guide states the phone orientation: `portrait` (lens at the top edge, the default) or `portraitUpsideDown`
  (the phone flipped so the lens sits at the bottom edge). Upside down is the way to get the lens within a few cm of
  a table, counter or floor; some shots only work that way. List: `guide_levels.json` `orientation`.
- P0 scripts offer portrait guides only (owner 2026-11-10); upside-down guides stay in the library for later. A
  guide's camera height must be reachable in its orientation (a portrait lens is about 1.5 cm below the phone's top).
- The recorder freezes the clip's rotation from gravity (90 portrait, 270 upside down), so the clip stays upright
  either way; the guide must say "turn the phone upside down" as its first beat when it needs it.

## Objects

- The standard is the code-built P0 object set (procedural cup, saucer, plate, pasta, glass, table, chair, door,
  sign, counter, board, card...) and the approved outside pieces in active guides (milk pitcher, gooseneck kettle,
  Tripo pizza and salad, the canonical creator rig, CC0 hands). Owner ruling 2026-11-10.
- A new object, or an existing model new to line art, joins only after the owner approves a line-art render of it.
  Agents never generate or buy a model on their own: they write an object request (see guide-objects).
- Dish guides show pasta on a dinner plate by default; per-kind dish variants (pastry, pancakes, pizza, salad, from
  2026-11-14) replace it by the chosen dish. Personal dishes sit at usable place settings, never at the table centre.
  [table_composition.py]
- Place setting per dish (owner rule 2026-11-15; code table `PLACE_SETTING` in `guides/blender_motion/drafts/plate_dishes.py`):
  the dessert kind (one shared dessert object stands for every dessert; no per-dessert renders) sits on a dessert
  plate (about 8 in), ideally with a dessert
  spoon and a dessert knife beside it; pastry, pizza and every bakery item get no knife, spoon or fork; mains and salad
  keep the dinner plate with fork and knife about 3/4 in (2 cm) clear of the plate edge; pancakes use the dessert plate
  with fork and knife. A dish kind not listed asks the owner before rendering. Cutlery that is not in the approved set
  (dessert spoon, dessert knife) is an object request first; until approved, the dessert plate is used without it.

## People and hands

- At most two visible hands in a frame, counted across all people; partial hands count; never detached or
  duplicated. Hands fade from the grip. [render_p0.py, hand-pose-references.md]
- Hands must read as 3D (owner review 2026-11-10): never seen edge-on as a flat cut-out; turn the hand so the back of
  the hand, the knuckles and separate fingers face the lens (about 30-45 degrees off edge-on); the forearm keeps its
  real length (a cuff extension of at most about 10 cm), never stretched into two thin lines. Hands and forearms never
  pass through a plate, glass, cup, table or counter on any frame.
- The CC0 hand mesh's local +Z is the palm side: a hand resting on a rim or table is placed with its palm normal pointing
  down, fingers curled gently onto the surface (owner pick 2026-11-10, counter hands variant a).
- People are the canonical creator rig only; faces stay schematic and keep the creator's mouth line (owner ruling
  2026-11-10); no teeth or lip detail. Front-camera guides are mirrored only in the final preview.

## Library

- A replaced guide is archived (registry `availability: archived`, files under `archive/guides/`), never deleted; it
  can be restored. A step may offer up to 5 guides of its level (owner 2026-11-10).

## Checks before a guide is offered

`build_guides.py check --profile p0`, `verify_p0_scene.py` (and `verify_p0_people.py` for people) in Blender, the
browser playback check for people guides, and an owner look at the player page. Commands: `catalog/p0/RUNBOOK.md`.
