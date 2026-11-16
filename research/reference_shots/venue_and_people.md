# Reference shots, part B: venue and people

Scope: the shots a visitor films from the customer side of a cafe or restaurant. These are the entrance, the
menu board, ordering at the counter, the room from the table, the verdict to camera and the hook. Each spec is
written so a line-art guide can show three things: composition, camera angle and one move. References are in
`sources_venue_and_people.md` as RB1..RB53. [S..] and [F..] point to `../sources.md` from the earlier pass.
Values I derived myself are marked "(judgement)". Fetched on 2026-11-10.

## Evidence limits (read first)

- YouTube transcripts could not be read. For video references the evidence is the title, the description and
  the chapter list (`opened (meta)` in the sources file). A timestamp shows where in the video the technique is
  demonstrated. It does not quote what is said there. Before a guide is animated from one of these, someone
  should watch the chapter and confirm the framing (judgement).
- The hard numbers come from written primary or near-primary sources. Those are platform help pages and
  platform-funded research (RB1, RB2, RB5, RB8 to RB10), RED and PremiumBeat on panning (RB29, RB30), a
  peer-reviewed selfie-distortion model (RB19), DXOMARK lens specs (RB20) and Apple support (RB21, RB37).
- Hook research comes from ads (TikTok, Meta, Google). Applying it to organic visitor reels is a judgement.
- No source gives a camera height in centimetres or a pitch in degrees for these shots. All heights and angles
  below are judgement, anchored to body landmarks (eye, chest, table) that a guide can show.

## 0. Shared conventions used by every spec

### 0.1 The 9:16 frame and its UI-safe area (1080 x 1920)

| Zone | Value | Refs |
|---|---|---|
| Top band covered by UI | 14 to 15% (about 270 to 290 px) | RB3, RB4 |
| Bottom band covered by caption, handle and audio | 25 to 35% (480 to 672 px). TikTok: keep essential text out of the lowest quarter | RB3, RB4 |
| Right action rail | 10 to 15% (108 to 162 px). Meta's ad figure is 6%, and tools widen it to about 120 px | RB3, RB4 |
| Left margin | 6 to 10% | RB3, RB4 |
| Official TikTok position | No fixed pixels: the zone "is determined by the dimension, ad caption length and any additional formats". Templates only | RB2 |
| Working safe box for Loca guides | x 8% to 85%, y 15% to 65% of the frame. Faces, eyes, the sign and the hero object stay inside it, and text sits in its upper half (judgement, the intersection of RB3 and RB4) | judgement |

What this means for people: put the eyes at about one third from the top (y about 33%, 640 px) [RB15]. That
line sits inside the safe box with about 18% of clearance under the top UI band. Do not push the face right,
where the action rail competes with the eyes [RB3].

### 0.2 Phone lenses in a portrait frame

The frame width in portrait is the short side of the sensor. That is why portrait pans feel faster than
landscape pans.

| Lens button | Equivalent | Approx. horizontal view in portrait 9:16 | Use | Refs |
|---|---|---|---|---|
| 0.5x (rear ultra-wide) | 13 mm | about 78 degrees | Tight rooms, walk-and-talk, entrance in a narrow street. Faces and edges distort | RB18, RB23 |
| 1x (rear main) | 24 to 26 mm | about 44 to 47 degrees | Default for walking and for most venue shots. Best low-light quality | RB18, RB23 |
| 2x (rear crop or tele) | 48 to 52 mm | about 23 to 25 degrees | Menu board, counter detail, a friend filming a person. Straighter lines | RB33 |
| Front camera | 23 mm (20 mm on iPhone 17) | about 45 degrees (about 50 on iPhone 17) | Selfie verdict, walk-and-talk with feedback | RB20, RB21, RB22 |

The view angles are geometry from the equivalent focal length (judgement). Never change the zoom while
moving [RB23].

### 0.3 Phone orientation (owner request)

- **Portrait (normal)** is the default for every shot.
- **Portrait upside down** means the phone is flipped 180 degrees so the rear lens sits at the bottom edge.
  It is only needed when the lens must be lower than about 10 cm above a surface. Held normally and resting
  on its bottom edge, an iPhone's rear lens sits about 13 to 15 cm above the surface. Upside down it sits
  about 1 to 3 cm above (phone geometry, judgement).
- Evidence: Apple's education community recommends the upside-down hold for a "subject-level" low shot
  without kneeling, and notes that the image still displays upright [RB37]. Creative Bloq covers the same
  trick [RB39]. Both are written for stills. Video use is my extension (judgement). "Get low" is a standard
  phone B-roll chapter [RB35 2:15] but does not mention flipping.
- Implementation caution for Loca's own recorder: rotation values for upside-down capture differ by model,
  and the iPhone 17 front camera reports 180 degrees [RB38]. The app must rotate or tag the clip itself and
  must flip the guide overlay (judgement).
