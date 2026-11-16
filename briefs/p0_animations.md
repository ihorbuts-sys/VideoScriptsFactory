# P0 animations and previews

The list to generate with the existing pipelines (`ScriptsAndGuides/guides/blender_motion/` for the Blender
renders, `guides/tools/` for the schematic fallback and the bundle, `previews/clay-3d/` for step pictures), with
the composition setup of every animation so the next agent knows which objects to build and where to put them.

Sections: 1 the 12 shot types, 2 shared rules, 3 the 28 animations (summary and one setup each), 4 previews and
selector files, 5 how to run.

## 1. The 12 shot types (proposed; the P0 doc does not list them)

Derived from the three scripts' steps and the trigger and preset examples in the P0 doc. Capture preset per
P0's Recorder table: moving shots `cinematicExtendedEnhanced` with continuous focus; static shots `standard`
with focus, exposure and white balance locked at record start; details lock the lens; 30 fps always.

| Shot type | Steps it serves | Camera | Trigger | Preset | Composition | Ambient | Guides |
|---|---|---|---|---|---|---|---|
| `entrance` | food-review.entrance, cafe.entrance, restaurant.entrance | back | motion | moving, continuous focus | center | noise | 3 |
| `menu-board` | cafe.counter (board), food-review.menu (board) | back | motion | moving, lens free | thirds | noise | 2 |
| `menu-card` | restaurant.menu, food-review.menu (card) | back | still | static, locked, lens locked | thirds | noise | 2 |
| `counter-order` | cafe.counter, food-review.menu (counter) | back (PiP optional) | still | static, locked | thirds | content | 2 |
| `plate-reveal` | food-review.dish, restaurant.plate | back | motion (tissue: countdown) | moving, lens locked | triangle | content | 3 |
| `hand-off` | food-review.dish (variant), cafe.drink (variant) | back | still | static, locked | center | content | 2 |
| `pour` | cafe.drink | back | still (upside-down: countdown) | static, locked, lens locked | center | content | 3 |
| `steam` | cafe.drink (cup on the table) | back | still (push-in, orbit: motion) | static or moving, lens locked | thirds | content | 3 |
| `first-bite` | food-review.bite, restaurant.forkful | front (both for the PiP variant) | still | static, locked | center | content | 2 |
| `sip` | cafe.sip | front | still | static, locked | center | content | 2 |
| `room-from-table` | restaurant.room | back | motion | moving, continuous focus | thirds | noise | 2 |
| `verdict` | all three verdict steps | front | still | static, locked | center | content | 2 |

28 guides in all: three for entrance, plate, pour and steam (the four types where the techniques differ most), two
for the rest. `cafe-before-opening` and every staff step are out; a custom step that maps to none of these gets
text only.

## 2. Rules shared by every animation

- **Frame**: 9:16, 405 x 720 at 15 fps, APNG with alpha, `alphaFactor: 1` (the app sets 65% before and 30% during
  recording). A second render at 120 x 213 for the selector sheet. No text, labels, arrows, phone glyphs or
  viewfinder in the artwork; the app draws the sight, the grid and the caption.
- **Clock**: frame 0 is the target frame, held 0.5 s; cut to the start of the move; the move lasts exactly
  `durationSec`; 0.5 s hold on the target. Props variants (tissue slide, upside-down) add a setup beat of 1.0 s
  before the move. No whip-out streaks, no push-through fill, no next-step object: the file ends on the target.
- **Objects present from frame 1; only the camera moves.** A pour, a hand or steam is an action inside the scene
  and keeps its real contact (stream into the cup, hand on the cup, feet on the floor). Light and lens are fixed.
- **Hero band**: the hero's contours stay inside the middle band (clear of the top 28% and bottom 22% of the
  frame, the kit's `check.py` rule) at the target frame; nothing important in the Loca safe zone the editor
  protects at export (bottom 35%, top 14%). A `triangle` step draws its three markers (faint, 6 px dots) at the
  triangle corners of the target frame.
- **Opacity hierarchy inside the file** (from `guides/cinematic_composition.md`): hero clearest, support
  subordinate, important background clearer than nearby decoration, foreground frame restrained, context
  faintest. Walls, floor and ceiling are absent unless one edge explains the framing.
- **Visitor side only**: no kitchen, pass, till or behind-the-counter camera position; staff hands may enter
  the frame from the far side of the counter. At most two visible hands in a frame.
- **Reach**: every camera position is a phone in a hand, flat on the table or on a napkin; distances and heights
  below assume that. Heights are above the support plane (table 0.75 m, counter 1.05 m, floor 0).
