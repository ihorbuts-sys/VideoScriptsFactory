# Reference shots: food and drink (part A)

Purpose: shot specs a first-time visitor can repeat with a phone at a cafe or restaurant table, for the line-art
guides (composition on the table, camera angle, one move). Every value cites reference ids from
`sources_food_and_drink.md` (RA1 and up). Values I inferred are marked (judgement). The earlier vocabulary in
`../commercial_shots.md` still holds; this file narrows it to seven food-and-drink shot types and adds evidence.

## 0. Evidence quality, read first

- What was reachable: written guides by food photographers and videographers (RA4, RA5, RA8, RA9, RA19, RA21,
  RA42, RA43), two transcripts of video breakdowns (RA14, RA15), LensVid write-ups of Daniel Schiffer's shoots
  (RA12, RA13), platform guidance and safe-zone specs (RA1, RA2, RA3), and the metadata and chapters of 15
  YouTube tutorials by food videographers (RA11, RA27 to RA41).
- What was not: YouTube transcripts. For those videos I only claim what the title, description and chapter list
  say; the timestamp tells the owner where to watch to check framing. A short visual check of the timestamps in
  the "Watch list" (section 9) would firm up the numbers marked (judgement).
- Most numeric values in the evidence are angles (degrees) and timing windows. Distances in cm, move speeds and
  durations are almost never stated by any reference; they come from `../commercial_shots.md` and are marked
  (judgement). That is the biggest gap.
- No reference describes a "napkin slide" reveal on food, a hand-off filmed by the receiver, or a menu-on-table
  shot in detail. Those specs are built from adjacent evidence (slide into frame RA19, foreground reveal RA17
  RA50, hands RA20 RA5) and say so.

## 1. Shared conventions

### 1.1 Frame and safe areas (9:16, 1080 x 1920)

| Edge | TikTok [RA2] | Reels [RA2][RA3] | Shorts [RA2] | Use for Loca (judgement: the union of the three) |
|---|---|---|---|---|
| Top | 130 px | 269 px (14 %) | 288 px | 290 px (15 %) |
| Bottom | 484 px | 672 px (35 %) | 672 px | 672 px (35 %) |
| Right | 140 px | 65 px; action rail covers the rightmost 21 % of the bottom 40 % [RA3] | 192 px | 192 px (10 %) |
| Left | 44 px | 65 px (6 %) | 48 px | 65 px (6 %) |

- These are ad specs; no platform publishes organic margins [RA2][RA3]. TikTok asks to keep content inside the UI
  safe zone [RA1].
- Resulting clear box: x 65 to 888 px, y 290 to 1248 px, about 820 x 960 px (judgement from RA2). Its center is at
  about 40 % of frame height and 44 % of width, so a "centered" hero in Loca sits slightly above and left of the
  true center (judgement).
- Reels grid covers crop the frame to 3:4, cutting 240 px top and bottom [RA3]; a hero inside the clear box
  survives that crop (judgement).
- Text space: the free band above the hero (y 290 to about 600) is where a caption fits without covering food
  (judgement). Keep the bottom 35 % to table texture, napkin, cutlery, not to the hero.

### 1.2 Phone orientation (owner addition)

| Orientation | What it is | Lens height when the phone rests on its edge on the table | When it is needed |
|---|---|---|---|
| portrait | Normal grip, lens at the top edge | About 13 to 15 cm (phone length minus lens inset, judgement) | Every shot with the lens 15 cm or more above the table: 3/4 views, overhead, selfies, most pours |
| portrait upside down | Phone flipped, lens at the bottom edge | About 1 to 3 cm (judgement) | Lens at table or liquid level: straight-on and low hero of tall food [RA5][RA4], a low glass or cup at its liquid line [RA42], table-level slides with the phone resting on the table (judgement) |

- Evidence: MakeUseOf tells phone users to turn the phone upside down for straight-on shots of tall food [RA5];
  Apple's own support account and an Apple Education author recommend it for getting close to the ground, and
  the Camera app saves the clip upright [RA7][RA6]. If the image goes blurry that close, back up or use 0.5x,
  and use orientation lock if the preview flips [RA7].
