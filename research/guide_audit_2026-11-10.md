# Guide audit against the reference-shot research (2026-11-10)

Read-only audit of the 37 published P0 guides (`catalog/p0/animations-light/*`) against
`research/reference_shots/food_and_drink.md` (RA), `venue_and_people.md` (RB), `skills/script-composer/references/shot_library.md`
and `skills/guide-animator/references/framing.md`. Nothing was edited or rendered. "(judgement)" marks a reason no
reference states.

## 1. Method and what was measured

- Script: `measure.py`, run once per guide in Blender 5.2.3 background mode, one process at a time
  (`Blender -b <id>/scene.blend -P measure.py -- <out.json>`). Output: one JSON per guide plus
  `measurements_all.json`, in `/private/tmp/claude-501/-Users-ihor-buts-Documents-Development-Loca/2d99ee53-6048-43a7-b97a-41db55ac1f7c/scratchpad/guide_audit/`
  (folder `m/` holds the per-guide files).
- Clock: from `meta.json` (frame_count, target_hold_frames 8, final_hold_frames 7, setup_frames). Frame 1 is the
  target. The move window is frame 9 to the last frame. The jump from frame 8 (target) to frame 9 (start pose) is left out of
  speeds. Move start and end are the first and last frames where the camera position or view direction changes.
  Speeds are frame-to-frame differences at 15 fps. Peak means the largest single step. Mean is path length divided
  by move duration.
- Camera "Visitor phone": world position, pitch (degrees below horizontal, negative = looking up), roll, yaw. Angular
  speed is the angle between successive view directions. Orbit arc is the change in the camera's azimuth around the
  hero centre. Lens: every guide has a fixed lens (no zoom animation). Rear guides use 24 mm with a 36 mm vertical
  sensor fit, so 45.7 deg horizontal in 9:16 (matches the 1x 44-47 deg in RB 0.2). The four front-camera guides use
  18 mm, so 58.7 deg horizontal.
- Hero: meshes with `composition_role` = hero. People guides have no hero role, so the hero is the creator's
  skin contour inside the face safety mask. Eye position comes from the mask's eye and brow contours. Fill is the
  hero's projected vertex extent at the target frame, as a fraction of frame width. Centre is the extent centre,
  measured from the top. "Group fill" is the hero's parent group (for example the whole plate with pasta) where the
  hero part is small.
- Support surface: meshes named tabletop, counter top or shelf (slab under 12 cm thick, at least 25 x 20 cm). The
  height under the hero is the highest top below it. The height under the lens is the top under the lens, or the
  nearest top within 60 cm when the lens is past an edge. Otherwise it is the floor (z 0). Surfaces used: `Quiet tabletop`
  (top 0.785 m), `Customer counter top` (1.05 m), `Long commercial dining tabletop` (0.785 m), the floor for
  entrance, board and people guides.
- Portrait feasibility (measured, not estimated): per frame, a segment from the lens down the phone's up axis for
  13.2 cm (iPhone about 14.7 cm long, rear lens about 1.5 cm below the top edge, judgement). Portrait is impossible on a
  frame where that segment enters a surface slab under the lens (phone body inside the table). This separates "lens
  low but held past the edge", which is possible in portrait, from "lens low over the table", which needs upside
  down. The research threshold of about 10-12 cm (framing.md, RA 11, RB 0.3) applies to the second case only.
- Not measured: blocker-to-lens distance for reveals, light direction and hand timing.

Cross-cutting findings that the table does not repeat:
- Hero centre at the target sits at 47-56% from the top in almost every guide. The research clear-box centre is about 40-45%
  [RA2] (placement judgement). Everything is inside the STYLE 28%/35% band, so this is a re-framing note, not a
  verdict driver.
- Every people guide puts the eyes at 46-47% from the top (verdict_high_plate: 41%). The target is 33% [RB15].
- The creator rig stands (eyes at 1.52 m, 73 cm above the table). Seated eye height is 110-120 cm (judgement in RB D). Seated people
  guides would need a seated pose.
- No guide exceeds the STYLE camera-speed cap of 1.3 m/s. The fastest peak is entrance_walk_in at 1.06 m/s.

## 2. Per-guide verdicts

Columns: H = lens height above the named surface (start->end). P = pitch start->end. D = distance to the hero centre.
v = mean/peak speed. w = mean/peak angular speed. t = move duration. fill = hero width fraction at the target, centre
from the top. Used by = GUIDE_INDEX steps.