- **Fill**: the fraction is the hero's width over the frame width at the target: wide 0.55 to 0.75, medium 0.7 to
  1.0, close 0.95 to 1.6 (the scene builders' `FRAC`).
- **Previews** (section 4) are the step's own picture in the plasticine style and are separate from the guides.

## 3. The 28 animations

### Summary

| # | id | Title | Shot type | Technique | s | Trigger | Source scene | New objects |
|---|---|---|---|---|---|---|---|---|
| 1 | `entrance_walk_in` | Walk in through the door | entrance | push-in from across the street to the door | 5 | motion | `door_eye_in_wd_through` (drop the through tail) | none |
| 2 | `entrance_door_low` | Through the door at hip height | entrance | low POV walk-in into the room | 5 | motion | `pov_door_entry` (kit) | door with glass pane, two chairs |
| 3 | `entrance_sign_tilt` | Sign down to the door | entrance | hold on the sign, tilt down, two steps in | 5 | motion | `sign_tilt_down_reveal` (kit) + `facade` | hanging sign bracket |
| 4 | `menu_board_truck` | Slide along the board | menu-board | truck right at eye level | 4 | motion | `menu_board_eye_truckr_mm` | none |
| 5 | `menu_board_tilt_up` | Counter edge up to the board | menu-board | low start on the counter, tilt up to the board | 4 | motion | new | counter edge, board with three columns |
| 6 | `menu_card_top` | Menu flat on the table | menu-card | top-down hold | 4 | still | `card_menu_top_hold` | card with price rows |
| 7 | `menu_card_push` | Into the dish name | menu-card | high angle push-in to one line | 4 | motion | `card_menu_high_in_cd_whipout` (drop the whip) | none |
| 8 | `counter_over_shoulder` | Over your shoulder at the counter | counter-order | hold, board and counter in frame | 5 | still | `over_shoulder_counter_os_hold` (one phase, 5 s) | none |
| 9 | `counter_edge_to_pass` | Along the counter to the pass | counter-order | low truck along the counter edge ending on the pass | 5 | motion | new | counter with pass, espresso machine, takeaway cup |
| 10 | `plate_low_push_in` | Low push into the plate | plate-reveal | plate-height push-in | 4 | motion | `plate_low_in_cd_whipout` (drop the whip) | none |
| 11 | `plate_high_orbit` | Quarter orbit over the plate | plate-reveal | 45 degree orbit, 60 degrees of arc | 5 | motion | `plate_high_orbitl_cc` | none |
| 12 | `plate_tissue_slide` | Tissue slide to the plate | plate-reveal | phone flat on a napkin, slid across the table | 4 | countdown | new | napkin, phone-on-napkin setup beat |
| 13 | `handoff_counter_cup` | Cup handed over the counter | hand-off | hold; the cup arrives from the far side | 4 | still | new | hand with cup (far side), counter edge |
| 14 | `handoff_plate_lands` | Plate lands at your place | hand-off | hold from the seat; the plate enters and lands | 4 | still | new | hand carrying a plate, place setting |
| 15 | `pour_top_down_latte` | Latte art from above | pour | top-down, slight push-in during the pour | 5 | still | `latte_top_in_cd` | milk pitcher with stream, rosetta surface |
| 16 | `pour_side_low` | Pour at cup height | pour | low side hold, stream backlit | 5 | still | `glass_pour_low_in_cd` | pitcher and stream, window light cue |
| 17 | `pour_upside_down` | Upside-down at the counter | pour | phone held upside down, lens at counter level | 5 | countdown | new | counter edge, pitcher, stream |
| 18 | `steam_low_backlit` | Steam against the window | steam | low eye level hold, cup between camera and window | 4 | still | new | cup with steam strands, window |
| 19 | `steam_push_in_high` | Into the steam | steam | 45 degree push-in on the cup | 4 | motion | `cup_eye_hold_whipout` reversed (no whip) | steam strands |
| 20 | `steam_orbit_eye` | Around the cup | steam | eye-level 60 degree orbit | 5 | motion | `cup_eye_orbitr_cc` | steam strands |
| 21 | `bite_selfie_eye` | The bite at arm's length | first-bite | front camera hold, forkful rises | 5 | still | `selfie_bite_eye_in_mc` (silhouette) | bust silhouette, fork with forkful |
| 22 | `bite_pip_dish` | Dish behind, you in the corner | first-bite | back camera low on the dish, PiP window | 5 | still | new | plate, PiP window frame |
| 23 | `sip_selfie_eye` | First sip at eye level | sip | front camera hold, cup rises | 5 | still | `selfie_sip_eye_in_mc` (silhouette) | bust silhouette, cup |
| 24 | `sip_high_lean` | Cup up, lean in | sip | front camera from above, slow lean in | 5 | still | `selfie_sip_reaction` (kit, silhouette) | none |
| 25 | `room_reveal_cup` | Room from behind your cup | room-from-table | truck right from behind the cup | 5 | motion | `room_cupreveal_eye_reveal_dw` | none |
| 26 | `room_seated_pan` | Slow pan from your seat | room-from-table | pan right at seated height | 5 | motion | `interior_pan` (kit) | none |
| 27 | `verdict_eye_level` | Straight on, eyes level | verdict | front camera hold at eye level | 6 | still | `talking_head_eye_level` (kit, silhouette) | bust silhouette |
| 28 | `verdict_high_plate` | A little above, plate in frame | verdict | front camera from above, plate at the bottom | 6 | still | `selfie_one_high_hold` (silhouette) | bust silhouette, plate |

Durations are the guide's `durationSec` (the move only); file length = 0.5 + setup + s + 0.5.

Existing objects (Blender `blender_motion/assets.py`, `venue_assets.py`, `food_assets.py`, `real_hands.py`, and
the glTF library in `catalog/guide-objects.json`): table, dining_table, chair, plate (dinner_plate), serving_bowl,
cup, saucer, fork, pasta, pastry, burger, card, menu_board, door, facade, window, pendant, plant, daylight_patch,
lettering, studio_sign, bench, pastry_case, stemmed_glass, anatomical hands, portrait bust (deferred for people).
Objects to generate are listed per animation; "generate" means a new native model in the same style, not an
image.

### Setups

Placement convention: the hero sits at the origin on its support plane; x to the right as seen from the
customer side, z toward the camera. Camera: distance from the hero, height above the support plane, azimuth
(0 = customer side, positive = to the right), tilt from the project bands (top-down 85, high 45, eye-level 0, low
-12, POV 10, over-shoulder 20, selfie from above 30 degrees).

#### 1 `entrance_walk_in`, Walk in through the door

- **Target frame**: the door fills 0.7 of the frame width, centred, its top edge at 25% of the frame height, the
  threshold at 70%; the sign reads above the door inside the band. Symmetric: a centred doorway communicates
  the subject (composition `center`).
- **Objects**: hero door (existing `door`, closed glass pane, handle on the right); support: sign above the
  door (`studio_sign`), one lit pendant through the glass (`pendant`); background: facade edges left and right
  (`facade`, faint); foreground: none; light cue: a daylight patch on the pavement in front of the threshold
  (`daylight_patch`).
- **Placement**: door 0.9 x 2.1 m at the origin on the floor; sign 0.6 m wide, bottom 2.3 m; pendant 1.5 m behind
  the pane at 2.0 m; facade edges at x = -1.6 and +1.6 m.
- **Camera**: start 4.0 m from the door, height 1.4 m, azimuth 0, eye-level; target 1.2 m, height 1.4 m, same
  line. The move is a straight walk at an even pace over 5 s; the door grows from 0.3 to 0.7 of the width.
- **Filming guideline** (invariant caption): "Door centred, walk straight at it at an even pace." Tip for the
  card: hold the phone at chest height with both hands.
- **Render**: reuse the `door_eye_in_wd_through` scene; drop the through-fill tail; the target is the 1.2 m frame.

#### 2 `entrance_door_low`, Through the door at hip height

- **Target frame**: inside the room just past the threshold; the first two tables and chairs fill the middle band,
  the door frame edges leave the frame at the sides in the last 0.5 s of the move.
- **Objects**: hero: the room's first table with two chairs (`dining_table`, `chair` x 2); support: a second
  table behind (0.6 fainter); foreground: the door frame edges (`door` open 90 degrees, pane edge only, faint);
  background: window on the far wall (`window`), one pendant; light cue: daylight patch on the floor from the
  window.
- **Placement**: threshold at z = 1.5 m from the first table (origin); second table at z = -1.8 m, x = 1.0 m;
  window at z = -4 m; pendant above the first table at 2.0 m.
- **Camera**: start 1.0 m outside the threshold, height 1.0 m (hip), azimuth 0, POV tilt 10 degrees; target
  0.6 m inside, height 1.0 m, tilt 5 degrees. Walk 1.6 m over 5 s, slightly slowing at the end.
- **Filming guideline**: "Phone at hip height, lens forward, walk in without stopping." Tip: lock elbows to the
  body so the walk does not bounce.
- **Render**: adapt the kit `pov_door_entry` scene (it already has a storefront and a door) and add the room
  objects behind the door; the clip ends on the room, not on the door.

#### 3 `entrance_sign_tilt`, Sign down to the door

- **Target frame**: the door at 0.6 width, centred, threshold at 72%; the sign has just left the top of the frame.
- **Objects**: hero door (`door`); support: hanging sign on a bracket (generate: a 0.5 x 0.3 m board on an
  L-bracket, 0.3 m out from the wall) with `lettering` shapes, no readable text; background: facade edges;
  light cue: window glow on the pane (rim cue).
- **Placement**: door at the origin; sign bracket at height 2.6 m, x = 0.6 m; facade edges at x = -1.5 / +1.5 m.
- **Camera**: start 2.5 m from the door, height 1.4 m, tilt up 25 degrees on the sign (sign fills 0.5 width,
  centred); the first 1.5 s is the hold on the sign, then a tilt down to eye-level over 1.5 s, then two steps in
  (2.5 m to 1.8 m) over 2 s. Total 5 s. One continuous handheld move.
- **Filming guideline**: "Start on the sign, tilt down to the door, then two steps in." Tip: turn the wrist, not
  the arms, for the tilt.
- **Render**: the kit `sign_tilt_down_reveal` scene gives the sign and the tilt; append the two-step walk; no
  reveal tail.

#### 4 `menu_board_truck`, Slide along the board

- **Target frame**: the board's right third (the drinks column) fills 0.9 of the width; rows read as bars.
- **Objects**: hero: wall board 1.8 x 0.9 m, three columns of six rows (`menu_board`); support: the counter top
  edge along the bottom of the band at 68% (a 2 m line, faint); background: a shelf of cups behind the counter
  (three `cup` repeats, fainter); light cue: a spot pool on the board's right column (yellow, soft).
- **Placement**: board bottom at 1.5 m on the back wall (z = -1.2 m from the counter edge); counter edge at the
  origin; cups on a shelf at height 1.3 m, z = -1.1 m.
- **Camera**: 1.4 m from the board, height 1.6 m, azimuth 0, eye-level; truck right from x = -0.6 m to x = +0.6 m
  over 4 s at an even pace. The board's left column is the start, the right column the target.
- **Filming guideline**: "Phone level, slide sideways past the board at one even pace." Tip: step sideways, do not
  turn.
- **Render**: reuse `menu_board_eye_truckr_mm`; re-time to the P0 clock.

#### 5 `menu_board_tilt_up`, Counter edge up to the board

- **Target frame**: the board fills 0.85 of the width, its bottom edge at 60% of the frame; the counter top is a
  thin line at the bottom of the band.
- **Objects**: hero: the board (`menu_board`); support: counter edge with a card holder and one cup on it
  (`cup`); background: the shelf of cups; light cue: pendant above the counter (`pendant`), its pool on the
  counter top.
- **Placement**: as in 4; the cup at x = 0.4 m on the counter top.
- **Camera**: start 1.0 m from the counter edge, height 1.1 m (just above the counter), tilt -5 degrees on the
  cup and the counter edge (cup fills 0.35 width, right of centre); tilt up 35 degrees over 4 s to the board,
  no walking.
- **Filming guideline**: "Start on the counter, tilt up until the board fills the frame." Tip: rest the elbows on
  the counter edge.
- **Render**: new scene from the `menu_board` and `cup` assets; tilt only.

#### 6 `menu_card_top`, Menu flat on the table

- **Target frame**: the card fills 0.8 of the width, rotated 8 degrees, its top edge at 22%; the table edge is a
  faint diagonal; a cup corner enters at the top-right third (rule of thirds on the cup and the card's first
  row).
- **Objects**: hero: the menu card (`card`, A5, seven price rows as bars); support: a cup and saucer at the
  top-right corner (`cup`, `saucer`); foreground: none; background: the table edge (faint).
- **Placement**: card at the origin, long side along x, rotated 8 degrees; cup at x = 0.22 m, z = -0.18 m.
- **Camera**: 0.45 m above the card, top-down (85 degrees), centred on the card; a still hold, no move: the
  "move" window of 4 s is a hold in which the camera settles (a 2 cm drift at the start, then still).
- **Filming guideline**: "Straight above the menu, elbows on the table, hold still." Tip: tap the price line to
  focus.
- **Render**: reuse `card_menu_top_hold`; P0 clock; the poster is the held frame.

#### 7 `menu_card_push`, Into the dish name

- **Target frame**: one price row fills the width (close, 1.3), the row sits on the upper third line.
- **Objects**: hero: the card (`card`) with the target row 15% taller than the others; support: a fork beside
  the card (`fork`), the cup at the far corner; background: table edge.
- **Placement**: card at the origin; fork at x = -0.2 m parallel to the card; cup at x = 0.25 m, z = -0.2 m.
- **Camera**: start 0.6 m from the card centre, height 0.45 m, azimuth 0, high angle 45 degrees (card fills 0.7);
  push in to 0.25 m from the row, height 0.2 m, same angle, over 4 s with a slow stop.
- **Filming guideline**: "Move in slowly until the dish's line fills the screen, then stop." Tip: breathe out and
  stop; the auto-stop ends the take.
- **Render**: reuse `card_menu_high_in_cd_whipout` without the whip-out tail.

#### 8 `counter_over_shoulder`, Over your shoulder at the counter

- **Target frame**: the board upper-left on the thirds crossing, the counter edge as a diagonal from the lower-left
  to the middle-right, the pass with one cup on it at the right third; the creator's shoulder is not drawn.
- **Objects**: hero: the board and the pass cup together (`menu_board`, `cup` on the counter); support: the
  espresso machine behind the counter (check `cafe_first_visit.py` for the machine; otherwise generate: a
  0.7 x 0.45 x 0.5 m box with a group head and a steam wand); background: shelf of cups; light cue: pendant pool
  on the counter.
- **Placement**: counter edge along x at the origin; pass cup at x = 0.6 m, z = -0.3 m; machine at x = 0.9 m,
  z = -0.8 m; board on the back wall at z = -1.3 m, bottom at 1.5 m.
- **Camera**: 0.9 m from the counter edge, height 1.5 m, azimuth +25 degrees (over the right shoulder),
  over-shoulder tilt 20 degrees; a still hold of 5 s (the barista's hands may enter from the far side at second
  2 to place the cup: one hand, `real_hands`).
- **Filming guideline**: "Phone over your shoulder on the board and the counter, hold still while you order."
  Tip: the front camera PiP can record your face at the same time.
- **Render**: the existing `over_shoulder_counter_os_hold` has three phases (grinder, espresso, milk) over 7.2 s;
  keep only the cup-placed phase at 5 s.

#### 9 `counter_edge_to_pass`, Along the counter to the pass

- **Target frame**: the takeaway cup at the pass fills 0.9 of the width (medium), the counter edge runs out of
  the lower-left corner, the machine's side is a faint block behind.
- **Objects**: hero: the cup at the pass (`cup`, or generate a takeaway cup with a lid, 0.09 x 0.13 m);
  support: the counter edge (leading line) and a card holder; background: the espresso machine (as in 8); light
  cue: window light from the left on the cup's left edge (rim cue).
- **Placement**: counter edge along x; the cup at x = 0 (origin), 0.1 m in from the edge; machine at x = -0.3 m,
  z = -0.7 m; card holder at x = -0.8 m.
- **Camera**: start 1.3 m left of the cup (x = -1.3 m), 0.25 m out from the counter edge, height 1.2 m
  (counter + 0.15), azimuth +60 degrees looking along the edge, low tilt -5; truck right along the edge to
  x = -0.35 m, turning to azimuth +10 over 5 s. The counter edge leads to the cup; no staff side.
- **Filming guideline**: "Low over the counter, slide along its edge until your cup fills the frame." Tip: keep
  the phone just above counter height.
- **Render**: new scene; the bar truck in `bar_transition.py` is the nearest builder (one room, one camera, a low
  truck); no table lean at the end.

#### 10 `plate_low_push_in`, Low push into the plate

- **Target frame**: the plate's near rim at 75% of the frame height, the food filling 1.1 of the width (close),
  the far rim curving into the upper third; the triangle markers on the food's top, the near-left rim and the
  cup's base at the right.
- **Objects**: hero: a dinner plate with a tall dish (`dinner_plate` + `pasta`, or `burger` for fast-food);
  support: a cup and saucer right-behind (`cup`, `saucer`), a fork at the left edge (`fork`); background: a chair
  back across the table (`chair`, faint); light cue: side light from the left on the food (`fixed_side_light`).
- **Placement**: plate at the origin, food centred 0.08 m high; cup at x = 0.22 m, z = -0.15 m; fork at x =
  -0.17 m along z; chair at z = -0.9 m.
- **Camera**: start 0.55 m from the plate centre, height 0.12 m (plate height), azimuth 0, low tilt -12 (plate
  fills 0.6); push in to 0.22 m, height 0.10 m, same tilt, over 4 s, slowing into the stop.
- **Filming guideline**: "Phone at plate height, move in slowly until the dish fills the screen." Tip: rest the
  wrist on the table and slide it.
- **Render**: reuse `plate_low_in_cd_whipout` without the whip-out tail; add the triangle markers in frame 0.

#### 11 `plate_high_orbit`, Quarter orbit over the plate

- **Target frame**: the plate at 0.95 width, centred slightly left, the cup and the fork making the triangle's
  right and bottom corners; the plate's far rim at 30% height.
- **Objects**: as in 10, plus a second small plate (bread) at the top-left (`dinner_plate` scaled 0.6).
- **Placement**: plate at the origin; cup at x = 0.25 m, z = -0.1 m; small plate at x = -0.22 m, z = -0.22 m;
  fork at x = -0.16 m.
- **Camera**: 0.45 m from the plate centre, height 0.45 m (high angle 45 degrees), azimuth from -30 to +30
  degrees over 5 s at an even angular pace, always looking at the food's centre.
- **Filming guideline**: "Elbows on the table, circle the phone around the plate at one even pace." Tip: move the
  phone, not your body.
- **Render**: reuse `plate_high_orbitl_cc` (seven cross-faded poses over 60 degrees); P0 clock; markers.

#### 12 `plate_tissue_slide`, Tissue slide to the plate

- **Target frame**: the plate's near rim fills the bottom of the band, the food at 1.4 width (close), the far side
  of the table and the cup base soft behind; lens at table level (0.01 m).
- **Objects**: hero: the plate and food (as in 10); support: a folded napkin under the phone (generate: a 0.2 x
  0.2 m flat square, 4 mm thick, visible in the setup beat as a rectangle at the bottom edge, gone once the move
  starts), the cup; background: chair back; light cue: side light.
- **Placement**: plate at the origin; the phone starts 0.5 m from the plate's near rim on the napkin; cup at x =
  0.2 m, z = -0.15 m.
- **Camera**: height 0.01 m, tilt 0, azimuth 0; setup beat 1.0 s (the frame shows the napkin edge and the
  table surface, still); countdown trigger; slide straight toward the plate from 0.5 m to 0.12 m over 4 s at an
  even pace. The phone never lifts.
- **Filming guideline**: "Lay the phone flat on a napkin, lens toward the plate, and slide it straight in."
  Tip: pull the napkin, not the phone.
- **Render**: new scene; `countdown` trigger; `setupBeatSeconds: 1.0`; the preset locks focus at the start
  distance so the glide stays sharp (override on the guide record).

#### 13 `handoff_counter_cup`, Cup handed over the counter

- **Target frame**: the cup on its saucer at the centre of the band, 0.8 width (medium), the counter edge at 70%
  height, the hand that placed it already leaving at the top-right.
- **Objects**: hero: cup and saucer (`cup`, `saucer`); action: one hand from the far side (`real_hands`,
  entering top-right at second 1, placing the cup at second 2.5, leaving by second 3.5); support: the counter
  edge, a card holder; background: machine side (faint); light cue: pendant pool.
- **Placement**: counter edge along x at the origin; the cup lands at z = -0.15 m; the hand's path from (0.5,
  -0.6) to the cup.