- The front camera upside down puts the lens at the bottom of the screen. The person then looks down at the
  lens and the face is shot from below. Never use it for selfies (judgement).

Shots that need upside down to work, with the portrait alternative:

| Shot | Why upside down | Portrait alternative |
|---|---|---|
| A3 ground-level walk-in (lens at shoe height, filming feet and the threshold) | The lens must sit 2 to 5 cm above the floor while you walk | Crouch-walk with the phone at knee height and the top edge tilted down 10 to 15 degrees. It reads "low" but not "ground" (judgement) |
| D2 reveal from behind a cup at table level (lens level with the cup rim or below it) | The lens must be under about 8 cm above the table | Rest the phone on a saucer or a folded napkin and accept a 30 to 40 degree high angle. Or reveal from behind a taller object such as a bottle, vase or plant |
| C3 counter slide (lens skimming the counter top, a cup or tray in the foreground) | The lens must be under about 5 cm above the counter | Hold the phone 15 cm above the counter, pitched 15 to 20 degrees down |
| All other shots (entrance at chest height, menu board, OTS at the counter, room pan, verdict) | Not needed | Portrait normal |

### 0.4 Walking technique (shared by A, C and any walk-and-talk)

- Ninja walk: knees slightly bent, heel-to-toe rolling steps, short strides, head and torso at one height
  [RB23, RB24, RB25 3:00].
- Constant speed, no stop-start [RB25 3:25]. Slow down for key shots [RB23]. Slow walking speed is about
  0.5 to 0.8 m/s against a normal 1.3 m/s (judgement).
- Two hands, elbows against the ribs, arms never locked straight. For vertical video, one hand supports the
  bottom of the phone [RB23].
- Turn with shoulders, hips and feet as one unit, never with the wrist [RB23] [S10].
- Keep clips to about 5 s and take several [RB23]. Stay on the main 1x lens for walking. Use 0.5x only in
  good light [RB23] [S31].
- Never walk backwards while watching the screen [S10]. Any pull-out at room scale is replaced with a pan or a
  foreground reveal (judgement, as in the earlier pass).

### 0.5 Pan speed (shared by A, D)

- Cinema rule: no faster than one full frame width every 7 s at 24 fps [RB29]. Example: a 45-degree pan on a
  35 mm lens should take at least 8 s [RB30]. A wider view can pan faster, and higher frame rates reduce
  judder [RB29].
- Translated to a portrait phone frame at 1x (about 45 degrees wide), that is about 6 to 7 degrees per second
  at 24 fps. At 30 fps with stabilisation, up to about 10 degrees per second is my working ceiling (judgement
  from RB29). At 0.5x (about 78 degrees) the ceiling roughly doubles, to about 15 to 20 degrees per second.
- This **disagrees with the earlier pass**: `commercial_shots.md` sets pans at 15 to 30 degrees per second,
  which is 2 to 4 times RED's limit at 1x. Recommendation: room pans at 1x go 8 to 10 degrees per second (45
  degrees in about 5 s), or 0.5x at 15 degrees per second. Faster turns are treated as whips, not pans
  (judgement).
- DXOMARK also notes slight judder when panning on the iPhone front camera [RB20]. Do not pan the selfie
  camera.

---

## A. Entrance and arrival

### References

| ID | What it shows |
|---|---|
| RB31 | Through-the-door in-camera transition (Mango Street video, via No Film School): push in until the door fills the frame, open it, keep moving through. Fill the frame fully with the door so there is a cut point |
| RB53 | Two walking options (Filmora short, 14 s): the camera tracks the walking subject, or the camera holds still and the subject walks into or out of frame |
| RB25 | Handheld moves without a gimbal: 3:00 the walk, 3:25 constant speed, 3:40 dolly in, 4:21 dolly and tilt (the sign-to-door tilt), 5:10 slow push-in |
| RB26 | 3:02 the POV shot, 3:43 walking handheld, 4:00 tracking. Shot ideas for filming in public |
| RB52 | Storefront rules from Google Maps: show the whole business name, shoot while standing still, start straight-on or from the sidewalk approach |
| RB45 | Cafe reels built from storefront and exterior, then the interior. Example: a 10-s reel of storefront, parking spot and pickup zone |
| RB14 | The 3-Cut POV Review opens with a 3-s walk-in exterior |
| RB13 | Disagrees: never open on the establishing shot of the restaurant |

### Spec