| Guide | Shot type | Level | Used by | Measured | Research target | Verdict | Reasons |
|---|---|---|---|---|---|---|---|
| entrance_walk_in | entrance | easy | first-visit.entrance, food-review.arrive, food-review-handheld.window | H 1.40 m (floor); P 2->3 down; D 7.85->5.05 m to the door; path 2.80 m; v 0.57/1.06 m/s; t 4.9 s; door fill 0.27, centre 0.50 | A2: start 3-5 m out, walk 0.5-0.8 m/s constant for 3-5 s, chest or eye height, 0 deg, cut as the door fills the frame | adjust (distance, speed) | Starts 7.9 m out and ends 5 m short of the door. The door never fills the frame [RB31]. The peak of 1.06 m/s comes from easing, and the research wants a constant pace [RB25 3:25][RB23] (speed judgement). Start at 4 m, end at about 1.2 m, constant 0.6 m/s. |
| entrance_door_low | entrance | easy | same 3 steps | H 1.00 m (hip); P 3->6 down; walks from 1.0 m outside the threshold to 0.6 m inside; path 1.60 m; v 0.32/0.61 m/s; t 4.9 s; door behind the lens at the target | none at hip height: A2 is chest or eye height, A3 is 2-5 cm (upside down), and the portrait alternative is knee height tilted 10-15 down | redo: A4, a friend films static while you walk in (easy, no guide yet) | Hip height is not a referenced variant [RB25][RB37]. Walking through the door is the A2 push-through, which ranks 4th and adds door handling and an exposure jump [RB31][RB35 1:03]. The guide is levelled easy, which conflicts with that. It ends inside, not "cut before opening" (judgement). |
| entrance_sign_tilt | entrance | easy | same 3 steps | H 1.65->1.20 m (lowers 45 cm); P 37.7 up->3.3 down (41 deg); D 1.4-1.5 m from the door; w 8.3/16.3 deg/s; t 4.9 s; door group fill 1.03, handle at x 0.83-0.87 | A1: standing still at chest height about 1.30 m, 20-30 deg up -> 0 deg, 4-8 m from the facade at 1x, 3-4 s, about 8 deg/s | adjust (distance, height, speed) | Too close: the door overfills the frame and the handle sits in the right rail [RB3]. A1 is "standing still, one hinge of the elbows", with no 45 cm drop [RB25 4:21]. Tilt 41 deg vs 20-30 deg. Peak 16 deg/s vs about 8 deg/s. The record itself asked for 2.5 m. |
| menu_board_truck | menu-board | easy | food-review.order | H 1.85 m (0.80 above the counter top); P 0; D 1.98->1.62 m; path 1.14 m; v 0.29 m/s constant; t 3.9 s; column fill 0.33, board 1.31 | B2: truck 10-15 cm/s for 3-4 s (30-60 cm), lens at the board centre height, about 1.5 m back at 1x | adjust (speed, height) | 2-3x the truck speed [RB25 5:58] (speed judgement). 1.85 m is above a standing adult's eye line. Use at most 1.6 m and step back so the pitch is at most 10 deg up [RB51] (reach judgement). The distance is within range. |
| menu_board_tilt_up | menu-board | easy | food-review.order | H 1.13 m (floor), fixed; P 0.6 down->18.1 up, plus a 22.8 deg yaw (28.5 deg total); w 7.8/15.4 deg/s; t 3.7 s; D 2.29 m at 1x; board fill 0.84 (x 0.08-0.92) | B3: tilt 20-30 deg in 3 s between the board and the case; end pitch at most 10 deg up; 2-3 m at 2x or 1.5 m at 1x | adjust (height or distance, speed, framing) | Ends 18 deg up, which gives keystone [RB51]. Raise the lens to about 1.5 m or step back. A pure tilt with no pan [RB23 wrist pan as a mistake]. Peak at most 10 deg/s (judgement). The board runs past the 85% right edge [RB3]. Use 2x at 2-3 m [RB33]. The direction is the reverse of B3 (acceptable mirror, judgement). |
| menu_card_top | menu-card | easy | first-visit.menu | H 0.46 m above the table; P 71.9->85.6; D 0.47->0.45 m; path 0.15 m with a 55 deg swing around the card; v 0.04/0.06 m/s; t 3.9 s; fill 0.60, centre 0.50 | menu-card 1: static overhead at 90 deg with the cup in frame (25-35 cm, 1x) | adjust (pitch, make static) | The research variant is a still overhead [RA4][RA8]. The scene swings 55 deg and settles from 72 deg, which contradicts the record's "still hold". Keep the distance: at 25-35 cm on 1x the 23 cm card rows alone fill 78-100% of the width, so the card plus cup does not fit (judgement from the measured FOV). |
| menu_card_push | menu-card | easy | first-visit.menu | H 0.42->0.20 m; P 36 deg; D 0.70->0.33 m; path 0.38 m; v 0.10/0.18 m/s; t 3.9 s; row fill 0.64 | none: flat card overhead; variants are static overhead, hand opens the menu, 15 cm overhead rise | redo: menu-card 2, a hand opens the menu with the phone still (easy, no guide yet), or 3, an overhead rise of 15 cm in 3 s | A 36 deg diagonal push over a flat card is not referenced. Flat objects read overhead [RA4], and a tilted phone over a flat card is a named mistake [RA5]. The peak of 18 cm/s is above the 5-7 cm/s table push (RA21, judgement). |
| counter_over_shoulder | counter-order | easy | first-visit.counter, food-review-drink.order | H 1.45 m (floor); P 1.8 up; D 3.90->3.64 m to the board; path 0.47 m (slide plus push); v 0.10/0.18 m/s; t 4.9 s; fill 0.51; no shoulder object in the scene | C2: a friend's lens at your shoulder height, pitch 0-10 down, static or a push of 20-30 cm in 3-5 s; the near shoulder fills 25-35% | adjust (speed, pitch, framing) | Path 47 cm vs 20-30 cm. Peak 18 cm/s (judgement: at most 8). Pitch up vs 0-10 down [RB40]. With no foreground shoulder it is not an OTS shot. Add the near shoulder [RB40][RB15] or rename it a standing slide (judgement). |
| counter_edge_to_pass | counter-order | easy | first-visit.counter, food-review-drink.order | H 0.15 m above the counter top, held 40 cm in front of its edge (portrait possible, measured); P 3.6->7.7 down; D 1.45->0.69 m; path 0.95 m plus a 35 deg turn; v 0.19/0.36 m/s; w 7/15 deg/s; t 4.9 s; cup fill 0.24 | C3 portrait alternative: 15 cm above the counter, pitched 15-20 deg down, truck 5-10 cm/s for 3 s | adjust (speed, pitch, distance) | Orientation check closed: portrait works. The speed is 2-4x the 5-10 cm/s skim (judgement in RB C). Drop the 35 deg turn, since one move per guide is the rule (judgement). Pitch 15-20 down [RB 0.3]. End 40-60 cm from the cup so it is not 0.24 wide (judgement). |
| counter_through_cup_handle | counter-order | complex | none | lens 2-3 cm below the counter top level, 9 cm in front of the edge (portrait possible, phone hangs past the edge); P 19.5 up; D 0.32->0.26 m to the handle; path 0.07 m; t 5.7 s | none | redo: C1, a POV hand receives the cup (static, chest height, 20-30 deg down, 40-60 cm, cut on the grab) | Through-the-handle framing is not referenced. The beat "frame the barista" puts staff at the centre, while the research says film hands and cups, not staff faces [RB41][RB42]. C1 is the easiest counter variant [RB32][F19]. |
| plate_low_push_in | plate-reveal | easy | none | H 0.20->0.12 m above the table, lens 21 cm inside the edge; portrait blocked in the last 25 frames (phone 1.1 cm into the table); P 11.6; D 0.69->0.31 m; path 0.38 m; v 0.10/0.18 m/s; t 3.9 s; pasta fill 0.62, plate 1.25 | plate 3, 3/4 push-in: 45 deg down, 45-50 -> 25-30 cm, 20 cm in 3-4 s (5-7 cm/s), elbows on the table | adjust (pitch, height, distance, speed) | 12 deg is outside the 25-75 range [RA4]. The end pose is about 1 cm too low for portrait (borderline, and it clears once raised). Path 38 cm vs 20 cm and peak 18 cm/s vs 5-7 [RA21][RA17]. The plate overfills the frame at the end. |
| plate_high_orbit | plate-reveal | complex | first-visit.plate, food-review.dish, food-review-sweet.break, food-review-handheld.cut | H 0.45 m; P 42 constant; slant D 0.60 m (horizontal 0.45 m) constant; arc 60.8 deg in 4.9 s (12.3 deg/s around the plate); v 0.10 m/s constant; pasta fill 0.32, plate 0.59 | plate 5, orbit: pitch 30-45, radius 30-40 cm constant, 30-45 deg of arc in 4 s | adjust (distance, arc) | Pitch, constant radius and even pace all match [RA15][RA16][RA17]. The radius is 60 cm vs 30-40 cm, and the arc is 60 deg vs 30-45 deg (judgement values in RA 2c). Use 0.38 m and 40 deg. |
| plate_tissue_slide | plate-reveal | complex | same 4 steps | H 0.075 m above the table, lens 22 cm inside the edge; portrait blocked on every frame (phone 5.6 cm into the table); P 5; D 0.33->0.30 m; path 0.18 m plus a 32 deg turn; w 8.5/15.9 deg/s; t 3.8 s after a 1 s setup | 2d slide: upside down when the phone rests on the table; portrait alternative: top edge 3-5 cm above the table, slight down pitch | orientation | Lens 7.5 cm over the table, which is not possible in portrait [RA 1.2][RA 11]. Portrait alternative 1: plate 2, the napkin pull, with the phone still in portrait at 45 deg while a hand pulls the napkin away. It ranks 2nd easiest [RA 2e] and is the first-timer rule. Alternative 2: hold portrait at the near table edge with the top edge 3-5 cm above the table [RA 2d]. The 32 deg turn also contradicts its own "straight slide" record. |
| table_spread_orbit | plate-reveal | complex | food-review-table.spread | H 0.81->1.24 m above the table (2.02 m above the floor at the end); P 48.6->90; roll up to 33 deg; D 0.95->1.22 m; path 0.80 m; v 0.10/0.19 m/s; t 7.8 s; pizza fill 0.29 | plate 4, overhead rise: 90 deg the whole way, 25-30 -> 45-60 cm, 3-4 s, standing | redo: plate 4, the overhead pedestal rise at 90 deg throughout (the pending plate_rise_overhead, re-specified), or a static 3/4 at 45 deg | A tilt from 3/4 into overhead with a 33 deg roll is not referenced. RA 2a keeps 90 deg, and a tilted phone over a flat lay is a mistake [RA5]. A lens 2.0 m above the floor is out of reach over a table (judgement). 7.8 s vs 3-4 s. Note: the pending plate_rise_overhead is specced as "the table_spread_orbit move", so fix the spec before it is animated. |
| glass_slide_close | plate-reveal | complex | food-review-pour.glass | H 0.235 m above the table; P 12-13; D 0.36-0.39 m to the rim; phone nearly still (6 cm, 8.6 deg turn); t 5.7 s; rim fill 0.28, glass 0.82 (runs off the left edge by design) | the prop slides and the phone stays still; glass at 0 deg near the liquid line or 30-45 deg for a highball; 2x from 35 cm | keep | The move is the first-timer rule: the hand moves the glass and the phone stays [RA19][RA 2d option B]. The lens sits about 4 cm above the rim at 12 deg, close to the liquid line [RA42]. Optional: 2x at 35-50 cm [RA42]. |
| pancake_clear_path | plate-reveal | complex | food-review-table.spread | H 0.085 m above the table, lens 54 cm inside the edge; portrait blocked on every frame (4.7 cm into the table); P 0.6->2.3; D 2.05->0.50 m; path 1.55 m; v 0.20/0.37 m/s; t 7.9 s; fill 0.41 | tall-dish hero: upside down at the stack; portrait alternative 10-20 deg down from 30 cm | orientation | Lens 8.5 cm over the table, which is not possible in portrait [RA 11 tall dish][RB 0.3]. Portrait alternative: phone still in portrait at 10-20 deg down, 30 cm from the stack, while the two hands clear the foreground. That is the prop-moves rule [RA 2d option B] and needs no 1.55 m low push (judgement). |
| handoff_counter_cup | hand-off | easy | none | H 0.15->0.20 m above the counter top level (1.20-1.25 m floor), 91 cm in front of the counter; P 4.2->7.5; D 1.11->1.00 m; slide 23 cm plus an 11.5 deg turn; v 0.06/0.11 m/s; t 3.9 s; cup fill 0.19 | counter hand-off: chest height, phone still, the barista's hand passes the cup toward the lens; C1 20-30 deg down, 40-60 cm | adjust (distance, pitch, make static) | 1.0 m vs 40-60 cm and pitch 7 deg vs 20-30 deg [RB C1][RA 8]. The research move is static [RA 8][RB32]. The record itself asked for a still hold at 0.6 m and 20 deg. |
| handoff_plate_lands | hand-off | easy | none | H 0.42->0.45 m above the table; P 33.7->39.0; D 0.68->0.64 m; path 0.13 m plus a 12 deg turn; t 3.8 s; pasta fill 0.30, plate 0.56 | hand-off 1: static POV, 45 deg down from the seated eye line, 35-45 cm to the spot | adjust (distance, pitch, make static) | 0.64 m vs 35-45 cm, 39 deg vs 45 deg, and the phone moves while the research keeps it still with focus locked first [RA 8][RA19][RA23]. After this it is the easiest hand-off variant, which has no guide today. |
| pour_top_down_latte | pour | easy | food-review-drink.pour | H 0.49->0.43 m above the counter top; P 85.7; D 0.42->0.36 m; push 6 cm in 4.7 s; cup fill 0.56 (x 0.29-0.86), centre 0.50 | pour 2: static 90 deg on latte art, cup about half the width, 20-30 cm, 1x | keep | The angle and fill match: "cup fills about half the width" [RA8]. The measured fill shows that 20-30 cm would overfill on 1x, so the cm range is judgement. Optional: make the 6 cm push static and centre the cup (x 0.86 touches the rail) [RA2]. |
| pour_side_low | pour | easy | food-review-drink.pour, food-review-pour.build | H 0.15-0.17 m above the counter top, 27 cm in front of the edge (portrait possible, measured); P 9.9->8.0; D 0.57->0.59 m; drift 11 cm plus an 11 deg turn; t 4.8 s; cup fill 0.26 | pour 3a, pour-over: eye level or slightly low, 25-35 cm, 1x, static | adjust (distance, make static) | Orientation check closed: portrait works. 0.58 m vs 25-35 cm [RA8], so the cup is only 0.26 wide. The research pour is static, "let the action carry" [RA18]. |
| pour_upside_down | pour | complex | none (upside down, off P0) | lens 1.8 cm above the counter top level, 12 cm in front of the edge; P 10 up; D 0.28-0.31 m; slide 18 cm plus a 34 deg turn; w 7/13.5 deg/s; t 4.8 s after a 1 s setup; fill 0.61 (x to 0.91) | pour 4: upside down at the liquid line, the bartender pours, static | adjust (make static, framing); stays off P0 | The research move is static [RA42][RA7]. The fill runs into the right rail [RA2]. Measured: the lens is past the counter edge, so a portrait hold with the phone hanging in front of the counter reaches the same lens position (grip judgement). The P0 alternative is still pour 1, static 45 deg [RA8]. |
| steam_low_backlit | steam | easy | none | H 0.075 m above the table top level, 9 cm in front of the edge, never over the table (portrait possible as an edge hold, measured); P 0; D 0.57 m; slide 14 cm plus a 14 deg turn; v 0.04/0.07 m/s; t 3.8 s; cup fill 0.33 | steam 1 (upside down at the rim) or 2 (portrait 15 deg down, dark wall); 25-35 cm, static, back or side-back light | adjust (distance, make static) | Orientation check closed: an edge hold works in portrait, but the beat must say "phone past the table edge" (judgement). 0.57 m vs 25-35 cm, and steam is filmed static and at once [RA9][RA10]. |
| steam_push_in_high | steam | easy | none | H 0.65->0.42 m above the table; P 37; D 0.88->0.49 m; path 0.39 m; v 0.10/0.19 m/s; t 3.9 s; fill 0.36 | steam 2: portrait 15 deg down, 25-35 cm, dark background, static | redo: steam 2 (static, portrait 15 deg down) | Steam reads only at 0-20 deg against a dark background (RA 4, judgement). 37 deg from 49-88 cm is a different shot. Steam is static [RA9]. |
| steam_orbit_eye | steam | complex | first-visit.drink, food-review-drink.cup | H 0.08 m above the table top level, 3 cm or more in front of the edge on every frame (edge hold possible); P 0; D 0.57-0.59 m; arc 60 deg at 12.2 deg/s; v 0.12 m/s; t 4.9 s; fill 0.32 | steam: static only; an orbit is a plate move at 30-45 deg pitch | redo: steam 2 (static, portrait 15 deg down), with steam 3 (one spoon stir, static) as the second option | No steam reference moves the camera, "film at once" [RA9][RA10]. Orbits belong to plates, at 30-45 deg pitch, not during action [RA 2c][RA18]. An eye-level orbit that keeps the phone outside the table edge needs the cup at a corner, which is not first-timer repeatable (judgement). The arc is 60 deg vs 30-45 deg. |
| steam_slide_pull_out | steam | complex | first-visit.drink, food-review-drink.cup | H 0.17->0.20 m above the table; P 5; D 0.28->0.68 m (40 cm pull-back plus a 22 deg turn); path 0.44 m; v 0.08/0.14 m/s; t 5.8 s; fill 0.27 | steam: static, 25-35 cm | redo: steam 3, one spoon stir with the phone static (easy) | Pull-backs are not a referenced steam move [RA9]. The research replaces pull-outs with pans or reveals [RB 0.4] (extension to table scale is judgement). The steam is gone before 5.8 s [RA9]. |
| bite_pip_dish | first-bite | easy | first-visit.forkful, food-review.bite, food-review-sweet.taste, food-review-handheld.bite, food-review-table.bite | static; H 0.42 m above the table top level, 18 cm in front of the edge; P 20.5; D 0.76 m to the forkful; fork plus pasta fill 0.50 (x 0.35-0.85), centre 0.54 | bite 1, food only: the fork lifts a bite, phone static at 45 deg, close on 1x | adjust (pitch, distance, framing) | The static, food-only move matches [RA20][RA53][RA31 0:47]. Pitch is 20 deg vs 45 deg, and 0.76 m vs about 35-45 cm (distance judgement). The record itself asked for 0.4 m. The forkful touches the 85% rail [RA2]. |
| bite_selfie_eye | first-bite | easy | same 5 steps | front camera static; lens 3 cm above the eyes; P 8.7 down; 0.43 m to the eyes; eyes at 46% from the top; face fill 0.50; lens 18 mm (58.7 deg) | selfie at full arm's length 55-65 cm (RA 5a says 40-50 cm, judgement), eye level, 0-10 deg down, eyes at 33%; front camera 45-50 deg | adjust (distance, framing, lens) | 43 cm is in the distortion zone RB19 warns about. Use 55-65 cm [RB19][RB20]. Eyes at 33% [RB15]. The 18 mm scene lens is about 10 deg wider than a real front camera [RB20][RB22]. Use about 22-24 mm so the fill reads true (judgement). |
| bite_friend_three_quarter | first-bite | easy | same 5 steps | rear 1x; lens 2 cm above the eyes; P 6.2->4.8; 0.95 m to the eyes; curved drift 8 cm and 4 deg; t 4.8 s; eyes at 46%; face fill 0.33 | friend 60-90 cm, eye level 0-10 deg, static or a 15-20 cm push | adjust (framing, distance) | Height and angle match [RA45]. 0.95 m is just over 90 cm (judgement: 0.85 m). Eyes at 46% vs 33% [RB15]. |
| sip_selfie_eye | sip | easy | first-visit.sip, food-review-drink.sip, food-review-pour.sip | identical camera to bite_selfie_eye: 0.43 m, +3 cm, 8.7 down, eyes at 46%, fill 0.50, 18 mm | as bite_selfie_eye | adjust (distance, framing, lens) | As bite_selfie_eye [RB19][RB15][RB20]. |
| sip_high_lean | sip | easy | same 3 steps | front camera static; lens 22 cm above the eyes; P 28.2 down; 0.51 m to the eyes; eyes at 47%; face fill 0.42 | selfie: eye height or 5-10 cm above, 5-10 deg down, 55-65 cm | adjust (height, pitch, distance, framing) | 22 cm above and 28 deg down vs 5-10 cm and 5-10 deg [RB17]. 51 cm vs 55-65 cm [RB19]. Once adjusted it nearly equals sip_selfie_eye, so one of the two may be redundant (judgement). |
| sip_friend_side | sip | easy | same 3 steps | rear 1x; lens 1 cm above the eyes; P 5.9->4.4; 0.93 m to the eyes; drift 8 cm and 4 deg; t 4.8 s; eyes at 46%; face fill 0.31 | friend 60-90 cm, eye level, static | adjust (framing, distance) | As bite_friend_three_quarter [RA45][RB15]. |
| room_reveal_cup | room-from-table | complex | first-visit.room | H 0.08 m above the table, lens 50 cm inside the edge; portrait blocked on every frame (5.2 cm into the table); P 0; truck 35 cm at 0.07 m/s; t 4.9 s | D2 with a short blocker: upside down; portrait alternative: a tall blocker (bottle, vase, plant) at seated height, or the phone on a saucer at a 30-40 deg high angle | orientation | Lens 8 cm over the table, which is not possible in portrait [RB 0.3 table]. Portrait alternative: D2 from behind a bottle or plant at seated eye height 110-120 cm, truck 10-20 cm/s for 3-4 s [RB31][S21][RB35]. room_reveal_plant already covers this for the same step. |
| room_seated_pan | room-from-table | easy | food-review-table.how | H 0.165 m above the table (0.95 m above the floor), fixed; P 12 down; pan 55 deg in 4.7 s; w 11.5/20.4 deg/s (eased) | D3: seated lens 110-120 cm, pitch 0-5, 45 deg in 5-6 s at 1x (8-10 deg/s) | adjust (height, pitch, speed) | The open speed check is confirmed too fast: peak 20 deg/s vs a 10 deg/s ceiling, which reads as a whip [RB29][RB30]. Raise 15-25 cm to seated eye height and pitch 0-5 deg (heights judgement). Use 45 deg at an even pace over 5.5 s. |
| room_reveal_plant | room-from-table | complex | first-visit.room | H 1.18 m (floor); P 2.8; truck 40 cm; v 0.07/0.13 m/s; t 5.8 s; room fill over 1 | D2 with a tall blocker: 110-120 cm, pitch 0-5, truck 10-20 cm/s for 3-4 s, blocker out by second 2 | adjust (duration, speed) | Height and pitch match (judgement values in RB D). 5.8 s vs 3-4 s and 7 cm/s vs 10-20 cm/s [RB31][S21]. The beat "stand in the aisle" contradicts the measured seated height. Pick one (judgement). Blocker distance not measured. |
| verdict_eye_level | verdict | easy | 7 verdict steps (first-visit, food-review, -drink, -pour, -sweet, -handheld, -table) | identical camera to bite_selfie_eye: 0.43 m, +3 cm, 8.7 down, eyes at 46%, fill 0.50, 18 mm | E1: full arm's length 55-65 cm, eye height or 5-10 cm above, 5-10 deg down, eyes at 33%, 4-6 s | adjust (distance, framing, lens) | 43 cm vs 55-65 cm [RB19]. Eyes at 46% vs 33% [RB15][RB3]. Front lens FOV as above [RB20][RB22]. Height and pitch are within range [RB17]. |
| verdict_high_plate | verdict | easy | same 7 steps | front camera static; lens 22 cm above the eyes; P 27.8 down; 0.75 m to the eyes; eyes at 41%; face x 0.09-0.43 (left), fill 0.34 | E1 as above, with the dish raised to y 50-65% | adjust (height, pitch, distance, framing) | 22 cm and 28 deg vs 5-10 cm and 5-10 deg, which is close to the "from above" angle the research avoids [RB17]. 0.75 m is beyond arm's length (judgement: 0.60 m). The left offset is allowed but extreme [RB15][RB3]. |
| verdict_friend_eye | verdict | easy | same 7 steps | identical camera to bite_friend_three_quarter: 0.95 m, eye level, P 6->5, drift 8 cm, eyes at 46%, fill 0.33 | E2: friend 1.2-1.5 m at 1x, eye height, 0 deg, static | adjust (distance, framing) | 0.95 m vs 1.2-1.5 m, the distortion-free distance [RB19][RB18][RB28]. Eyes at 33% [RB15]. |