- **Camera**: 0.6 m from the counter edge, height 1.35 m (counter + 0.3), azimuth 0, tilt -20 degrees on the
  landing spot; a still hold of 4 s, the still trigger fires on the steady frame before the hand arrives.
- **Filming guideline**: "Frame the empty spot on the counter, hold still, let the cup arrive." Tip: start the
  take before the barista calls your name.
- **Render**: new scene; the contact rule applies (hand on the cup handle, cup on the saucer).

#### 14 `handoff_plate_lands`, Plate lands at your place

- **Target frame**: the place setting (fork left, knife right, glass top-right) at 45 degrees with the plate
  landed at the centre, 0.9 width; the triangle: glass, fork tip, plate's near rim.
- **Objects**: hero: the plate with food; action: one hand carrying the plate from the top-left, lowering it over
  1.5 s, leaving by second 3; support: fork, knife (generate: a knife matching `fork`, blade toward the plate),
  water glass (`stemmed_glass` or generate a tumbler); background: the far chair.
- **Placement**: plate lands at the origin; fork at x = -0.17 m, knife at x = +0.17 m, glass at x = 0.2 m, z =
  -0.25 m; the hand's path from (-0.4, -0.5, 0.3 m high).
- **Camera**: 0.5 m from the plate, height 0.45 m, azimuth 0, high angle 45; still hold of 4 s.
- **Filming guideline**: "Frame your place setting from your seat and hold still while the plate arrives." Tip:
  elbows on the table.