| Field | Value | Refs |
|---|---|---|
| Variants | A1 sign-to-door tilt (static feet, tilt down). A2 POV walk-in through the door (push). A3 ground-level walk-in (feet and threshold). A4 friend films you walking in (static camera, subject enters) | RB25, RB31, RB53 |
| Composition, start | A1: the sign fills the top half of the safe box, name fully readable, nothing cut [RB52]. A2: the door centred and filling about 50% of frame height at 3 to 4 m [RB31] (distance judgement). A3: the threshold line in the lower third, shoes entering from the bottom edge (judgement). A4: the door frame fills the frame, empty for 1 s before the person enters [RB53] | RB31, RB52, RB53 |
| Composition, end | A1: the open door centred, handle height about 55% down the frame (judgement). A2: the door fills the frame edge to edge (the cut point) or the room interior opens up [RB31]. A4: the person's back fills about 40% of the frame as they go through | RB31 |
| Eye line / people | Other people stay out of frame or are seen from behind. Do not linger on a passer-by [RB41]. In A4 the subject's head stays below the top UI band (top of head lower than y 15%) | RB41, RB3 |
| 9:16 safe area | The sign name sits between y 15% and 45%. Nothing important sits in the bottom 30%, where the caption covers the threshold | RB3, RB4 |
| Camera height and angle | A1: chest height (about 130 cm), starting 20 to 30 degrees up at the sign and ending at 0 degrees on the door. A2: chest or eye height, 0 degrees, horizon level. A3: lens 2 to 5 cm above the ground, 5 to 10 degrees up. A4: chest height, 0 degrees | judgement (RB37 for A3) |
| Distance and lens | A1: 4 to 8 m from the facade at 1x. Use 0.5x only if the sign does not fit. A2: start 3 to 5 m out at 1x, never zoom [RB23]. A3: 1x, because 0.5x makes the ground rush (judgement). A4: friend 3 to 4 m inside or outside at 1x | RB23, RB18 |
| Move, speed, duration | A1: tilt down 20 to 30 degrees over 3 to 4 s (about 8 degrees per second) [RB25 4:21]. A2: walk at 0.5 to 0.8 m/s for 3 to 5 s and cut as the door fills the frame [RB31]. A3: the same walk for 3 s. A4: static for 3 to 5 s while the subject crosses [RB53] | RB25, RB31, RB53, judgement on speeds |
| Walking technique | Ninja walk, two hands, elbows in, constant speed (section 0.4). Opening the door: keep the phone in the right hand at the sternum and push the door with the left hand or shoulder. Cut before the hand crosses the lens, or let it cross as the wipe [RB31] (hand detail judgement) | RB23, RB24, RB25 |
| Phone orientation | A1, A2, A4: portrait. A3: portrait upside down (section 0.3). Portrait alternative for A3: crouch at knee height, top edge tilted down | RB37 |
| What makes it cinematic | One clean continuous move ending on a cut point (door filling the frame). Level horizon. A steady pace. Exposure locked before the push so the brightness jump at the door does not pump [RB25 2:35, RB35 1:03] | RB25, RB31, RB35 |
| Common mistakes | Pinch-zooming into the door. A wrist pan to "find" the door. Walking fast (bounce). The sign cut off. A busy street of faces. Opening the reel on this shot (see disagreement) | RB23, RB52, RB13 |
| Feasibility, solo | A1 and A2 are easy. A3 is medium (you walk blind, so the guide must keep it 3 s and straight). Door handling is the main risk | judgement |
| Feasibility, friend | A4 is the easiest with a friend. The friend stands still and only frames the door | RB53 |
| Visitor-side constraints | Public pavement only. Do not block the door or other customers. Staff seen through the glass count as people [RB41]. Film when the door is clear | RB41 |

### Where the references disagree

- Opening on the entrance: NomNomad's 3-cut review opens with a 3-s walk-in [RB14], while Blitzcut says the
  establishing shot never goes first [RB13]. TikTok research also finds outdoor shoots score 26% lower [RB8].
  Resolution (judgement): the entrance is step 2 or a 1.5-s bridge after the hook, never frame one. Allow it
  as the opener only if it carries a spoken hook line or a place-name caption in the first 2 s [RB13].

### Most repeatable variants (easiest first)

1. A1 sign-to-door tilt: standing still, one hinge of the elbows, 3 s.
2. A4 friend static, you walk in: the friend does nothing but hold still.
3. A2 POV push to the door, cutting before you open it: 3 s straight walk with no door handling.
4. A2 full push-through with the door opened: adds the hand and the brightness change.
5. A3 ground-level walk-in, upside down: needs the flip and walking blind.

---

## B. Menu board at the counter

### References

| ID | What it shows |
|---|---|
| RB51 | Flat glossy boards: glare comes from lights reflected into the lens. Stay parallel at the board's centre height to avoid keystoning. No flash. Step back to fit the board |
| RB13 | Text-heavy menu frames get skipped, so say the dish instead of showing the menu |
| RB1 | On-screen reading pace: 5 to 10 words per second |
| RB33 | Cafe interiors shot on a 2x tele: compression and straight lines inside a coffee shop |
| RB45 | Cafe reels that end on a counter sign (a pickup sign as the hero of the counter shot) |
| RB25 | 5:58 slider move by hand (a sideways truck along a surface) |
| [S7] / earlier `rail-truck` | Truck along a shelf or board with a foreground object for parallax |