- Implementation note (judgement): Face ID iPhones do not rotate the interface to portrait upside down, so the
  Loca guide overlay must be drawn from device motion, not from interface rotation, and the capture pipeline must
  set the video rotation itself; the stock Camera app's "saves upright" behaviour [RA7] is not automatic in a
  custom capture session.
- Portrait alternative for every upside-down case: hold the phone in portrait with the top edge just above the
  table and pitch it down 5 to 15 deg, or raise the subject (saucer stack, menu under the plate). The cost is a
  lens 10 to 15 cm higher, which loses the "tower" read of tall food (judgement).

### 1.3 Lens and distance

- Main 1x lens is the default for cups and plates; the ultra-wide (0.5x) makes cups oval close up [RA8]. Wide
  lenses distort 3/4 food; use the 2x or 3x lens button and step back, never pinch [RA47][RA33 3:03]. Drinks in
  glass: 2x or 3x and move back [RA42]; a longer lens is a named beginner tip [RA34 1:25].
- Disagreement: RA4 says a phone should stick to overhead or straight-on because a 45 deg phone shot distorts;
  RA8 and RA43 say main 1x lens; RA42 says 2x/3x for glassware. Reconciled rule (judgement): 1x for overhead and
  for anything under 30 cm; 2x when the phone can be 35 cm or more from the subject (3/4 views of plates and
  glasses); 0.5x only when the 1x cannot focus that close [RA7].
- Close focus: the main lens of recent iPhones focuses from about 15 to 20 cm; closer, Pro models switch to the
  macro camera (judgement, not in a reference). Guides should not ask for less than 20 cm on 1x.

### 1.4 Light, steadiness, capture (applies to every shot)

- Window light, move the plate to the light [RA20][RA8]; turn off the light directly above the table if allowed
  [RA8][RA32 0:41]; back or side light for food, liquids and steam [RA32 1:49][RA18]; flash off [RA24]. A friend's
  white phone screen as fill in a dark room [RA20].
- Two hands, elbows on the table or the ribs, turn the body not the wrists, no zoom while moving [RA46]. A small
  tripod helps video [RA20]; handheld can look jerky [RA19], yet Schiffer shoots fully handheld [RA14][RA13].
- Lock AE/AF on the subject (crema, rim), not on the white saucer [RA8][RA42][RA23].
- Frame rate: 60 fps for slow-down of pours, 120 fps only in daylight [RA27][RA48]; Schiffer's coffee b-roll was
  1080p 120 [RA14].
- Roll 1 s before and after the action [RA18]; check that consecutive shots line up and colours match [RA14 4:36].
- Speeds and durations below are from `../commercial_shots.md` (judgement) unless cited; the commercial originals
  use motion control for slow, repeatable moves [RA49], so a phone guide should lean slow.

## 2. Plate reveal of a single dish

References: RA4, RA5, RA12, RA15, RA16, RA17, RA18, RA19, RA21, RA22, RA30 (6:52), RA31 (1:49, 2:53), RA35 (0:35,
2:39), RA38 (0:55, 3:46, 6:26), RA50.

Common composition (all four variants): the plate is the only hero; one supporting object (glass, cup, folded
napkin, cutlery) behind or to one side at about a third of the frame from the hero, never in front of it
(judgement, consistent with "props should feel natural" and "too many props compete", RA19). Messy crumbs are
fine, a lazy mess is not [RA20].

### 2a. Overhead flat-lay rise (pedestal up)

| Field | Value |
|---|---|
| Composition | Plate centered in the clear box (center at about 40 % height) [RA2] (judgement on placement); round plate reads well centered; supporting cup or glass at the upper-left third, cutlery on the right of the plate pointing down; bottom 35 % is table texture (judgement) |
| Angle | 90 deg, sensor parallel to the table [RA4][RA5][RA8]; MagSafe and selfie-stick rigs only get near 90 [RA22] |
| Distance / lens | Start 25 to 30 cm, end 45 to 60 cm above the plate, 1x (judgement; straight down distorts least on a phone [RA47]) |
| Orientation | portrait |
| Start framing | Close: plate rim touches the frame edges left and right (judgement) |
| End framing | Wide: plate plus the supporting objects and a strip of table (judgement) |
| Move | Pedestal up, done by hand on a phone [RA21]; 20 to 30 cm in 3 to 4 s, about 8 cm/s, 0.5 s still head and tail (judgement) |
| Reads as cinematic | The spread "appears" around one dish; overhead suits flat food and dishes with toppings [RA4][RA18] |
| Common mistakes | Phone tilts because the lens is off-center [RA5]; own shadow and hand shadow on the plate [RA23]; using it for a burger or tall food, which loses the interest [RA18][RA4] |
| Feasibility | Standing beside the table, two hands, elbows tucked: feasible but the hardest variant (arms rise and tilt). Seated: only for small plates, lens ends up at chin height (judgement) |
| Props | Napkin, cutlery, a second plate or glass; nothing on top of the hero |