- **Render**: new scene; the owner's table rule (plate at a usable place setting, cutlery oriented from the
  diner's view) is enforced by `table_composition.py`.

#### 15 `pour_top_down_latte`, Latte art from above

- **Target frame**: the cup fills 1.2 of the width (close), centred, the rosetta's stem pointing at the viewer;
  the saucer rim leaves the frame; the pitcher spout at the top edge of the band at the end.
- **Objects**: hero: the cup with crema (`cup`, 0.09 m); action: the milk pitcher (generate: 0.35 l pitcher
  with a spout) tilting from 45 to 70 degrees, a stream into the cup, the rosetta surface drawn on over 3 s
  (generate: a flat rosetta mask on the crema); support: saucer; background: counter top edge; light cue: the
  counter spot on the crema.
- **Placement**: cup at the origin on the counter; pitcher spout at height 0.1 m, from x = -0.05 m; the stream
  lands at the cup's centre and moves back 0.03 m as the rosetta grows.
- **Camera**: start 0.4 m above the cup, top-down 85, centred; a slow push to 0.3 m over 5 s while the still
  trigger starts the take on the steady frame; the pour runs from second 0.5 to 4.
- **Filming guideline**: "Straight above the cup, hold still, lean in slowly as the milk goes in." Tip: ask the
  barista to pour toward you.