People guides, checked separately against the targets given for this audit:

| Guide | Camera | Measured distance | Target | Height vs eyes | Eyes from top |
|---|---|---|---|---|---|
| verdict_eye_level | front | 0.43 m | selfie 55-65 cm | +3 cm | 46% |
| verdict_high_plate | front | 0.75 m | selfie 55-65 cm | +22 cm | 41% |
| verdict_friend_eye | rear 1x | 0.95 m | friend 1.2-1.5 m | +2 cm | 46% |
| bite_selfie_eye | front | 0.43 m | selfie 55-65 cm | +3 cm | 46% |
| sip_selfie_eye | front | 0.43 m | selfie 55-65 cm | +3 cm | 46% |
| sip_high_lean | front | 0.51 m | selfie 55-65 cm | +22 cm | 47% |
| bite_friend_three_quarter | rear 1x | 0.95 m | friend 60-90 cm | +2 cm | 46% |
| sip_friend_side | rear 1x | 0.93 m | friend 60-90 cm | +1 cm | 46% |

Shared cameras: verdict_eye_level, bite_selfie_eye and sip_selfie_eye use one camera pose, and verdict_friend_eye
and bite_friend_three_quarter use another, so one fix per pose covers several guides.

## 3. Proposed new guides (easiest variants with no guide yet)