### 2b. 3/4 push-in (diner's view)

| Field | Value |
|---|---|
| Composition | Plate on the lower-middle third line, its center at about 50 % height; the far rim and a glass or cup behind it fill the upper third (judgement); the 45 deg angle is the seated diner's view [RA18][RA38 3:46] |
| Angle | 45 deg down (range 25 to 75, 45 the commercial default) [RA4]; RA5 shows 30, 45, 60 |
| Distance / lens | Start 45 to 50 cm, end 25 to 30 cm, 1x; or start 60 cm on 2x if the venue light is good (judgement within RA47 RA42) |
| Orientation | portrait |
| Start framing | Medium: whole plate plus a margin of table |
| End framing | Close: plate fills the width; or detail of the best texture (judgement) |
| Move | Push-in by moving the phone, never by zoom [RA21][RA33 3:03]; elbows on the table, slide the forearms or lean from the hips; 20 cm in 3 to 4 s, about 5 to 7 cm/s (judgement) |
| Reads as cinematic | Slow push reveals texture and builds emphasis [RA18][RA17 "slower is more cinematic"] |
| Common mistakes | Pinch zoom; wide lens close to the rim makes the plate look like it slides off the table [RA4]; moving too fast [RA17] |
| Feasibility | Seated, two hands, elbows on the table: easiest moving variant (judgement) |
| Props | A drink behind the plate, a napkin to one side |

### 2c. Orbit (and the turntable alternative)

| Field | Value |
|---|---|
| Composition | Plate centered and constant in size, with a background that has depth (a wall, a window, other tables) so the parallax shows [RA15][RA16] |
| Angle | 30 to 45 deg down (judgement; no reference gives the orbit pitch for food) |
| Distance / lens | Radius 30 to 40 cm, 1x, constant [RA17 constant distance] (radius is judgement) |
| Orientation | portrait |
| Start framing | Close, plate a little off one side |
| End framing | Close, same size, plate centered |
| Move | Arc of 30 to 45 deg in 4 s around the plate, forearms on the table swinging as a unit (judgement); real orbit makes the background shear, which is the proof of an orbit [RA16][RA15] |
| Turntable alternative | Phone still, turn the plate (or a saucer under the cup) slowly by 90 deg [RA16][RA35 0:35]; background stays still; no parallax [RA15] |
| Reads as cinematic | Parallax behind a steady subject [RA15] |
| Common mistakes | Changing the radius mid-arc [RA17]; orbiting while something happens on the plate (cutting, pouring) [RA18]; too large an arc for one person (judgement) |
| Feasibility | Seated with elbows on the table: 30 deg OK; 90 deg needs standing and stepping, not first-timer (judgement) |
| Props | None in the arc path; a glass at the far side gives parallax |

Disagreement: RA15 and RA16 treat a turntable as a lesser substitute (no parallax), while Schiffer's commercial
opens with "basic turntable shots" [RA35 0:35]. For a first-timer the turntable is the more repeatable version
(judgement).

### 2d. Napkin or slider slide (reveal from behind, lateral slide)

No reference names a napkin-slide food reveal. Built from: foreground reveal from behind an object [RA17][RA50],
hero products sliding into frame [RA19], low hero slider moves [RA50], low handheld on a table [RA13].