### Spec

| Field | Value | Refs |
|---|---|---|
| Variants | B1 static hold, straight-on. B2 truck along the board left to right. B3 tilt down from the board to the pastry case or counter | RB25, RB51 |
| Composition, start | B1: the board fills the safe box width (x 8 to 85%), its top edge just under y 15%. B2: the first column of the board at frame centre and the board's edge entering from the right. B3: the board's lower half at the top of the frame | RB51, RB3 |
| Composition, end | B2: the last column at centre. B3: the case or counter front fills the lower two thirds | judgement |
| Eye line / people | Board edges parallel to the frame edges, not converging [RB51]. Staff behind the counter are out of frame or seen from behind [RB41] | RB51, RB41 |
| 9:16 safe area | The prices and names you want readable sit between y 15% and 65%. Do not put a caption over the board, because the board already is text [RB13] | RB3, RB13 |
| Camera height and angle | Lens at the board's centre height where you can reach it. Most boards hang above head height, so step back until the pitch is 10 degrees up or less. That reduces keystoning more than tilting does [RB51] (distances judgement) | RB51 |
| Distance and lens | 2 to 3 m back at 2x (straight lines, less keystone) or 1.5 m at 1x. Never 0.5x, which bends edges [RB18, RB23] | RB33, judgement |
| Move, speed, duration | B1: static 2 s. B2: truck 10 to 15 cm per second for 3 to 4 s (a sidestep or a slide along the counter edge). B3: tilt down 20 to 30 degrees over 3 s | earlier rail-truck, judgement |
| Walking technique | B2 is a sidestep with soft knees, shoulders square to the board and phone at chest height. Or slide both hands along the counter edge | [S10], judgement |
| Phone orientation | Portrait. No case needs upside down | section 0.3 |
| What makes it cinematic | Lines perfectly parallel. Board lit evenly with no hotspot. Exposure locked on the board, not on a bright window [RB35 1:03]. 2x compression [RB33] | RB33, RB35, RB51 |
| Common mistakes | Shooting from directly underneath (keystone). A light hotspot across the prices. Flash. Holding the board for 5 s or more (a skipped frame [RB13]). Reading the menu aloud | RB13, RB51 |
| Feasibility, solo | Very easy | judgement |
| Feasibility, friend | Not needed | judgement |
| Visitor-side constraints | Film while not holding up the queue (judgement). Stand on the customer side of the counter. Staff under the board may object [RB42] | RB42 |

### Where the references disagree

- Blitzcut drops menu frames entirely [RB13]. Cafe guides and the earlier pass keep the board as a context
  shot [RB45] [F-coffee walk-in tour]. Resolution (judgement): keep it to 2 s or less and point at the one
  dish the voiceover names. Never use it as the hook.

### Most repeatable variants

1. B1 static straight-on at 2x, 2 s.
2. B3 tilt from the board down to the case, 3 s.
3. B2 truck along the board, sliding along the counter edge.

---

## C. Ordering at the counter

### References

| ID | What it shows |
|---|---|
| RB40 | OTS framing: near head and shoulder in the foreground, out of focus. Do not block the subject's face. Medium lens. Focus on the far subject |
| RB26 | 4:43 over the shoulder, 3:02 POV, from a guide to filming yourself in public |
| RB15 | Foreground framing (doorway, furniture) for depth, without overdoing it |
| RB41 | Ask staff first. They may say "just don't show me". Film from behind |
| RB42 | A customer filming a counter worker was refused service |
| RB32 | Frame match on a coffee cup: cut as the cup is grabbed or set down |
| [F19] | Cafe hook: the customer's hand receiving the cup (POV), from the earlier pass |
| RB9 | Product in action raises attention by 31% |

### Spec