- **Render**: reuse `latte_top_in_cd`; add the pitcher and the stream as scene action; no whip tail.

#### 16 `pour_side_low`, Pour at cup height

- **Target frame**: the cup at the right third, 0.7 width, the stream a bright line from the top-left into it,
  the window behind as a soft rectangle; the counter top at 72%.
- **Objects**: hero: the cup; action: pitcher and stream (as in 15) from the top-left; support: the saucer;
  background: window (`window`) 1.5 m behind; light cue: rim highlight on the stream and on the cup's left edge
  (backlight explains the choice).
- **Placement**: cup at the origin; window at z = -1.5 m, sill at 1.0 m; the pitcher spout at (-0.1, 0.12 m).
- **Camera**: 0.35 m from the cup, height 0.08 m above the counter, azimuth -20, tilt 0; still hold of 5 s; the
  pour from second 0.5 to 4.
- **Filming guideline**: "Phone at cup height with the window behind the cup, hold still through the pour."
  Tip: rest the phone's bottom edge on the counter.
- **Render**: adapt `glass_pour_low_in_cd` (a low pour into a glass) to the cup, without the push-in; still.

#### 17 `pour_upside_down`, Upside-down at the counter

- **Target frame**: as in 16 but the lens is 0.01 m above the counter (the phone is held upside down, lens at
  the bottom); the counter surface is the bottom 20% as a reflection band, the cup at the centre, 0.9 width.