| Field | Value |
|---|---|
| Composition | Plate at center height in the clear box; a near blocker (folded napkin standing up, menu card, cup) 5 to 15 cm in front of the lens covers half the frame at the start (judgement after RA50); background behind the plate |
| Angle | 0 to 15 deg down, lens near the table (judgement) |
| Distance / lens | Plate 30 to 40 cm from the lens, 1x (judgement) |
| Orientation | portrait upside down when the phone rests and slides on the table (lens 1 to 3 cm up, at plate height) [RA5][RA7]; portrait alternative: hold the phone with its top edge 3 to 5 cm above the table, slight down pitch (judgement) |
| Start framing | Blocker fills half or more of the frame, out of focus |
| End framing | Medium: plate fully visible, sharp |
| Move | Option A, camera slides: truck 15 to 20 cm sideways along the table edge in 3 to 4 s, about 5 cm/s, phone resting on the table under the fingertips (judgement). Option B, prop slides: phone still, a hand pulls the napkin out of frame sideways (judgement) |
| Reads as cinematic | Something close slides away and the dish is there; parallax between blocker and plate [RA50][RA17] |
| Common mistakes | Rushing the reveal [RA17]; blocker too far from the lens so it never fills the frame (judgement after RA50); autofocus hunting on the blocker; lock focus on the plate first [RA23] |
| Feasibility | Seated, one hand on the phone, one on the napkin (option B) or both on the phone (option A): feasible (judgement) |
| Props | Napkin, menu card, a cup as the blocker |

### 2e. Most repeatable plate reveals (easiest first)

1. Turntable: phone still at 45 deg, turn the plate 90 deg by hand (no camera move) [RA16][RA35].
2. Napkin pull, option B: phone still, hand pulls the napkin away (judgement).
3. 3/4 push-in 20 cm with elbows on the table [RA4][RA21].
4. Overhead rise from 25 to 50 cm, standing [RA21][RA5].
5. Real orbit of 30 deg around the plate [RA15][RA17].

## 3. Pour

### 3a. Coffee pour (espresso or filter into a cup, carafe into a cup)

References: RA8, RA14, RA18, RA20, RA28 (7:29), RA30 (1:41), RA36 (6:01), RA37.

| Field | Value |
|---|---|
| Composition | Cup on the lower third line, spout or carafe entering from the top edge; for espresso the portafilter spout is visible at the top of the frame [RA8]; dark wall behind if there is steam [RA8] |
| Angle | 45 deg down into the cup for espresso [RA8]; eye level or slightly low for pour-over [RA8] |
| Distance / lens | 25 to 35 cm, 1x [RA8] (distance judgement) |
| Orientation | portrait for 45 deg; portrait upside down for a low eye-level pour with a short cup (lens at cup height, judgement) |
| Start framing | Close: cup plus the stream entering from the top |
| End framing | Same (static) |
| Move | Static; the liquid moves [RA18 "let the action carry"]; 3 to 6 s; the pour itself is shot continuously and the best part chosen later [RA20] |
| Reads as cinematic | Stream backlit or side lit [RA18]; slow-down from 60 or 120 fps [RA27][RA14] |
| Common mistakes | Exposure on the white saucer; crema waited on too long (dies within 30 s) [RA8]; flicker in slow-mo under room lights [RA48] |
| Feasibility | Seated: the visitor holds the phone, the barista or a friend pours, or the visitor pours from a carafe with the other hand (judgement) |
| Props | Saucer, spoon, carafe or milk jug |

### 3b. Latte art (pour and finished pattern)

References: RA8, RA14, RA36, RA37, plus the general overhead rules RA4, RA22, RA23.

| Field | Value |
|---|---|
| Composition | Pour: cup centered low, jug from upper right (judgement). Finished art: cup centered in the clear box, handle at 4 or 8 o'clock, saucer and spoon visible [RA8 for overhead]; white cup gives the most contrast, glossy black reflects the ceiling [RA8] |
| Angle | Pour 45 deg [RA8 espresso]; finished art 90 deg, lens parallel [RA8] |
| Distance / lens | 20 to 30 cm, 1x [RA8] (distance judgement) |
| Orientation | portrait |
| Start framing | Pour: close on cup and jug spout. Art: close, cup fills about half the width |
| End framing | Art: same, or a 10 cm rise to show the saucer (judgement) |
| Move | Static; the art is shot after the cup is set down, pouring and shooting at once gives a blurry hand [RA8]; window for sharpest contrast about 30 s, 15 s for plant milk [RA8] |
| Reads as cinematic | The pattern grows inside a still frame (judgement) |
| Common mistakes | HDR on (flattens foam contrast) [RA8]; ultra-wide makes the cup oval [RA8]; own shadow from directly overhead [RA23] |
| Feasibility | Visitor: finished art only, seated, phone held flat over the cup with elbows on the table [RA8 brace elbows]. Filming the pour needs the barista's cooperation (judgement) |
| Props | Saucer, spoon, a pastry at the edge |