| Field | Value | Refs |
|---|---|---|
| Variants | C1 POV hand receives the cup or tray (staff hand only). C2 friend films over your shoulder as you order. C3 slide along the counter top past a cup or tray (low). C4 POV over your own shoulder to the counter, phone held back at the shoulder | RB26, RB40, [F19] |
| Composition, start | C1: the counter edge across the lower third and an empty hand space in the centre. C2: your shoulder and the back of your head fill the left or right 25 to 35% of the frame, out of focus, and the counter or barista area fills the rest [RB40]. C3: the foreground cup fills 30 to 50% of one side of the frame | RB40 |
| Composition, end | C1: the cup in your hand at the centre of the safe box (y about 45%). C2: a 3 to 5 s push brings the counter detail to about 50% of the frame. C3: the menu or the barista area at the centre | RB40, judgement |
| Eye line / people | The staff face is excluded unless they agree. Frame hands and cups [RB41]. In C2 the subject is the counter and the action, not the cashier's face. The foreground shoulder must not cover the hero [RB40] | RB40, RB41 |
| 9:16 safe area | The cup or hand sits between y 30% and 60%. The near shoulder can sit in the bottom-left. Keep it off the right rail | RB3 |
| Camera height and angle | C1: chest height, 20 to 30 degrees down. C2: the friend's lens at your shoulder height, 10 to 15 cm behind and 20 to 30 cm to the side, pitch 0 to 10 degrees down. C3: lens 2 to 5 cm above the counter, 0 to 5 degrees up. C4: phone at your ear height behind you, 15 to 20 degrees down | judgement |
| Distance and lens | C1: 1x, 40 to 60 cm to the hand. C2: 1x or 2x [RB40 "medium lens"]. 2x needs the friend 1.5 m back. C3: 1x (0.5x may switch to macro and jump, judgement). C4: 0.5x so both the shoulder and the counter fit | RB40, judgement |
| Move, speed, duration | C1: static, the hand enters (3 s). Cut on the grab [RB32]. C2: slow push-in of 20 to 30 cm over 3 to 5 s, or static. C3: truck 5 to 10 cm per second for 3 s. C4: static | RB32, earlier counter-over-shoulder |
| Walking technique | None. Brace your elbows on the counter for C1 and C3 | [S10] |
| Phone orientation | C1, C2, C4: portrait. C3: portrait upside down for the skim. Portrait alternative: 15 cm above the counter, pitched 15 to 20 degrees down (section 0.3) | RB37 |
| What makes it cinematic | Foreground depth (blurred shoulder or cup) [RB40, RB15]. Cut on the grab [RB32]. Real action: the cup being handed over [RB9] | RB9, RB15, RB32, RB40 |
| Common mistakes | Filming the cashier's face or the card terminal screen (judgement). Shoulder covering the action [RB40]. Too wide, so the whole queue is in frame. Holding up the order | RB40, RB41 |
| Feasibility, solo | C1 easy (one hand films, one takes the cup, so put the cup down first if needed). C3 medium. C4 awkward | judgement |
| Feasibility, friend | C2 is the natural friend shot | RB40 |
| Visitor-side constraints | Customer side of the counter only. No behind-the-bar shots. Ask the barista first [RB41]. Do not film the payment screen (judgement). Refusal risk is real [RB42] | RB41, RB42 |

### Where the references disagree

- The earlier pass describes `counter-over-shoulder` as standing behind the barista (staff side). That is
  outside visitor scope. Here OTS is always over the visitor's own shoulder or a friend's [RB40].

### Most repeatable variants

1. C1 POV hand receives the cup: static, 3 s, cut on the grab.
2. C2 friend over your shoulder, static.
3. C2 with a slow push-in.
4. C3 counter-top slide (upside down or the 15 cm alternative).
5. C4 your own shoulder POV (awkward grip, rarely worth it).

---

## D. Room from the table

### References

| ID | What it shows |
|---|---|
| RB29 | Pan limit: one frame width per 7 s at 24 fps. A wider view can pan faster |
| RB30 | A 45-degree pan needs at least 8 s on a 35 mm lens |
| RB48 | A restaurant shoot from a corner booth in an operating venue: slow moves or pans for the room |
| RB44 | Wides when the venue is in full swing. Talent enjoying the room |
| RB46 | Panoramic interior with named spaces as text callouts |
| RB41 | Film the atmosphere, not a particular guest. Do not linger on a person |
| RB31 / [S21] | Foreground wipe: fill the frame fully with the blocker. A closer blocker gives a faster wipe |
| RB15 | Foreground framing (furniture) for depth |
| RB35 | 3:36 let the action happen (static, the room moves). 1:03 lock focus and exposure |

### Spec