- **Objects**: as in 16 plus a faint reflection of the cup in the counter (`reflection`).
- **Placement**: as in 16; the camera at height 0.01 m.
- **Camera**: 0.3 m from the cup, height 0.01 m, azimuth -15, tilt +5 degrees (looking slightly up at the
  cup); setup beat 1.0 s (the frame settles after the flip), countdown, then a still hold of 5 s with the pour
  from second 0.5.
- **Filming guideline**: "Turn the phone upside down so the lens sits on the counter, then hold still."
  Tip: the picture is corrected for you; do not rotate it.
- **Render**: new scene; the recorder marks the clip's rotation for the editor (task 02 bakes it);
  `setupBeatSeconds: 1.0`, `countdown`.

#### 18 `steam_low_backlit`, Steam against the window

- **Target frame**: the cup at the left third, 0.6 width, three steam strands rising to the upper third against
  the window's bright rectangle; a saucer and a spoon at the bottom of the band.
- **Objects**: hero: the cup with steam (generate: three curved strands, 0.12 m high, drifting 2 cm over the
  hold, drawn as faint lines with a yellow rim); support: saucer, spoon (generate: a 0.14 m spoon); background:
  window; light cue: window backlight rim on the strands.
- **Placement**: cup at the origin; spoon at x = 0.12 m on the saucer; window at z = -1.2 m.
- **Camera**: 0.4 m from the cup, height 0.06 m above the table, azimuth +15, tilt 0; a still hold of 4 s.
- **Filming guideline**: "Put the window behind the cup, phone at cup height, hold still." Tip: steam shows only
  against something bright.
- **Render**: new scene; the steam is drawn on from frame 1 (not animated in), only its drift moves.

#### 19 `steam_push_in_high`, Into the steam

- **Target frame**: the cup's mouth fills 1.2 of the width (close), seen from 45 degrees, the steam strands
  leaving the top of the band; the triangle: the handle, the near rim, the strand tip.
- **Objects**: hero: the cup with steam; support: saucer, a pastry on a small plate at the top-right (`pastry`,
  `dinner_plate` scaled 0.6); background: the table edge; light cue: side light.
- **Placement**: cup at the origin; pastry plate at x = 0.2 m, z = -0.2 m.
- **Camera**: start 0.5 m from the cup, height 0.4 m, azimuth 0, high 45 (cup fills 0.5); push in to 0.2 m,
  height 0.17 m, over 4 s, slowing into the stop.
- **Filming guideline**: "From above at an angle, move in slowly until the cup's rim fills the frame." Tip: stop
  before the steam touches the lens.
- **Render**: reverse the `cup_eye_hold_whipout` scene (it dollies out) into a push-in at 45 degrees; no whip.

#### 20 `steam_orbit_eye`, Around the cup

- **Target frame**: the cup at 0.9 width at eye level with the handle turned to the right, steam above it, the
  saucer rim as the bottom line of the band.
- **Objects**: hero: cup with steam; support: saucer; background: a chair back (faint); light cue: side light
  from the left, so the orbit reveals the lit and the shadow side.
- **Placement**: cup at the origin, handle at azimuth +90 at the start.
- **Camera**: 0.3 m from the cup, height 0.08 m, tilt 0; azimuth from -30 to +30 over 5 s; the handle comes
  round into view.
- **Filming guideline**: "Phone level with the cup, circle slowly until the handle comes into view." Tip: keep the
  distance constant.
- **Render**: reuse `cup_eye_orbitr_cc` (kit cup, seven poses); add the steam strands.

#### 21 `bite_selfie_eye`, The bite at arm's length