Disagreement: RA8 films the espresso stream at 45 deg but the finished art at 90 deg; the search summaries
suggest filming the pour at 45 and cutting to 90 for the pattern [RA54]. No reference gives a single angle for the
latte pour itself.

### 3c. Beer or cocktail pour

References: RA26, RA41, RA42, RA43, RA52, RA14 (move with the subject).

| Field | Value |
|---|---|
| Composition | Glass on the vertical center line, rim at about 40 % height so the stream enters from above inside the clear box (judgement); dark or mid-tone background, light behind [RA42][RA43] |
| Angle | Stemmed or layered glass: 0 deg at the liquid line [RA42]; highball: 30 to 45 deg down [RA42]; bartender pour: over the shoulder or eye level [RA43] |
| Distance / lens | 35 to 50 cm on 2x [RA42]; main lens for beer [RA43] (distances judgement) |
| Orientation | portrait upside down when the liquid line is under 12 cm from the table (coupe, lowball, a pint on a low table) so the lens sits at the liquid line [RA42 0 deg][RA7] (judgement on the 12 cm threshold); portrait for highballs (30 to 45 deg down) and for standing bartender pours |
| Start framing | Close: empty or iced glass and the bottle or shaker entering from the top |
| End framing | Same; head or garnish complete |
| Move | Static [RA42 order: empty glass, ice, pour, garnish]; beer: glass tilted 45 deg, poured on the side, straightened halfway [RA43]; 4 to 6 s (judgement) |
| Reads as cinematic | Backlight through the liquid, key at 10 to 11 o'clock behind and above [RA42][RA43]; a thin rim highlight kept [RA42] |
| Common mistakes | Top light alone (beer goes opaque) [RA43]; fingerprints under raking light [RA42]; own reflection in the glass (use a dark flag or clothing) [RA42]; wide lens crowding the rim into an oval [RA42] |
| Feasibility | The visitor rarely pours; the bartender pours while the visitor films seated at the bar or table (judgement). Foam lasts under 60 s [RA43], so frame on the empty glass first [RA42][RA52] |
| Props | Coaster, garnish, bottle |

### 3d. Most repeatable pours (easiest first)

1. Static 45 deg on a coffee cup while someone else pours, phone braced on the table [RA8].
2. Static 90 deg on finished latte art, set the cup down first [RA8].
3. Visitor pours from a carafe or bottle with one hand, phone in the other at 45 deg (judgement).
4. Upside-down phone at the liquid line of a cocktail or beer, bartender pours [RA42][RA7].
5. Slow-mo pour at 120 fps by a window [RA27][RA48].

## 4. Steam and hot drink on the table

References: RA8, RA9, RA10, RA11, RA18, RA28 (5:37), RA32.

| Field | Value |
|---|---|
| Composition | Cup or bowl at center height in the clear box with the dark part of the room behind it (dark wall, dark corner); the light source (window) behind and to one side [RA9][RA10][RA11 0:46]; empty space above the cup for the steam to rise into, which doubles as the caption band (judgement) |
| Angle | 0 to 20 deg down, close to eye level with the cup (judgement; RA9 gives no camera angle, but steam is seen against the background only from a low angle) |
| Distance / lens | 25 to 35 cm, 1x (judgement) |
| Orientation | portrait upside down for a small cup on the table (lens at the rim, about 5 to 8 cm up) (judgement after RA5 RA7); portrait for a bowl or a tall mug held at 10 to 20 deg down |
| Start framing | Close: cup in the lower half, top half dark background |
| End framing | Same (static), or a 10 cm push (judgement) |
| Move | Static, 3 to 4 s; film at once, steam is gone within seconds [RA9] |
| Light | Back or side-back: 10 to 11 or 1 to 2 o'clock with the camera at 6 [RA9]; "backlight it on a dark background" [RA10]; turn off house lights over the table [RA32 0:41] |
| Reads as cinematic | White wisps lit against black [RA9][RA10][RA18] |
| Common mistakes | Light background [RA9]; front light (no wisps) [RA9][RA32 2:36]; waiting too long [RA9]; showing the steam source [RA9] |
| Feasibility | Seated, phone braced on the table edge or against a sugar pot, one hand: easy. Requires the drink to be fresh (judgement) |
| Props | Allowed in a venue: a hot refill, the saucer, a spoon. Not allowed for visitors: hidden microwaved pads, garment steamers [RA9][RA10] (these are studio cheats) |

