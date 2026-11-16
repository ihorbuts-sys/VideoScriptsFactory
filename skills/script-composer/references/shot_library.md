# Shot library (for planning steps)

Compiled 2026-11-10 from `research/reference_shots/food_and_drink.md` (RA refs) and `venue_and_people.md` (RB refs);
sources with URLs and opened/search status: `research/reference_shots/sources_*.md`; the earlier vocabulary:
`research/commercial_shots.md` and `research/sources.md` (S, F refs). Read the research section named in each row
before writing a guide request. "(judgement)" marks values no reference states; most distances and speeds are
judgement, most angles and timing windows are cited. Video references were read from titles and chapters only: the
watch lists (food section 9, venue "Gaps") name the timestamps to check before animating a new guide.

## Rules that apply to every step

- Frame and safe box: 9:16; the platform UI covers about the top 15%, the bottom 25-35% and the right 10-15%; keep
  faces, the hero, signs and caption text inside x 8-85%, y 15-65% [RA2][RB3][RB4]. Guides are stricter: the hero
  sits inside the 28% / 35% band (`STYLE.md`). Eyes at one third from the top [RB15].
- Speed: slower reads as cinematic and is easier [RA17][RA49]. Pans at 1x: 8-10 degrees per second, 0.5x up to
  about 15 [RB29][RB30] (the earlier 15-30 degrees per second was too fast). Walks 0.5-0.8 m/s, ninja walk, two
  hands, elbows in [RB23][RB25] (speed judgement). Never zoom while moving [RB23][RA21].
- Lens: 1x by default; 2x for menu boards, glassware and 3/4 plates from 35 cm or more; 0.5x only for tight rooms and
  pans, never for faces or close food [RA8][RA42][RA47][RB18][RB23].
- Hook: frame one carries the hook, the claim lands by 2 s, the reason to stay by 6 s; a person talking early beats a
  facade or a logo [RB8][RB9][RB10]. The entrance is a bridge, not frame one, unless it carries a spoken hook [RB13].
- Visitor side: ask staff first, no lingering staff or guest faces, no payment screens [RB41][RB42].
- Phone orientation: portrait unless the lens must be under about 10-12 cm above a surface; P0 uses portrait only
  (`STYLE.md`). Upside-down shots and their portrait alternatives: food section 11, venue section 0.3.
- First-timer rule (from both reports): the easiest variants keep the phone still and let a hand, the plate or the
  person move.

## Per shot type: variants, easiest first

Level (easy / complex) follows the composer's rule (talk-friendly or not); a step's guides share one level.