- **Target frame**: a head-and-shoulders silhouette centred (the project's face target is centred), the eyes at
  45% of the frame height, the fork with the forkful rising from the lower-right third to the mouth level over
  the hold; the table and the plate as a faint line at the bottom of the band.
- **Objects**: hero: bust silhouette (no face, no hair detail; generate from the `portrait` bust as a filled
  outline, pending the owner's people decision); action: a fork with a forkful (`fork` + a pasta tuft) rising
  0.2 m over 2 s; support: the plate's rim at the bottom edge; background: none.
- **Placement**: the bust 0.65 m from the lens (the `PERSON_DISTANCE` front medium), shoulders at 60% height;
  the fork from (0.15, -0.2) to (0.05, 0.0) relative to the mouth.
- **Camera**: front camera, 0.65 m, height at eye level, tilt 0; still hold 5 s; the fork rises from second
  1 to 3; mirrored like the preview.
- **Filming guideline**: "Front camera at arm's length, eyes level, lift the first bite to the lens." Tip: the
  back camera can film the plate in the small window.
- **Render**: adapt `selfie_bite_eye_in_mc` without the push-in; silhouette only.

#### 22 `bite_pip_dish`, Dish behind, you in the corner

- **Target frame**: back camera on the plate as in 10 at 1.0 width (medium-close), and a PiP window outline
  (0.3 x 0.3 of the frame) at the top-right corner inside the band where the front camera shows the face; the
  fork enters the plate from the bottom-right and lifts.
- **Objects**: hero: the plate with food; action: the fork lifting a forkful from the plate (one hand,
  `real_hands`, at the bottom-right); support: the cup; the PiP window outline (faint rectangle, the only UI-like
  shape allowed because the app draws nothing there); background: chair back.
- **Placement**: plate at the origin; fork hand from (0.25, 0.3, 0.15 m high) to the plate's centre.
- **Camera**: back camera 0.4 m from the plate, height 0.2 m, azimuth 0, low tilt -10; still hold 5 s; `camera:
  both`.
- **Filming guideline**: "Back camera on the dish, your face in the small window, lift the bite toward you."
  Tip: look at the lens, not at the screen.
- **Render**: new scene; `camera: both`; the preset's multicam rules apply (1080p30 both streams).

#### 23 `sip_selfie_eye`, First sip at eye level

- **Target frame**: as in 21 with the cup rising from the lower-left third to the mouth level; the cup at 0.3
  width.
- **Objects**: bust silhouette; action: the cup with saucer-less grip (`cup`, one hand) rising 0.2 m over 2 s;
  background: none.
- **Placement**: bust at 0.65 m; the cup from (-0.15, -0.2) to (-0.03, 0.0) relative to the mouth.
- **Camera**: front, 0.65 m, eye level, tilt 0; still hold 5 s.
- **Filming guideline**: "Front camera at arm's length, lift the cup, sip, react to the lens." Tip: hold the cup by
  the body, not the handle, so it does not hide your face.
- **Render**: adapt `selfie_sip_eye_in_mc` without the push-in; silhouette.

#### 24 `sip_high_lean`, Cup up, lean in

- **Target frame**: the silhouette from 30 degrees above, the eyes at 40% height, the cup at the mouth filling
  0.35 width, the table's edge and the saucer at the bottom of the band (the plate-and-face triangle: eyes,
  cup, saucer).
- **Objects**: bust silhouette; action: cup rising; support: saucer on the table; background: none.
- **Placement**: bust at 0.6 m, the camera 0.25 m above the eye line; saucer at the table 0.4 m in front of the
  bust.
- **Camera**: front, selfie-from-above tilt 30; the 5 s window: 1 s settle, then a slow lean in from 0.6 m to
  0.5 m over 3 s, 1 s hold; still trigger on the settle.
- **Filming guideline**: "Phone a little above your eyes, cup up, lean in slowly as you sip." Tip: keep the
  saucer in the bottom of the frame.
- **Render**: adapt the kit `selfie_sip_reaction`; silhouette.

#### 25 `room_reveal_cup`, Room from behind your cup

- **Target frame**: the room's tables and the window at the thirds: the window top-left, the far tables along the
  middle line, the near table edge at the bottom of the band; the cup has slid out of the frame to the left.
- **Objects**: hero: the room (two `dining_table` + `chair` groups, a `window`, a `pendant`); foreground: the
  creator's cup (`cup`, blocker at 0.68 width at the start, leaving left); support: the near table edge; light
  cue: daylight patch from the window on the floor.
- **Placement**: cup at the origin on the near table; tables at z = -2.5 m (x = -0.8) and z = -3.5 m (x = +1.0);
  window at z = -5 m, x = -1.2 m; pendant above the first far table.
- **Camera**: seated height 1.1 m (table + 0.35), 0.12 m behind the cup at the start, azimuth 0, tilt 0; truck
  right 0.35 m over 5 s at an even pace, keeping the tilt; the cup leaves by second 2.
- **Filming guideline**: "Start with the lens right behind your cup, slide sideways until the room shows." Tip:
  keep the phone level; the horizon warning checks 5 degrees.
- **Render**: reuse `room_cupreveal_eye_reveal_dw`; P0 clock.

#### 26 `room_seated_pan`, Slow pan from your seat

- **Target frame**: the far wall's window at the right third, the bar or counter at the left third, the tables'
  tops as a horizontal rhythm along the middle line.
- **Objects**: hero: the room (three table groups, the counter block from `venue`, the window); support: the
  pendants (three, rhythm); foreground: the near table's edge and the creator's cup at the bottom-left (faint);
  light cue: window daylight patch.
- **Placement**: the near table at the origin; tables at z = -2, -3.5, -5 m staggered in x; counter along x = -2.5
  m; window at z = -6 m, x = +1.5 m.
- **Camera**: seated, height 1.1 m, at the near table's edge; pan right 50 degrees over 5 s at an even angular
  pace, tilt 0 throughout; no walking.
- **Filming guideline**: "Sit still, turn the phone slowly across the room, level all the way." Tip: turn from the
  hips, not the wrists.
- **Render**: adapt the kit `interior_pan` to seated height; P0 clock.

#### 27 `verdict_eye_level`, Straight on, eyes level

- **Target frame**: the silhouette centred, eyes at 42% height, shoulders at the bottom of the band, the room's
  pendant and a table edge as faint context behind; nothing in the bottom 35% but the shoulders.
- **Objects**: bust silhouette; background: one pendant and the far table edge (faint); no action.
- **Placement**: bust at 0.65 m; pendant 2.5 m behind at 2.0 m high, x = +0.6 m.
- **Camera**: front, 0.65 m, eye level, tilt 0; still hold 6 s.
- **Filming guideline**: "Front camera at arm's length, eyes level, say the price and the street." Tip: the
  prompter scrolls with you.
- **Render**: adapt the kit `talking_head_eye_level`; silhouette; 6 s.

#### 28 `verdict_high_plate`, A little above, plate in frame

- **Target frame**: the silhouette from 30 degrees above, eyes at 38% height, the plate (or the cup) at the
  bottom-right of the band at 0.35 width, the table edge as a diagonal; the triangle: eyes, plate, the far
  shoulder.
- **Objects**: bust silhouette; support: the plate with the remains of the dish (`dinner_plate`, `pasta` half)
  or the cup for the cafe script; background: chair back; no action.
- **Placement**: bust at 0.6 m; the plate on the table 0.35 m in front of the bust, x = +0.2 m.
- **Camera**: front, selfie-from-above 30, 0.6 m; still hold 6 s.
- **Filming guideline**: "Phone a little above your eyes with the plate in the frame, give the verdict." Tip:
  tilt the phone down a touch so the plate stays in.
- **Render**: adapt `selfie_one_high_hold`; silhouette; the cafe variant swaps the plate for the cup (one id,
  two subject variants, as the catalog already does for `selfie_one_high_hold`).

## 4. Previews and selector files

Step previews (1080 x 1920 plasticine, `previews/clay-3d/`): the three scripts have 16 steps. Existing pictures
cover the 10 steps of `food-review` and `cafe-first-visit` (re-check them for the P0 rule "customer-side
composition": the pour picture must be from the customer side of the counter). New:

| # | Preview file | Title | Note |
|---|---|---|---|
| 1 | `restaurant-first-visit_entrance.jpg` | Arrive | the door from across the street, evening light |
| 2 | `restaurant-first-visit_menu.jpg` | The menu | card on the table, 45 degrees, cup at the corner |
| 3 | `restaurant-first-visit_plate.jpg` | The plate arrives | place setting from the seat, a plate being set down |
| 4 | `restaurant-first-visit_forkful.jpg` | First forkful | front camera framing, fork rising |
| 5 | `restaurant-first-visit_room.jpg` | The room from the table | seated view across the tables to the window |
| 6 | `restaurant-first-visit_verdict.jpg` | Verdict | from a little above, plate in frame |
| 7 | `food-review_dish_handoff.jpg` | The dish, handed over | the hand-off variant's example (used by the hand-off guides' card) |
| 8 | `cafe-first-visit_drink_handoff.jpg` | Your drink, handed over | the cup arriving over the counter |

Selector files, derived from the animations, not illustrated: 28 x `<id>_selector.png` (120 x 213 APNG loop) and
28 x `<id>_poster.png` (frame 0 at 405 x 720).

## 5. How to run

> Superseded (2026-11-10): the commands that ran are in `catalog/p0/RUNBOOK.md`; 37 guides now, the rigged creator, bottom band 35%.

1. **Scenes**: add the 28 ids to `guides/blender_motion/scene_plans.py` with the setups above (hero, support,
   background, foreground, light cue, camera start and target, action timing); the source scenes named in the
   summary are the starting projects (`render_saved_scene.py` reads them without modifying them). New objects
   go into `assets.py` / `venue_assets.py` / `food_assets.py` with a footprint, a placement anchor and metres.
2. **Clock**: add a `p0` export mode to `export_shot.py`: 0.5 s target hold, cut, the move over `durationSec`,
   0.5 s hold, optional `setupBeatSeconds`; no hand-over tail; `alphaFactor: 1` (skip `api/opacity_assets.py`);
   write `<id>.png`, `<id>_selector.png` (120 x 213), `<id>_poster.png` into `guides/p0/renders/` (the bundle reads
   them there; a guide without all three is listed in `shot_types.json` `pendingRenders`).
3. **Checks**: `verify_rollout.py` for people count (zero, or silhouettes once allowed), hand count (two at most),
   reach and travel, fixed light; `guides/tools/build_guides.py check` for the kit band rule; the frame-0 equals
   poster rule and the duration rule from task 03 section 5.
4. **Schematic fallback**: the same 28 setups can be built with `guides/tools/scenes.py` builders (`door`, `menu`,
   `card`, `plate`, `cup`, `latte`, `glass`, `selfie`, `room`, `table`, `over_shoulder`, `hands`) for a line-art
   variant; `catalog.py` gets a `P0` table mapping id to family, item and signature.
5. **Previews**: the eight pictures through the `step-previews` skill with `previews/clay-3d/style-v2.md`, visitor
   side, two hands at most; register them in `manifest.json` and `active-art-revision.json`.
6. **Bundle**: `guides/tools/build_bundle.py --profile p0 --out
   /Users/ihor.buts/Documents/Development/Scriptwriter/catalog` (task 03), then `api/check_api.py`.