| Field | Value | Refs |
|---|---|---|
| Variants | D1 static wide from the seat (people move, the camera does not). D2 reveal from behind a cup, plant or bottle (truck sideways). D3 slow pan across the room. D4 tilt up from the table to the room | RB31, RB35, RB48 |
| Composition, start | D1: horizon (eye level of seated guests) at about y 40%, the longest view of the room on the diagonal. D2: the blocker fills the frame fully, out of focus [RB31]. D3: a wall, window or the bar at one edge. D4: your cup or plate in the lower half | RB15, RB31 |
| Composition, end | D2: the room or bar sharp, with the blocker gone off one side. D3: the opposite feature (window, bar, lights) at about 1/3 width. D4: the room with your table edge as foreground at the bottom (judgement) | RB31 |
| Eye line / people | Guests seen as atmosphere: backs, profiles, out of focus. Never a lingering face [RB41]. Cinematic mode or a shallow depth of field helps in busy spots [RB41] | RB41 |
| 9:16 safe area | Ceiling lights stay in the top band. The table edge or foreground sits at the bottom (it may sit under captions). The room's hero feature sits between y 20% and 60% | RB3 |
| Camera height and angle | Seated table height: lens about 110 to 120 cm off the floor (eye height of a seated adult), pitch 0 to 5 degrees. D2 at table level: lens 5 to 10 cm above the table, level | judgement |
| Distance and lens | D1, D3: 0.5x in small rooms (fits more and allows a faster pan [RB29]) or 1x in large rooms [RB18]. D2: 1x with the blocker 5 to 15 cm from the lens [S21]. Exposure and focus locked on the room before the reveal [RB35 1:03] | RB18, RB29, RB35 |
| Move, speed, duration | D1: static 3 to 4 s. D2: sideways truck 10 to 20 cm per second, 3 to 4 s, blocker out by second 2. D3: 45 degrees in 5 to 6 s at 1x (8 degrees per second) or 60 degrees in 4 s at 0.5x (15 degrees per second) [RB29, RB30]. D4: tilt up 30 degrees over 3 to 4 s | RB29, RB30, earlier pass |
| Walking technique | None. Seated: elbows on the table, rotate from the torso for pans, never the wrist [RB23] | RB23 |
| Phone orientation | D1, D3, D4: portrait. D2 with a short blocker (a cup): portrait upside down. With a tall blocker (bottle, plant, vase): portrait (section 0.3) | RB37 |
| What makes it cinematic | Depth layers: your table in front, guests in the middle, the window or bar behind [RB15]. Real motion in a still frame (D1) [RB35 3:36]. A full-frame blocker [RB31]. A pan slow enough not to judder [RB29] | RB15, RB29, RB31, RB35 |
| Common mistakes | Pans at whip speed (the earlier pass's 15 to 30 degrees per second at 1x is over RED's limit). An empty room (shoot at a busy hour [RB44]). One guest's face filling the frame. Exposure pumping when the window enters the pan | RB29, RB41, RB44 |
| Feasibility, solo | All four are easy seated. D2 needs a blocker on the table | judgement |
| Feasibility, friend | The friend can be the foreground subject in D1, seen from behind or in profile | RB15 |
| Visitor-side constraints | Film only from your own table. Do not stand on furniture or move other tables. Many venues ban photographing other customers (see RB41 and the search summary on house rules) | RB41 |

### Where the references disagree

- Pan speed: RED's 7-s rule [RB29] against the earlier pass's 15 to 30 degrees per second. Section 0.5 resolves
  this as 8 to 10 degrees per second at 1x.
- People in the room: Kepayang says keep faces out [RB41], while promo guides want the venue full and lively
  [RB44]. Resolution: full room, nobody identifiable for long (judgement).

### Most repeatable variants

1. D1 static wide, elbows on the table, 3 s.
2. D4 tilt up from your plate to the room.
3. D2 reveal from behind a bottle or plant (portrait).
4. D3 slow pan at 0.5x.
5. D2 reveal from behind a cup at table level (upside down).

---

## E. Verdict / talking to camera

### References

| ID | What it shows |
|---|---|
| RB19 | Selfie distortion: at about 30 cm the nasal base looks 30% wider than at 1.5 m. 1.5 m is a proportional portrait distance |
| RB20 | iPhone front camera: 23 mm, fixed focus, good for vlogging. Tested at 30, 55, 90 and 120 cm. Faces at 120 cm go soft. Judder on pans |
| RB21, RB22 | iPhone 17 Center Stage front camera: 20 mm, auto widen and auto rotate |
| RB15 | Eyes on the top third line. Show neck or shoulders. Look room. Nothing growing out of the head |
| RB16 | Centred with "roughly a third of empty space above your head" (disagrees with RB15) |
| RB18 | Rear 1x looks better, while the selfie camera suits spontaneous walk-and-talk. Leave headroom for the platform crop |
| RB28 | Selfie camera is "much worse" than the main camera for a talking head (description) |
| RB27 | 0:40 using the right camera, 4:47 composition |
| RB26 | 5:23 talking head |
| RB8 | Direct-to-camera talking head lifts 2-s view-through by 14%. Everyday people hook better |
| RB9 | A greeting lifts recall by 112%. Saying "you" in the first 5 s helps |
| RB50 | Keith Lee: films himself in his car, opens with "I got it, let's try it, and rate it one through 10", scores each dish |
| RB14 | Verdict cut of 4 s with a location tag, last in the 3-cut review |

### Spec