| Shot type | Variants, easiest first (level; orientation) | Key numbers | Matching guides today | Research |
|---|---|---|---|---|
| entrance | 1 sign-to-door tilt, standing still (easy; portrait) - 2 friend static, you walk in (easy) - 3 POV walk to the door, cut before opening (easy) - 4 push-through with the door (complex) - 5 ground-level walk-in (complex; upside down) | chest height ~130 cm; tilt 20-30 deg in 3-4 s; walk 0.5-0.8 m/s for 3-5 s from 3-5 m; 1x [RB25][RB31][RB23] (heights, speeds judgement) | entrance_sign_tilt (1), entrance_walk_in (3), entrance_door_low (low POV) | venue A |
| menu-board | 1 static straight-on at 2x, 2 s (easy) - 2 tilt from board down to the case (easy) - 3 truck along the board (easy) | step back until pitch <= 10 deg up; 2-3 m at 2x or 1.5 m at 1x; truck 10-15 cm/s for 3-4 s [RB51][RB33] | menu_board_truck (3), menu_board_tilt_up (reverse of 2) | venue B |
| menu-card | 1 static overhead of the card with the cup (easy) - 2 hand opens the menu, phone still (easy) - 3 overhead rise from the name to the card (easy) - 4 lateral slide along a standing card (upside down) | 90 deg for a flat card, 25-35 cm, 1x; rise 15 cm in 3 s; tilt 15 deg off a lamp to kill glare [RA4][RA8] (distances judgement) | menu_card_top (close to 1/3), menu_card_push | food 7 |
| counter-order | 1 POV hand receives the cup, static, cut on the grab (easy) - 2 friend over your own shoulder (easy) - 3 same with a slow push (easy) - 4 counter-top slide (complex; upside down, or 15 cm high in portrait) | chest height 20-30 deg down, 40-60 cm, 1x; push 20-30 cm in 3-5 s; skim truck 5-10 cm/s [RB32][RB40] | counter_over_shoulder (2-3), counter_edge_to_pass (4, check orientation), counter_through_cup_handle | venue C |
| plate-reveal | 1 turntable: phone still at 45 deg, turn the plate 90 deg (easy) - 2 napkin pull, phone still (easy) - 3 3/4 push-in with elbows on the table (easy) - 4 overhead pedestal rise, standing (complex) - 5 orbit of about 30 deg (complex) - napkin/slider slide resting on the table (complex; upside down) | 3/4: 45 deg, 45-50 -> 25-30 cm, 1x, 20 cm in 3-4 s; overhead: 90 deg the whole way, 25-30 -> 45-60 cm, 3-4 s, standing; orbit: 30-45 deg pitch, radius 30-40 cm, 30-45 deg arc in 4 s [RA4][RA5][RA15][RA16][RA21] (distances, speeds judgement) | plate_low_push_in (3), plate_high_orbit (5), plate_tissue_slide (slide), plate_rise_overhead draft (4) | food 2 |
| hand-off | 1 static POV on the empty table spot while the plate is set down (easy) - 2 same, own hand takes the cup (easy) - 3 counter hand-off at chest height (easy) - 4 served, then a 10-15 cm push (easy) | 45 deg down from the seated eye line, 35-45 cm, 1x; lock focus and exposure on the spot first [RA19][RA31][RA23] (framing judgement) | handoff_plate_lands, handoff_counter_cup | food 8 |
| pour | 1 static 45 deg on a coffee cup while someone pours (easy) - 2 static 90 deg on finished latte art (easy) - 3 you pour from a carafe, phone in the other hand (easy) - 4 lens at the liquid line, bartender pours (upside down) - 5 slow-mo by a window | 25-35 cm, 1x; espresso 45 deg, art 90 deg; crema contrast lasts about 30 s, beer foam under 60 s [RA8][RA42][RA43] | pour_top_down_latte (2), pour_side_low (low pour; check orientation), pour_upside_down (4, off P0) | food 3 |
| steam | 1 fresh cup, lens at the rim, window behind (upside down) - 2 portrait 15 deg down, dark wall behind (easy) - 3 one spoon stir to lift fresh steam (easy) - 4 bowl from 30 deg, backlit | 25-35 cm, 1x; back or side-back light, dark background, film at once (steam lasts seconds) [RA9][RA10] | steam_low_backlit (check orientation), steam_push_in_high, steam_orbit_eye, steam_slide_pull_out | food 4 |
| first-bite | 1 food only: fork lifts a bite toward the lens, phone static at 45 deg (easy) - 2 friend across the table, eye level, static (easy) - 3 selfie propped against a glass (easy) - 4 hand-held selfie (easy) | selfie eye level 0-10 deg, 40-50 cm (verdict: 55-65 cm); friend 60-90 cm at 1x/2x; 4-6 s: look, bite, 2 s reaction [RA25][RA45][RB19] | bite_pip_dish (1), bite_friend_three_quarter (2), bite_selfie_eye (4) | food 5 |
| sip | 1 cup only: phone static at 45 deg, hand lifts the cup out of frame (easy) - 2 friend films (easy) - 3 propped selfie - 4 hand-held selfie | eye level; selfie 40-50 cm, friend 60-90 cm; 4-5 s [RA45][RA8] | sip_selfie_eye, sip_high_lean, sip_friend_side (no cup-only guide yet) | food 6 |
| room-from-table | 1 static wide, elbows on the table, 3 s (easy) - 2 tilt up from your plate to the room (easy) - 3 reveal from behind a bottle or plant (complex) - 4 slow pan at 0.5x (easy) - 5 reveal from behind a cup at table level (complex; upside down) | seated eye height 110-120 cm, pitch 0-5 deg; pan 45 deg in 5-6 s at 1x or 60 deg in 4 s at 0.5x; reveal truck 10-20 cm/s, blocker 5-15 cm from the lens [RB29][RB30][RB35] | room_seated_pan (4, check speed), room_reveal_plant (3), room_reveal_cup (5, check orientation) | venue D |
| verdict | 1 seated selfie at full arm's length, dish raised into frame, 5 s (easy) - 2 phone propped, rear camera (easy) - 3 friend across the table at 1x (easy) - 4 walk-and-talk selfie leaving (easy) | front camera at full arm's length 55-65 cm (a 30 cm selfie widens the nose about 30%), eye height or 5-10 cm above, 5-10 deg down; friend 1.2-1.5 m at 1x; 4-6 s for 8-14 words; never pan the selfie camera [RB17][RB19][RB20] | verdict_eye_level (1), verdict_high_plate, verdict_friend_eye (3) | venue E |
| hook (frame one) | 1 the verdict line moved to the front (recorded last, edited first) - 2 pour or steam close-up with the place name - 3 one-second flash of the first bite - 4 walk-in with a spoken hook line | claim by 2 s; a person early raises hook power ~50%, talking to camera lifts 2 s view-through ~14% [RB8][RB9][RB10] | an editor rule, not a guide | venue F |

## Open checks raised by the research (not yet done)

- Orientation check of active portrait guides whose lens sits near a surface: `pour_side_low`, `steam_low_backlit`,
  `room_reveal_cup`, `counter_edge_to_pass`. The research says a lens under about 10-12 cm needs the phone upside
  down; measure each guide's lens height and either confirm a portrait hold (phone held past the table edge) or move
  the guide to upside down (off P0).
- `room_seated_pan` speed against 8-10 deg/s at 1x.
- Variants with no guide yet that are the easiest for first-timers: turntable plate, napkin pull, cup-only sip,
  static hand-off POV, static overhead menu card.