Most repeatable (easiest first):
1. Freshly served cup, phone upside down at the rim, window behind the cup (judgement after RA9).
2. Same in portrait, 15 deg down, dark wall behind (judgement).
3. A spoon stirred once to lift fresh steam, static (judgement).
4. Bowl from 30 deg with a backlight from a window (judgement after RA9).

## 5. First bite

References: RA14, RA19, RA20, RA25, RA31 (0:47), RA39, RA44, RA45. Evidence is thin; no reference gives framing
numbers for an eating shot.

### 5a. Selfie (front camera, held by the eater)

| Field | Value |
|---|---|
| Composition | Face in the upper half, eyes near the upper third line (y about 640 px, inside the 290 px top margin) (judgement); fork or bite enters from the lower edge; the plate edge visible at the bottom inside the bottom 35 % is acceptable because it is context, not the hero (judgement) |
| Angle | Lens at eye level, 0 to 10 deg down [RA45 eye level][RA44 eye-level selfie] |
| Distance / lens | Arm's length, 40 to 50 cm, front camera at its default (judgement) |
| Orientation | portrait |
| Start framing | Medium close: head and shoulders, fork rising |
| End framing | Same; reaction after the bite |
| Move | Static; 4 to 6 s: 1 s look at the food, bite, 2 s reaction (judgement); one continuous take, no edit inside the moment [RA25] |
| Reads as cinematic | Unscripted reaction, over-scripting is the named mistake [RA25]; window light on the face [RA44] |
| Common mistakes | Same framing for every shot [RA44]; mixed window and warm lamp light [RA44]; scripted enthusiasm [RA25] |
| Feasibility | One hand holds the phone, one the fork: possible but the phone drifts while chewing (judgement); better propped against a glass or the menu (judgement) |
| Props | Fork or spoon; napkin |

### 5b. Filmed by a friend (rear camera)

| Field | Value |
|---|---|
| Composition | Eater medium close, face upper third, plate in the lower third; friend sits across the table (judgement) |
| Angle | Eye level, 0 to 10 deg [RA45] |
| Distance / lens | 60 to 90 cm across the table, 1x or 2x (judgement) |
| Orientation | portrait |
| Start framing | Medium: eater and plate |
| End framing | Close on the face after the bite, via a 15 to 20 cm push (judgement) or static |
| Move | Static or slow push-in [RA21 dolly]; 4 to 6 s (judgement) |
| Reads as cinematic | Background blur from distance or Cinematic mode (judgement); the bite as the payoff, hands rather than faces is also a valid style [RA20] |
| Common mistakes | Filming the bite off camera when the script wants a reaction (RA19 ends recipe videos with a bite off camera, which is the opposite choice); framing changed mid-take [RA25] |
| Feasibility | Seated friend, two hands, elbows on the table: easy |
| Props | Fork, the dish |

### 5c. Variant: food-only first bite (no face)

Fork lifts a bite out of the plate toward the lens, plate at 45 deg, phone static or a 10 cm pull back (judgement;
"a hand diving in with a fork" [RA53], a dish with bites taken [RA20], POV angle [RA31 0:47]
[RA39]). Orientation: portrait. This needs no face and suits shy visitors (judgement).

Most repeatable (easiest first):
1. Food-only: fork lifts a bite out of the dish toward the lens, phone static at 45 deg (judgement after RA20).
2. Friend films across the table, static, eye level [RA45].
3. Selfie with the phone propped against a glass, eye level (judgement).
4. Hand-held selfie, one hand (judgement).