| Field | Value | Refs |
|---|---|---|
| Variants | E1 seated selfie at arm's length (front camera). E2 friend films across the table (rear 1x or 2x). E3 walk-and-talk selfie out of the door. E4 phone propped on the table against a cup or bottle (rear or front) | RB18, RB26, RB50 |
| Composition | Eyes on the top-third line (y about 33%) [RB15]. Head and shoulders, with the top of the shoulders at about y 55 to 60% and the hero dish or cup raised into the frame at chest level (y 50 to 65%) (judgement). Face centred horizontally, or offset left with look room right if the eyes turn to the dish [RB15]. Never offset right, where the rail sits [RB3] | RB3, RB15 |
| Headroom | Small: 5 to 10% of frame height above the head, with the head top below the top UI band (y 15%) (judgement reconciling RB15 and RB16). Leave a little extra for the platform crop [RB18] | RB15, RB16, RB18 |
| Background | Into the room (lights, bar, other tables out of focus), not a blank wall. Nothing growing out of the head [RB15]. No strong window directly behind, or the face goes dark (search summary; judgement) | RB15 |
| 9:16 safe area | The face occupies y 15 to 50%. The mouth must stay above the bottom 35% caption band. A caption is fine below the chin | RB3, RB4 |
| Camera height and angle | E1: lens at eye height or 5 to 10 cm above, pitch 5 to 10 degrees down at the face (search summary from a Canon vlogging guide: eye level or slightly above; degrees are judgement). E2: lens at the subject's eye height, 0 degrees | RB17, judgement |
| Distance and lens | E1: full arm's length, about 55 to 65 cm (judgement). This halves the 30 cm distortion RB19 measured, though it is still short of 1.5 m. Front camera at its widest (23 mm, or 20 mm on iPhone 17 [RB20, RB22]). Do not tap the selfie zoom to 1x close up (judgement). E2: friend 1.2 to 1.5 m away at 1x, or 2.5 m at 2x. That is distortion-free [RB19] and uses the better camera [RB18, RB28] | RB18, RB19, RB20, RB22, RB28 |
| Move, speed, duration | Static, 4 to 6 s for 8 to 14 words. The only movement is the person raising the dish or cup into frame. E3: walk at 0.5 m/s with the arm locked at the elbow, never panning the selfie camera [RB20] | RB14, RB20, earlier pass |
| Walking technique (E3) | Arm bent at about 120 degrees, elbow against the ribs, phone at eye height. Ninja walk. The face stays at the same spot in the frame | RB23, RB24 |
| Phone orientation | Portrait for all. Never upside down for the front camera (section 0.3). E4 propped on a cup: portrait leaning back 5 to 10 degrees. Because the lens is at the top, the propped phone films from a natural height | section 0.3 |
| What makes it cinematic | Eye contact with the lens, not the screen (search summary). Background depth. A short line with a number ("8 out of 10") [RB50]. Saying "you" early [RB9]. Real reaction | RB8, RB9, RB50 |
| Common mistakes | Phone 30 cm from the face (nose 30% wider [RB19]). Shooting up the nose from below. Face pushed into the right rail or under the top band. Looking at yourself on the screen instead of the lens. Long preamble ("hi guys") [RB12, RB13] | RB3, RB12, RB13, RB19 |
| Feasibility, solo | E1 easy. E4 easy with a prop. E3 medium | judgement |
| Feasibility, friend | E2 is the best quality: rear camera at proper distance | RB18, RB19 |
| Visitor-side constraints | Speak quietly, because other diners are recorded in audio too (search summary on wiretap law). Keep other guests' faces soft behind you [RB41]. Keith Lee films in his car to stay anonymous and avoid disturbing service [RB50]. Outside or in the car is a valid fallback | RB41, RB50 |

### Where the references disagree

- Eye position: eyes on the top third [RB15] against centred with a third of empty space above the head
  [RB16]. RB16 puts the eyes near the middle of the frame. Resolution: RB15's top third, which also clears the
  9:16 bottom band. RB16's extra headroom only suits a later crop.
- Camera choice: rear camera for quality [RB18, RB28] against front camera for feedback and walk-and-talk
  [RB18]. Resolution: solo verdict uses the front camera, friend verdict uses the rear camera.

### Most repeatable variants

1. E1 seated selfie at full arm's length, dish raised into frame, 5 s.
2. E4 phone propped against a cup or bottle, rear camera, sitting back.
3. E2 friend films across the table at 1x.
4. E3 walk-and-talk selfie leaving the venue.

---

## F. The hook (first 1 to 2 seconds)

### References

| ID | What it shows |
|---|---|
| RB1 | Proposition in the first 3 s, hook within 6 s, people on camera, text at 5 to 10 words per second |
| RB10 | 47% of a video's value lands in the first 3 s and 74% by 10 s (Facebook) |
| RB7 | Skip rate counts the views lost in the first 3 s. Mosseri: "the first three seconds ... super important" |
| RB5, RB6 | Open on a bold statement, a surprising visual or a question. Trim slow starts. Viewers leaving at 4 s means the hook needs work |
| RB8 | Everyday people hook 1.7x better than celebrities. Direct-to-camera lifts 2-s view-through by 14%. A logo on screen lowers 6-s view-through by 14% |
| RB9 | A person shown early raises hooking power by 50%. Saying "you" in the first 5 s lifts purchase intent |
| RB11 | Tight framing on people or product at the start, more than two shots in the first 5 s (search) |
| RB12 | Hook from the very first second, no rambling, open on a teaser or highlight |
| RB13 | Frame one is the most appetising frame. Name the location within 2 s. Sound-only first second. No establishing shot |
| RB14 | Disagrees: the walk-in exterior opens the 3-cut review |