From `shot_library.md`, filtered by the measurements above. Each is portrait and easy unless stated.

| Shot type | Variant | Key numbers | Refs | Fills the gap left by |
|---|---|---|---|---|
| entrance | A4: a friend films static while you walk in | friend at chest height, 0 deg, 3-4 m from the door at 1x, 3-5 s; the door empty for 1 s, then the creator enters; back fills about 40% at the end | RB53, RB41, RB3 | redo of entrance_door_low |
| menu-board | B1: static straight-on at 2x | 2-3 m back, lens at the board centre height or pitch at most 10 deg up, 2 s | RB51, RB33, RB13 | none (the most repeatable board shot) |
| menu-board | B3: tilt from the board down to the case | tilt 20-30 deg in 3 s, end pitch level or down | RB51 | optional; menu_board_tilt_up is the reverse |
| menu-card | 2: a hand opens the menu, phone still | 90 deg overhead, about 45 cm on 1x (measured fit), 3-4 s | RA4, RA8, RA21 | redo of menu_card_push |
| counter-order | C1: POV hand receives the cup | chest height about 1.3 m, 20-30 deg down, 40-60 cm, 1x, static 3 s, cut on the grab | RB32, F19, RB41 | redo of counter_through_cup_handle |
| plate-reveal | 1: turntable | phone still at 45 deg, 25-30 cm on 1x, the plate turned 90 deg by hand in 4 s | RA16, RA35 0:35, RA15 | none (easiest plate reveal) |
| plate-reveal | 2: napkin pull (option B) | phone still at 45 deg in portrait, a hand pulls the napkin sideways out of frame, focus locked on the plate | RA 2d, RA17, RA23 | orientation of plate_tissue_slide |
| plate-reveal | 4: overhead pedestal rise (complex) | 90 deg throughout, 25-30 -> 45-60 cm, 3-4 s, standing | RA4, RA5, RA21 | redo of table_spread_orbit; re-spec the pending plate_rise_overhead |
| hand-off | 1: static POV on the table spot | 45 deg down from the seated eye line, 35-45 cm, focus and exposure locked, the plate set down | RA19, RA31, RA23 | handoff_plate_lands after its adjust gets there; a new scene is not needed |
| pour | 1: static 45 deg on a cup while someone pours | 25-35 cm on 1x, 3-6 s, the stream from the top edge | RA8, RA18 | P0 alternative to pour_upside_down |
| steam | 2: portrait 15 deg down, dark wall behind | 25-35 cm on 1x, back or side-back light, static 3-4 s | RA9, RA10 | redo of steam_push_in_high and steam_orbit_eye |
| steam | 3: one spoon stir to lift fresh steam | as steam 2, a hand stirs once, phone static | RA9 (judgement) | redo of steam_slide_pull_out |
| first-bite | 3: selfie propped against a glass | front camera at eye level, 55-65 cm, 4-6 s | RA 5a, RB19, RB15 | none |
| sip | 1: cup only | phone static at 45 deg on the cup, a hand lifts it up out of frame, the saucer stays, 4-5 s | RA 6, RA8 | none (no cup-only guide) |
| room-from-table | D1: static wide from the seat | seated lens 110-120 cm, pitch 0-5, 3-4 s, people move | RB35 3:36, RB15, RB41 | none (easiest room shot) |
| room-from-table | D4: tilt up from your plate to the room | 30 deg in 3-4 s, seated | RB D | orientation of room_reveal_cup (with room_reveal_plant) |
| verdict | E4: phone propped on the table, rear camera | portrait leaning back 5-10 deg against a cup, about 1.2 m, 4-6 s | RB18, RB19, RB28 | none |