Disagreement: recipe videographers tend to keep the eater off camera (bite off camera [RA19], hands not faces
[RA20]); UGC and review guidance puts the face and reaction at the center [RA25][RA44].

## 6. First sip

References: RA8, RA25, RA42, RA44, RA45, RA14 (move with the subject). No reference covers a sip shot directly.

| Field | Value |
|---|---|
| Composition | Face in the upper half; cup rises from the lower third into the face; the cup's logo or art turned to the lens (judgement) |
| Angle | Eye level [RA45] |
| Distance / lens | Selfie 40 to 50 cm front camera; friend 60 to 90 cm, 1x or 2x (judgement) |
| Orientation | portrait |
| Start framing | Medium close: face plus the cup on the table or in hand |
| End framing | Same; reaction after lowering the cup |
| Move | Static, 4 to 5 s (judgement); the cup is the moving element, rising at the speed a person naturally drinks |
| Reads as cinematic | Window light on the face [RA44]; steam or latte art seen before the sip (link to section 3b or 4, judgement) |
| Common mistakes | Cup hides the whole face for the full take (judgement); exposure on a white cup [RA8] |
| Feasibility | Selfie: one hand on the phone, one on the cup, feasible; friend: easy (judgement) |
| Props | Cup with saucer; glass |

Variant, cup-only sip (no face): phone static at 45 deg on the cup, hand lifts it out of frame upward, the saucer
remains (judgement). Most repeatable (easiest first): cup-only lift; friend filming; propped selfie; hand-held
selfie (judgement).

## 7. Menu card on the table

References: RA40 (menu is one of five essential restaurant b-roll shots), RA51 (menu placed on the table beside
the dish in a first-timer shot list), RA4, RA5, RA8 (chalkboard menu straight on), RA17 (overhead sweep).
No reference gives menu framing; the spec is built from flat-object rules.

| Field | Value |
|---|---|
| Composition | Menu card fills the clear box diagonally or straight; the venue name or one dish name sits in the clear box, not in the bottom 35 % (judgement from RA2); a cup or the dish at the upper-left corner as context [RA51] |
| Angle | 90 deg overhead for a flat card (flat objects read best overhead [RA4]); 45 deg for a card in a stand (judgement); straight on for a chalkboard [RA8] |
| Distance / lens | 25 to 35 cm, 1x (judgement) |
| Orientation | portrait (a standing card in a holder at table level can be shot portrait upside down for a 0 deg view, judgement) |
| Start framing | Close on the name or the logo |
| End framing | Medium: whole card plus the cup |
| Move | Pedestal up 15 cm in 3 s or a hand opens the folded menu while the phone is still (judgement after RA21 pedestal) |
| Reads as cinematic | Clean single subject; side light shows paper texture (judgement after RA18 side light) |
| Common mistakes | Glare on laminated cards (tilt 15 deg off the light axis, by analogy with foil bags [RA8]); text in the bottom UI band (judgement from RA2); tilted phone over a flat card [RA5] |
| Feasibility | Seated, both hands: easy |
| Props | Cup, cutlery |

Most repeatable (easiest first): static overhead of the card with the cup; hand opens the menu (static phone);
overhead rise from the name to the whole card; slow lateral slide along a standing card at table level (portrait
upside down).

## 8. Hand-off (cup or plate served to you)

