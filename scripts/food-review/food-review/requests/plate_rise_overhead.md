# Guide request: plate_rise_overhead

- Script and step: `food-review.dish` (also listed for `first-visit.plate`, `food-review-sweet.break`,
  `food-review-handheld.cut`); the step is **complex** (silent, beats instruct).
- Shot type: `plate-reveal`. Level: complex. Camera: back. Length: 6 s (`durationSec`). Trigger: motion.
- Title: "Rise over the plate".
- Move: start at a high three-quarter angle about 0.5 m from the plate; over 4.5 s raise the phone smoothly into a
  straight overhead view; end with the whole plate and the cup rim in frame. One continuous rise, no orbit.
- Target frame (end, also frame 0 and the poster): straight overhead, the plate centred, filling about 0.6 of the
  frame width, the cup rim at the upper right; hero inside the 28% / 35% band.
- Objects: the shared example dish exactly as in `plate_low_push_in` (dinner plate with pasta, cup and saucer
  right-behind, fork at the left edge, place setting). No new objects. No hands, no people.
- Template: `table_spread_orbit` for the rise (its camera path) on the dish family's objects (`plate_high_orbit` /
  `plate_low_push_in` scene). Composition: `triangle` (three faint markers at the target).
- Beats (complex):
  - 0.0 Start high, at a three-quarter angle to the plate.
  - 1.5 Raise the phone slowly over the plate.
  - 4.5 Finish straight above with the whole plate in frame.
- Why: the dish step offers two complex single-plate guides (`plate_high_orbit`, `plate_tissue_slide`); this is the
  third. `table_spread_orbit` shows a shared spread and may not sit on a one-dish step (owner ruling 2026-11-10).

## Draft (guide-animator, 2026-11-10)

- Folder: `scripts/food-review/food-review/guides/plate_rise_overhead/` (record.json, render/, export/, sheet.png).
  Export checks passed. No new objects, no object request.
- Beats used (unchanged, `atSec` ascending, below 6): 0.0 "Start high, at a three-quarter angle to the plate." /
  1.5 "Raise the phone slowly over the plate." / 4.5 "Finish straight above with the whole plate in frame."
- Timing: the rise runs 0.0-4.5 s (smootherstep) and holds overhead 4.5-6.0 s.

## Revision 1 (owner, 2026-11-10): precise, simple, cinematic

The guide teaches three things a creator can repeat with a phone: the composition on the table, the angle, one move.
The shot is the classic flat-lay reveal: from the seat, 45 degrees, lift and tilt until the phone is flat above.

- **Composition on the table (fixed for start and end):** plate at the place setting, centred left-right in the
  frame; fork straight, parallel to the plate's left side, about 4 cm from the rim; cup on its saucer at the plate's
  upper right (about one o'clock), its handle pointing right. Plate, cup and fork form the triangle (the three faint
  markers sit on the plate centre, the cup centre and the fork's middle).
- **Start (angle):** the creator's seat side, straight in front of the plate (no side offset); phone tilted 45 degrees
  down, lens about 0.45 m from the plate centre, plate centred in the frame. Nothing else moves the camera sideways.
- **Move:** one continuous crane up with a tilt: the phone rises and tilts together so the plate stays at the same
  place in the frame the whole way; speed eases in and out and uses the full `durationSec` (6 s), no early stop.
- **End (target frame, also frame 0 and the poster):** phone flat, straight above the plate (top-down, no roll: the
  fork vertical in the frame, the table edge horizontal if visible). Plate rim fills 0.55 of the frame width, plate
  centre at 55% of the frame height; the whole cup and saucer and the whole fork in frame with at least 4% margin;
  the plate inside the 28% / 35% band. Lens height above the plate at most 0.70 m (reachable seated or standing).
- **Beats (complex):**
  - 0.0 Sit in front of the plate, phone tilted 45 degrees down.
  - 1.0 Lift the phone slowly, tilting so the plate stays centred.
  - 5.0 Stop straight above, phone flat, plate, cup and fork in frame.
- Report the start and end camera positions, the measured plate fill and margins, and the contact sheet.

## Draft, Revision 1 (guide-animator, 2026-11-10)

- Same folder; render/ and export/ replaced, record.json updated. Export checks passed.
- Beats used (Revision 1, unchanged): 0.0 "Sit in front of the plate, phone tilted 45 degrees down." / 1.0 "Lift the
  phone slowly, tilting so the plate stays centred." / 5.0 "Stop straight above, phone flat, plate, cup and fork
  in frame."
- Camera: start (0, -0.341, 1.094), pitch 45, 0.45 m from the plate centre; end (0, -0.050, 1.466), pitch 90, no
  roll, lens 0.65 m above the plate rim. Crane-with-tilt over the full 6 s, eased; the plate centre stays at
  x 50% / 55% from the bottom on every frame.
- Layout (this guide only): table centred at (0, 0.40), chair at y 1.22, cup and saucer at (0.12, 0.236) (about one
  o'clock, handle right), fork straight at x -0.2015 (4 cm from the rim), centred on the plate's y.