## 4. Summary

Verdict counts over 37 guides:
- keep: 2 (glass_slide_close, pour_top_down_latte)
- adjust: 25
- redo: 7 (entrance_door_low, menu_card_push, counter_through_cup_handle, table_spread_orbit, steam_push_in_high,
  steam_orbit_eye, steam_slide_pull_out)
- orientation: 3 (plate_tissue_slide, pancake_clear_path, room_reveal_cup)

Four of the shot_library open checks are closed by measurement. counter_edge_to_pass (15 cm, 40 cm in front of the counter), pour_side_low (15 cm, 27 cm out) and
steam_low_backlit (7.5 cm, 9 cm past the table edge) are portrait-feasible because the lens is past the edge.
room_reveal_cup is not portrait-feasible (8 cm over the table). room_seated_pan is too fast (peak 20 deg/s).

The 5 most important changes:
1. Steam: three of the four steam guides use camera moves no steam reference supports (orbit, high push, slide and
   pull-out). Those include both guides offered for first-visit.drink and food-review-drink.cup. Replace them with
   steam 2 (static, portrait 15 deg down, 25-35 cm) and steam 3 (spoon stir) [RA9][RA10].
2. People framing: the eight people guides (five distinct scene cameras) place the eyes at 41-47% instead of 33% [RB15].
   The selfies sit at 43 cm instead of 55-65 cm [RB19]. The friend verdict sits at 0.95 m instead of 1.2-1.5 m. The front-camera
   scene lens is about 10 deg wider than a real front camera. verdict_* guides are offered in all seven scripts.
3. Orientation: plate_tissue_slide (offered in four plate steps), pancake_clear_path and room_reveal_cup hold the
   lens 7.5-8.5 cm over the table. Measured, the phone body would sit 4.7-5.6 cm inside the table in portrait.
   Replace them in P0 with the napkin pull, a still 10-20 deg view of the stack, and the bottle or plant reveal.
4. Speeds and distances at the counter and the door: menu_board_truck 0.29 m/s (target 0.10-0.15 m/s).
   counter_edge_to_pass 0.19 m/s plus a 35 deg turn (target 0.05-0.10 m/s). room_seated_pan peaks at 20 deg/s (target 10 deg/s).
   entrance_walk_in ends 5 m short of the door with a 1.06 m/s peak. entrance_sign_tilt is shot at 1.4 m with a 45 cm drop
   instead of 4-8 m standing still.
5. Plate set: plate_high_orbit, recommended for four steps, needs a 0.38 m radius and a 40 deg arc (now 0.60 m and 60 deg).
   plate_low_push_in needs 45 deg instead of 12 deg. table_spread_orbit needs a true 90 deg overhead rise, and the pending
   plate_rise_overhead copies its flawed move, so fix that spec first.