### Spec

| Field | Value | Refs |
|---|---|---|
| What fills frame one | One of: (H1) the hero dish or drink in tight close-up with motion (pour, steam, cut), (H2) the visitor's face mid-reaction or mid-sentence to camera, (H3) the payoff teased: a flash of the best moment, then a cut back. Never the logo, the facade alone or a menu board | RB8, RB11, RB12, RB13 |
| Framing | Tight. The subject fills 50 to 80% of the safe box [RB11]. For H2 the face framing follows E, but closer: eyes at y 30 to 33% and the chin at about y 55% (judgement) | RB11, RB15 |
| Words | First spoken or caption line within 1 s. It names the place or the claim within 2 s [RB13] and addresses "you" [RB9]. Caption at 5 to 10 words per second [RB1], placed in the upper half of the safe box | RB1, RB9, RB13 |
| Camera height, angle and lens | Inherited from the shot it borrows: H1 food close-up (part A file), H2 = E1 or E2, H3 = any | cross-reference |
| Move, speed, duration | 1 to 2 s. Either motion in the subject (pour, bite, reaction) or one fast camera move (push-in or whip) into the next shot. Cut by 2 s. More than two shots in the first 5 s [RB11] | RB11, RB13 |
| Phone orientation | Inherited. An H1 pour at table level can need upside down (section 0.3) | section 0.3 |
| What makes it work | A person, and better a direct look at the lens [RB8, RB9]. An immediate payoff. Location stated early [RB13]. Sound of the food in the first second [RB13] | RB8, RB9, RB13 |
| Common mistakes | "Hi guys, today I'm at..." [RB12]. A slow establishing shot [RB13]. A logo opener [RB8]. A text wall | RB8, RB12, RB13 |
| Feasibility | Every hook is a re-cut of a shot filmed later in the visit, so the guide can record the hook last (judgement). The person filming does not need to get it in order | judgement |
| Visitor-side constraints | A face-first hook needs the visitor's own face. Never use a staff or guest face as the hook [RB41] | RB41 |

### Where the references disagree

- Hook length: 1 to 2 s [RB12, RB13], 3 s [RB1, RB7, RB10], 6 s [RB1, RB8, RB9]. The numbers measure
  different things: first frame, proposition and the end of the hook window. Loca rule: frame one carries the
  hook, the claim lands by 2 s, and the reason to stay is clear by 6 s (judgement).
- Opening on the walk-in: RB14 against RB13 and RB8 (see A).
- Lo-fi against polish: TikTok favours a DIY look [RB1], but high-impact sound, text and transitions still
  help [RB9]. No conflict for Loca: a phone-made look with clean framing.

### Most repeatable variants

1. H2 selfie verdict line moved to the front ("8 out of 10 and here is why"): recorded at the end, edited to
   frame one.
2. H1 pour or steam close-up with the place name as a caption.
3. H3 one-second flash of the first bite, then cut back.
4. A walk-in opener with a spoken hook line in the first second (the only acceptable entrance hook).

---

## Summary of cross-cutting findings

1. Pan speed in the earlier pass is too fast for 1x. Use 8 to 10 degrees per second, or move to 0.5x
   [RB29, RB30].
2. The verdict selfie at full arm's length (55 to 65 cm) halves the distortion of a typical 30 cm selfie.
   A friend at 1.5 m with the rear camera is distortion-free [RB19].
3. Eyes at one third from the top fit the 9:16 safe area. The face stays between y 15% and 50%, clear of the
   right rail [RB3, RB15].
4. Upside down is needed only for lens heights under about 10 cm: ground walk-in, a cup-level reveal and a
   counter skim. Every one has a portrait fallback [RB37].
5. The entrance is a bridge shot, not frame one, unless it carries a spoken hook [RB8, RB13].
6. Visitor scope: no staff faces without a yes, no other guests' faces lingering, no payment screens
   [RB41, RB42].

## Gaps

- No video transcript was read. Timestamped chapters (RB25, RB26, RB27, RB35) should be watched before the
  guides are animated.
- No primary source gives centimetre heights or degree angles for any of these shots. All are judgement.
- No hospitality-ad cinematographer breakdown with readable text was found. The professional references (RB47,
  RB48) are metadata only.
- Meta's safe-zone page could not be read. The 14/35/6 figures are secondary [RB4].