References: RA19 (hero slides into frame), RA20 (hands), RA31 (0:47 POV), RA39 (POV rig), RA5 (hands add context),
RA14 (move at the subject's speed to stay in focus). No reference covers a receiver-filmed hand-off; the search
found only stock clips of a plate slid onto a counter. All framing below is judgement.

| Field | Value |
|---|---|
| Composition | POV: the empty table spot centered in the lower half of the clear box; the server's hand and the cup enter from the top or the far side and set it on that spot; the visitor's own hand may enter from the lower edge to receive it (judgement after RA19 slide in, RA31 POV) |
| Angle | 45 deg down from the seated eye line, POV (judgement after RA31) |
| Distance / lens | 35 to 45 cm to the table spot, 1x (judgement) |
| Orientation | portrait |
| Start framing | Medium: empty spot, cutlery, napkin |
| End framing | Medium close: the served cup or plate centered |
| Move | Static while the server places it, then an optional 10 to 15 cm push in 2 s onto the dish (judgement); lock focus and exposure on the spot first so the hand entering does not change brightness [RA54][RA23] |
| Reads as cinematic | The arrival as a reveal: something enters an empty, prepared frame [RA19] |
| Common mistakes | Following the server's hand with the phone (motion and focus hunting) (judgement); the server's face filmed without consent (judgement) |
| Feasibility | Seated, phone in one hand braced on the table, the other hand free to receive: easy, needs the server to do it once (judgement) |
| Props | Napkin and cutlery laid out first |

Variant, counter hand-off at a takeaway cafe: phone at chest height, barista's hand passes the cup across the
counter toward the lens, visitor's hand takes it, the phone stays still (judgement after RA31 POV).

Most repeatable (easiest first): static POV on the table spot while the plate is set down; same with own hand
taking the cup; counter hand-off at chest height; served then push-in on the dish.

## 9. Watch list (for a visual check of the (judgement) values)

| Shot | Watch | Why |
|---|---|---|
| Overhead and table-level framing | RA38 0:55, 6:26, 8:22 | Scrivani on overhead, table level and vertical with an iPhone |
| POV and top-down rigs | RA31 0:47, 1:49, 2:53 | DoP shows POV, lay flat and side profile setups |
| Low shots below food | RA28 6:24, RA31 4:16 | Phone shots from below the food |
| Steam | RA11 0:46 to 8:22, RA28 5:37 | Background, light position, steam pour on a phone |
| Pour on phone | RA30 1:41, RA28 7:29, RA36 6:01 | Sauce and coffee pours filmed on phones |
| Turntable | RA35 0:35 | Turntable framing in a commercial |
| Phone stability, lens cover, through-glass | RA29 0:54, 3:54, 7:14 | Phone-only b-roll: grip, a lens-cover transition, shooting through glass |
| Move speed and focus | RA14 6:05, 7:07 | Handheld move at the subject's speed, ramp to center |
| Lens choice | RA33 1:21, 3:03; RA34 1:25 | Close vs far camera, no pinch zoom, longer lens |

## 10. Where references disagree (summary)

- Phone at 45 deg: avoid it [RA4] vs use it as the default diner view [RA18][RA38 3:46][RA19]. Resolution: use
  45 deg only with the phone 35 cm or more away on 2x, or 25 to 30 cm on 1x with the plate centered (judgement).
- Lens for drinks: main 1x [RA8][RA43] vs 2x/3x [RA42].
- Orbit vs turntable: orbit for parallax [RA15][RA17] vs turntable as the cleaner product spin [RA16][RA35]; do
  not orbit during action [RA18].
- Steam light: side-back clock positions [RA9] vs plain backlight [RA10]; both agree on a dark background.
- Handheld: jerky, use a tripod [RA19][RA20] vs fully handheld commercial b-roll [RA14][RA13].
- Eater on camera: off camera or hands only [RA19][RA20] vs face and reaction [RA25][RA44].

## 11. Orientation summary per shot

| Shot | Needs portrait upside down? | Why / portrait alternative |
|---|---|---|
| 2a overhead rise | No | Lens over the plate |
| 2b 3/4 push-in | No | Lens 20 cm or more above the table |
| 2c orbit | No | Pitch 30 to 45 deg |
| 2d napkin or slider slide | Yes when the phone rests and slides on the table | Lens at plate height [RA5][RA7]; alternative: portrait held with the top edge just above the table |
| 3a coffee pour | Only for a low eye-level pour | Alternative: 45 deg portrait [RA8] |
| 3b latte art | No | 90 deg or 45 deg |
| 3c beer or cocktail | Yes for glasses with the liquid line under about 12 cm | 0 deg at the liquid line [RA42]; alternative: portrait at 30 deg down, accepted for highballs [RA42] |
| 4 steam | Yes for a small cup | Lens at the rim against the dark background; alternative: portrait 15 deg down |
| 5 first bite, 6 first sip | No | Eye level |
| 7 menu card | Only for a standing card at 0 deg | Alternative: overhead portrait |
| 8 hand-off | No | POV from seated eye line |
| Tall dish hero (burger, stack, layered cake) | Yes | Straight-on and low read the layers [RA4][RA5]; alternative: portrait at 10 to 20 deg down from 30 cm |
