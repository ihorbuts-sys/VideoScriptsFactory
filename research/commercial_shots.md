# Commercial shots: the vocabulary of the shot plan

Purpose: define every token used in `scripts/shot_plan.json` precisely enough that the script researcher can
chain steps and the guide author can animate them. Sources are in `sources.md` as [S1]..[S35]. Lines marked
(judgement) are my own reasoning, not a source claim; numbers without a source (speeds, distances) are judgement.

Vocabulary note: the README lists moves as `pan`, `tilt`, `truck`, `orbit` without direction and adds
`rack-focus-stand-in`. This file uses the directional tokens fixed by the task (`pan-left`, `pan-right`,
`tilt-up`, `tilt-down`, `truck-left`, `truck-right`, `orbit-left`, `orbit-right`) and does not define
`rack-focus-stand-in`. The shot plan author should reconcile the README with this list (judgement).

Conventions used below (judgement, chosen to be measurable by the live guide):
- Directions are the camera's, seen from behind the phone: `pan-left` turns the lens to the left; `truck-left`
  slides the phone to the left; `orbit-left` walks the phone to the left around the subject, so the subject's
  right side (from the viewer) comes into view.
- Framing is the size of the main subject in a 9:16 frame: `wide` = subject plus its surroundings, subject under a
  third of frame height; `medium` = subject fills a third to two thirds; `close` = subject fills the frame edge to
  edge; `detail` = one part of the subject (foam, crumb, label, scissor tips) fills the frame.
- A shot of 2 to 8 s, as the kit allows. Speeds are given per second so the guide's faster/slower cue has a target.

## 1. Angles

The camera height and pitch relative to the subject. Commercial food work treats the angle as the first decision
because it decides what part of the product reads: top, side, or both [S9].

| Angle | Definition | What it says | Suits | Distance and lens | Phone notes |
|---|---|---|---|---|---|
| eye-level | Lens at the subject's own height, pitch near 0 deg. For a dish: lens level with the plate rim ("straight-on" [S9]). For a person: lens at their eyes | Neutral, honest, "this is what it is" | Tall food (burger, layer cake, stacked pancakes, sandwich) where the side shows the layers [S9]; drinks in a glass; storefront; shelf face; a person talking | Dish 30 to 50 cm; person 1 to 1.5 m | Rest the phone on the table edge or a stack of saucers for food; phone vertical, horizon level |
| low | Lens below the subject looking up, 10 to 30 deg pitch up | Size, importance, "hero" [S7][S9] | Burger, tall drink, cake on a stand, sign above a door, a stylist standing behind a chair | Dish 20 to 40 cm, lens just above the table; facade 3 to 8 m | Phone upside down (lens at the bottom edge) gets the lens closest to the table (judgement); watch ceiling lights in frame |
| high | Lens above the subject looking down 30 to 60 deg; the "3/4" or 45 deg angle of food photography [S9] | The diner's view; shows top and sides together; the safe default for plated food [S9] | Plated mains, bowls, pastries in a case, latte art in a cup still on the saucer, hands at a counter, a client in a salon chair | 40 to 70 cm, 2x lens where possible [S19][S20] | Phone wide lenses distort a 3/4 dish; step back and use 2x or 3x via the lens button, not pinch [S20] |
| top-down | Lens pointing straight down at 90 deg, sensor parallel to the table | Pattern, layout, "the spread" [S9][S14] | Pizza, flat-lays, table spreads, bowls with toppings, latte art, nails on a hand, a menu or receipt; avoid layered food [S9] | 40 to 80 cm above the table; whole spread needs a chair | Straight-down distorts least on a phone [S20]; stand up and hold the phone at chest height with elbows on the ribs; keep your shadow out of frame (judgement) |
| over-shoulder | Lens behind and just above a person's shoulder, their shoulder or head soft at a frame edge, looking at what they look at or work on | Participation: "you are standing where the barista stands" | Barista at the machine, chef at the pass, stylist at the mirror, cashier, customer looking at a shelf | 30 to 60 cm behind the shoulder | Creator stands behind a staff member; needs the staff member's consent; ask them to repeat the action |
| dutch | Camera rolled 10 to 25 deg so verticals slant | Energy, playfulness, unease; impact fades with overuse [S27] | Geometric sets (glasses, citrus slices) [S9], neon signs, a dance-floor moment, a quick cutaway in a fast edit | Any | Roll the wrists, keep the subject centered; at most one dutch shot per ad (judgement) |
| pov | Lens at the creator's eye or chest height, pointing where the creator looks; hands may enter the frame | "This is you": walking in, picking, tasting | Door entry, menu pick, taking a cup across the counter, a first bite (fork rising to lens), walking an aisle | Hands at 30 to 50 cm | Phone at the sternum or at the eyes, elbows tucked; enter hands from below the frame edge (judgement) |

Subject-to-angle defaults (synthesis of [S9][S14][S20], judgement where unsourced):
- Dish: high for plated, top-down for flat, eye-level or low for tall. Drink: eye-level or low; top-down for latte
  art and foam. Pour: eye-level beside the glass, or over-shoulder of the pourer; top-down for pouring into a cup.
- Counter: eye-level wide from the customer side, or over-shoulder from the staff side. Storefront: eye-level from
  across the street, low for a sign. Product on a shelf: eye-level with the shelf, truck along it. Hands at work:
  high or top-down. A person: eye-level for speech, low for confidence, over-shoulder for work.

## 2. Moves

A move is what the camera body does during the shot. A zoom is not a push-in: a push changes perspective as the
camera advances, a zoom only magnifies the center [S22]. A truck keeps its distance to the subject, pans and tilts
are rotations that reveal new information [S28][S29]. Tabletop studios run moves on motion-control arms so the
move repeats exactly and stays in focus [S3]; home-studio food spots get the same "invisible hand" look from slider rigs [S2]; a phone creator substitutes body mechanics and short distances. Grip
rules that apply to every move: both hands, elbows against the ribs, arms not locked, turn the hips and feet rather
than the wrists, slow down, no zoom while moving, main lens rather than ultra-wide [S10][S11].

Speeds below are the target the guide should animate and cue (judgement, calibrated to 2 to 8 s steps and to a
phone held at arm's reach). "Must visibly change" is what the animation has to show so the move is understood
without text, as the README requires.

| Move | Speed and distance | Typical length | Must visibly change | One person with a phone | Feasibility |
|---|---|---|---|---|---|
| static | 0; phone does not move, the subject or hands act | 2 to 4 s (hook or end card), up to 6 s for a pour | Only the action in frame (pour fills, steam rises, hands work) | Brace elbows on the table or a wall, or lean the phone on a cup; 1 to 2 s of stillness before the action [S15] | phone OK |
| push-in | 10 to 15 cm/s near food (20 to 40 cm over 3 s); 30 to 50 cm/s on a facade or room (one slow step per second) | 3 to 5 s | Subject grows by about one framing step (medium to close, close to detail); background spreads and blurs | Food: elbows on the table, slide the forearms forward or lean the torso in from the hips. Room: ninja walk, short steps, heel to toe [S10] | phone OK up to 40 cm; phone hard for dolly-smooth slow pushes over 1 m |
| pull-out | Same speeds as push-in, reversed | 3 to 5 s | Subject shrinks one framing step; surroundings enter from all edges, revealing context | Lean back from the hips, or step backwards only after checking the floor; never walk backwards blind [S10] | phone OK short; phone hard walking backward |
| pan-left / pan-right | 15 to 30 deg/s; 45 to 90 deg over 3 s | 2 to 4 s | Scene slides across frame opposite to the turn; new things enter from the side the lens turns toward | Rotate hips and feet as one unit with the phone at the chest; never pivot the wrist [S10] | phone OK |
| tilt-up / tilt-down | 10 to 20 deg/s; 30 to 60 deg over 3 s | 2 to 4 s | tilt-down: the top of the frame leaves, what is below enters (sign down to door, glass rim down to coaster, face down to hands); tilt-up the reverse, often ending on a sign or a face | Hinge at the elbows with the forearms as a unit, or bend at the knees for low starts | phone OK |
| truck-left / truck-right | 5 to 15 cm/s near a counter or shelf; 30 to 50 cm/s along a facade or rail | 3 to 6 s | Foreground passes faster than background (parallax); subject keeps its size; a close foreground object gives depth [S7] | Sidestep with knees soft, phone at chest, shoulders square to the shelf; on a counter, slide the phone along the counter edge with both hands | phone OK on a surface; phone hard walking |
| orbit-left / orbit-right | 10 to 20 deg/s around the subject; 45 to 90 deg over 4 s at 30 to 60 cm radius | 3 to 5 s | The far side of the subject comes round; background sweeps behind the subject in the opposite direction; subject stays centered and the same size [S30] | Food: elbows on the table, swing both forearms around the plate in an arc, or turn the plate (a turntable "fake orbit"). Room scale: walk a quarter circle with crossed steps | phone OK under 45 deg at table scale; phone hard 90 deg plus; studios use a rotating arm at speed [S4] |
| whip | 300 deg/s or faster for 0.2 to 0.4 s; the image becomes motion blur | 0.3 s in the cut, plus 1 to 3 s of hold before it | The frame flicks; everything streaks in one direction | Hold the shot, then snap the hips and wrists together in one direction; stop dead on the next subject; repeat 3 takes [S8] | phone OK; stabilization and fast shutter in bright light reduce the blur [S8] (judgement on the phone detail) |
| reveal-from-behind | 10 to 20 cm/s sideways or forwards past a near object (pillar, plant, menu board, door frame, cup) | 3 to 5 s | First frames mostly blocked by an out-of-focus foreground; it slides off to one side and the subject appears sharp [S7][S21][S23] | Start with the lens 5 to 15 cm behind the blocker, then truck or push past it; closer blocker gives a faster, fuller wipe [S21] | phone OK |

Speed notes:
- Commercial push-ins on food are slower than a creator expects: tabletop rigs program small, precise motor steps for
  slow moves and reserve fast moves for pneumatic "explosive" action [S3]. The phone guide should lean slow; a push
  that runs out of distance in 2 s reads as a jolt (judgement).
- Every move needs a still head and tail of about 0.5 to 1 s so the editor has handles and the AI edit can cut on a
  settled frame [S15]. The guide's clock should include them (judgement).
- Rack focus (Cinematic mode) is a phone substitute for a pull-focus but records at 30 fps and is decided by depth
  data; it can be edited after capture [S35]. It is not a move token here.

## 3. Transitions (transitionOut)

`transitionOut` is a property of the outgoing step; it constrains how step N ends and how step N+1 starts. In-camera
transitions (whip, lens cover, object wipe, match cut) are the norm for Reels because the built-in editor
transitions are limited [S24]. TikTok explicitly recommends transitions to hold attention [S13].

### cut
- What it is: the plain edit. No constraint on the join beyond the chaining rules in section 5.
- Outgoing: any end framing; settle 0.5 s before the end so the cut lands on a still frame (judgement).
- Incoming: must differ from the outgoing in size and angle; at least 30 deg of camera position and a size step
  [S12]. Cutting inside a movement (the hand still rising, the door still opening) hides the cut further: match on
  action [S12][S26].
- Phone: phone OK.

### match-cut (same subject, new angle or size)
- What it is: the subject, or a shape in the same place in frame, carries across the cut while angle or size
  changes. Graphic match = shape, colour or movement aligned across the cut [S25]; match on action = a movement
  continued across the cut [S26].
- Outgoing: subject centered (or at a fixed third), ends still or mid-action. Note where the subject sits in frame.
- Incoming: the same subject in the same frame position, at a different size (close to detail) or angle (high to
  top-down), or a different object of the same shape (round cup rim to round plate, before-hair to after-hair).
- Examples: espresso cup from high close to top-down detail of the crema; client's head from behind before the cut,
  same head position after the cut finished [S16]; round pizza to round clock (judgement).
- Phone: phone OK if the guide shows a ghost of the last frame's subject position so the creator can line up the
  next start (judgement).

### whip
- What it is: the outgoing shot ends in a fast pan, the incoming shot begins in a fast pan in the same direction at
  the same speed; the cut is placed inside the blur [S8].
- Outgoing: hold the subject 1 to 3 s, then whip (usually `pan-right` or `pan-left`) out of it.
- Incoming: start mid-whip in the same direction, decelerate onto the new subject, hold.
- Constraints: same direction and speed; similar brightness and colour at the whip points, otherwise a short
  dissolve [S8]. Several takes in different directions give the editor choice [S8].
- Phone: phone OK. Two whips in a row, or more than two in an ad, read as a trick (judgement).

### push-through
- What it is: push into the subject until it fills the frame (a dark cup interior, a door, a dark jacket, a palm),
  cut, and start the next shot equally filled before pulling or pushing into the new scene. A cousin of the lens
  cover transition [S16][S24].
- Outgoing: push-in that ends on a frame filled by one dark or plain surface (detail framing, ideally out of focus).
- Incoming: starts filled by a similar surface (a door from the inside, the hand leaving the lens, a cup lifting away)
  and opens up with a push-in or pull-out.
- Examples: walk into the glass door, open inside the room; push into the black coffee, open on the next cup leaving
  the machine; stylist's cape over the lens, cape off on the finished look [S16].
- Phone: phone OK. Autofocus and exposure hunt on a filled frame; lock AE/AF on the subject before the push
  (judgement).

### pull-back-reveal
- What it is: the outgoing shot ends on a tight detail; the incoming shot (or the same shot) starts on a matching
  detail and pulls out to reveal the whole: plate, table, room, person. Combines a match-cut start with a pull-out.
- Outgoing: ends on detail of something that also exists in the reveal (a sauce drop, a logo, a scissor tip).
- Incoming: begins on that detail (or a matching one), pulls out to medium or wide.
- Examples: crumb detail to the whole bakery case; logo on the cup to the barista holding it; nail detail to the
  client's hand and face.
- Phone: phone OK when the pull is under 50 cm; walking backwards is phone hard (see moves).

## 4. Named patterns

Each pattern is one step (2 to 8 s). "Venue kinds" use the production slugs (README). Feasibility is for one person
holding a phone. Names in the brief list are kept; four extra patterns follow them.

| Pattern | Angle | Start | End | Move | Seconds | Best transitionOut | Subjects / venue kinds | Feasibility |
|---|---|---|---|---|---|---|---|---|
| hero-push | low | medium | close | push-in | 3 to 4 | cut or push-through | Signature dish, burger, cake, cocktail / dining, fast-food, bakery, food-truck, coffee | phone OK |
| flat-lay-reveal | top-down | close | wide | pull-out | 3 to 5 | cut | Table spread, pizza, brunch, pastry box, product layout / dining, bakery, shopping, beauty | phone hard (needs standing height and a still pull) |
| sign-tilt-down | low | medium | medium | tilt-down | 3 to 4 | push-through (into the door) or cut | Sign to door to people / every venue | phone OK |
| counter-over-shoulder | over-shoulder | medium | close | push-in | 3 to 5 | match-cut | Barista, cashier, chef at the pass, stylist at the station / coffee, bakery, dining, beauty-salon, services | phone OK |
| pour-detail | eye-level | close | close | static | 3 to 6 | match-cut or cut | Milk into espresso, beer from tap, sauce on a plate, syrup / coffee, food-and-drinks, dining, bakery | phone OK (slow-mo phone hard indoors, see section 6) |
| orbit-hero | high | close | close | orbit-left or orbit-right | 3 to 5 | cut | Plated dish, cake, product on a counter, finished hairstyle / dining, bakery, shopping, beauty-salon | phone OK under 45 deg, phone hard beyond |
| whip-between-details | high | detail | detail | static then whip | 2 to 3 | whip | Two neighbouring details: two cakes, two shelves, two nail colours / bakery, shopping, beauty | phone OK |
| door-push-through | eye-level (pov) | wide | detail (door) | push-in | 3 to 5 | push-through | Entrance / every venue with a door | phone OK |
| steam-hold | eye-level | close | close | static | 3 to 4 | cut | Hot soup, ramen, fresh bread, coffee, a hot towel at a barber / dining, coffee, bakery, beauty | phone OK (needs a dark background behind the steam, judgement) |
| cut-reveal | high | close | detail | push-in | 3 to 5 | match-cut | Knife through a cake, croissant, burger or roll showing the inside / bakery, dining, fast-food | phone OK |
| cheese-pull | eye-level | close | close | static or tilt-up | 3 to 5 | cut | Pizza slice, toastie, lasagne, mozzarella stick / dining, fast-food, food-truck | phone OK (commercial versions use motion-control robots and high speed [S5][S6]) |
| sip-reaction | eye-level | medium | close | push-in | 3 to 5 | cut | Creator or guest taking a sip or bite, then reacting / coffee, food-and-drinks, dining, bakery | phone OK on a table; selfie-held is phone hard |
| mirror-reveal | over-shoulder | medium | medium | static or pull-out | 3 to 5 | match-cut or pull-back-reveal | Salon client seeing the finished look in the mirror, outfit in a fitting-room mirror / beauty-salon, beauty, clothing-shops | phone OK (keep the phone out of the reflection) |
| rail-truck | eye-level | medium | medium | truck-left or truck-right | 4 to 6 | cut | Clothes rail, shelf, bakery case, menu board, records / clothing-shops, shopping, shopping-music, bakery | phone OK on a counter, phone hard walking |
| hands-at-work | high or top-down | close | close | static | 3 to 5 | match-cut | Latte art, dough shaping, cutting hair, manicure, wrapping a gift / coffee, bakery, beauty-salon, shopping, services | phone OK |
| before-after-match-cut | eye-level | medium | medium | static | 2 to 3 per half | match-cut | Haircut, nails, a room, an empty and a full plate / beauty-salon, beauty, services, dining | phone OK (subject must hold the same position [S16]) |
| facade-pull-back | eye-level | close (sign or window) | wide | pull-out | 3 to 5 | cut | Storefront establishing shot, often opener or closer / every venue | phone hard (backward walk); substitute push-in reversed in the edit (judgement) |
| pov-pick | pov | medium | close | push-in | 2 to 4 | cut | Hand reaches for a pastry, a shirt, a bottle, picks it up / bakery, shopping, clothing-shops, food-and-drinks | phone OK |
| foreground-reveal | eye-level | close (blocker) | medium | reveal-from-behind | 3 to 5 | cut | Plant, pillar or menu board slides away to reveal the room or the bar / dining, coffee, entertainment, recreational-other | phone OK |
| room-pan | eye-level | wide | wide | pan-left or pan-right | 3 to 4 | whip or cut | Interior, seating, crowd, gym floor / dining, entertainment, sport_health, recreational-other | phone OK |

"Reads" (what the viewer sees, one line per pattern):
- hero-push: the dish grows toward you from below until it towers over the frame.
- flat-lay-reveal: one plate from above, then the camera rises and the whole table appears around it.
- sign-tilt-down: the sign above, then the view drops to the open door below it.
- counter-over-shoulder: you stand behind the barista and lean in as the drink is made.
- pour-detail: milk falls into the cup and the pattern spreads, nothing else moves.
- orbit-hero: the plate turns past you, its far side coming round while the background slides behind.
- whip-between-details: one cake, a blur, the next cake.
- door-push-through: you walk up to the door until it fills the screen, then you are inside.
- steam-hold: a still bowl with steam curling up against a dark background.
- cut-reveal: a knife slices down and the inside opens toward you.
- cheese-pull: a slice lifts and the cheese stretches in long strands.
- sip-reaction: someone sips, the camera eases in, and the face answers.
- mirror-reveal: from behind the chair, the mirror shows the new look as the client sees it.
- rail-truck: shirts or loaves slide past at an even pace, the front ones faster than the back.
- hands-at-work: hands do the craft, filling the frame from above.
- before-after-match-cut: same pose, same place, and on the cut everything has changed.
- facade-pull-back: the sign, then the whole shopfront and the street around it.
- pov-pick: your hand reaches in and takes the one you want.
- foreground-reveal: something dark slides off and the room is there.
- room-pan: the room turns past you from one side to the other.

Pattern sourcing: hero low angle and push [S7][S9]; top-down for spreads [S9][S14]; hands-at-work, door, detail and
shoot-through categories [S15]; before/during/after with a consistent transition [S16]; pour and sizzle as the
motion that sells [S14]; robot orbit and drop shots as the commercial originals [S4][S6]; foreground reveal [S7][S21].
The remaining pattern definitions are synthesis (judgement).

## 5. Chaining rules

These rules say when step N's end pose is a sensible start for step N+1. They are written so a validator can check
`shot_plan.json` (judgement, grounded in [S12] where noted).

Size and angle:
1. Never two consecutive steps with the same `angle` and the same framing (N.end vs N+1.start) unless the
   transition is `match-cut` (where the change is in the subject, not the camera) or `whip` (the blur is the change).
   Grounded in the 30 degree rule and "change position and shot size together" [S12].
2. A plain `cut` needs at least one of: a framing step of two sizes (wide to close, medium to detail), or an angle
   change of at least two rows in this order: top-down, high, eye-level, low; over-shoulder, pov and dutch count as
   different from all the others. Best is both [S12].
3. Avoid wide straight to detail on a plain cut: put a medium or close in between, or use `pull-back-reveal` or
   `push-through` to bridge it (judgement, consistent with the long-to-mid-to-close progression [S12]).
4. Alternate moving and static steps; three moves of the same family in a row (three push-ins) flatten the edit
   (judgement). Static steps should carry action in frame (pour, cut, steam, hands).
5. Opposite moves back to back (push-in then pull-out on a cut, pan-left then pan-right) read as a hesitation unless
   the transition is `pull-back-reveal` (judgement).

Transition-specific joins:
- `push-through`: N.end = detail and must be filled; N+1.start = detail or close, filled, then opens. Usually
  N+1.move = pull-out or push-in.
- `pull-back-reveal`: N.end = detail; N+1.start = detail, N+1.end = medium or wide, N+1.move = pull-out.
- `match-cut`: N.end and N+1.start share the subject or its shape and its frame position; angle or size changes by
  at least one step.
- `whip`: N.move ends in whip, N+1 starts in a whip of the same direction; N.end and N+1.start framings are free but
  brightness should match [S8].
- `cut`: rules 1 to 3.

Pose continuity: if step N ends top-down and step N+1 starts low, the creator has to change body position between
takes; that is fine because steps are separate takes, but the guide must show the new start pose before recording
(README). Within the same take (no cut), poses must be reachable by the move (judgement).

How many deliberate transitions: a 25 to 40 s ad with 5 to 7 steps should use 1 to 2 named transitions (whip,
push-through, pull-back-reveal) and match-cuts where the subject allows; the rest are cuts (judgement). Hair
transformation reels use one repeated transition per stage [S16]; TikTok recommends transitions as attention tools
without a count [S13]. An in-camera transition early (first 5 s) is a common creator claim but unverified [S24].

Shot length by position (judgement within the kit's 2 to 8 s; TV-commercial shots averaged under 2 s by 1991 [S33],
and beat-cut tools default to about 2 beats per cut with sub-second cuts reading as busy [S34]; the AI edit can
shorten any step, so shoot longer than it plays [S15]):

| Position | Recorded length | Typical move | Notes |
|---|---|---|---|
| Hook (step 1) | 2 to 3 s | push-in, whip, cheese-pull, pour, door-push-through | The proposition must land in the first 3 s, the hook inside 6 s [S13]; start on the most appetising frame, not the facade |
| Middle (steps 2 to N-1) | 3 to 5 s | alternate static action and one move | Spoken steps (close, pip, selfie) need 4 to 6 s for 8 to 14 words |
| End (last step) | 3 to 5 s | static or slow pull-out, facade-pull-back, sip-reaction | Hold the last frame 1 s still for the outro card (judgement) |

Vertical framing: keep the subject inside the UI safe zone, away from the bottom caption band and the right-side
buttons [S13].

## 6. What a single creator cannot do well, and the phone substitute

| Commercial technique | Why it fails on a phone, one person | Substitute |
|---|---|---|
| Dolly-speed slow push over a metre or more (motion control, slider) [S3][S7] | Walking adds vertical bounce no stabilizer removes [S11]; slow walking drifts | Push of 20 to 40 cm with elbows on the table; or film a pull-out and reverse it in the edit (judgement) |
| Overhead slider or rig for top-down moves [S7] | Arms tire, horizon rolls, the creator's shadow falls on the food | Stand on a chair, phone at chest height, static top-down; animate with hands entering frame instead of the camera moving |
| High-speed pours, drops and splashes at 1000 fps [S4][S6] | Phone slow-mo is 120 or 240 fps [S32]; under 50/60 Hz lights it flickers, worse at higher fps, and cannot be fully removed [S17][S18] | Shoot slow-mo near a window or outside in daylight [S17]; prefer 120 fps over 240 [S17]; otherwise real-time pour at normal speed, let the edit slow a short section |
| Fast orbit around a glass (rotating arm) [S4] | One person cannot walk a smooth 90 to 180 deg arc at table radius | Orbit of 30 to 45 deg with forearms on the table, or turn the plate on a lazy Susan with the camera static |
| Cheese pull or burger drop timed by robots [S5][S6] | Needs a second pair of hands and repeatable timing | Creator's own hand pulls the slice while the phone rests on a cup; staff helps; repeat 3 takes |
| Parallax truck around a centered subject (curved slider) [S7] | Hard even on standard sliders [S7] | Straight truck along the counter edge with a foreground object; let the subject drift across the frame |
| Long-lens compression on food (70 mm plus) [S9] | Phone main lenses are wide and distort close food [S19][S20] | Use the 2x or 3x lens button, step back [S20]; top-down when only the wide lens exists |
| Shallow focus pulls | Phone video has deep focus outside Cinematic mode | Cinematic mode at 30 fps with tap-to-refocus [S35]; or macro detail where the background falls off naturally |
| Walking stabilization at speed | Action mode crops the ultra-wide, max 2.8K, noisy in low light [S31] | Use Action mode only for walk-ins in good light; otherwise short ninja-walk takes of about 5 s on the main lens [S10] |
| Controlled studio light (several LED panels as bright as possible) [S1] | Venue light is mixed and dim | Move the subject to the window, turn off overhead downlights over the table if allowed, shoot in the venue's brightest hour [S14] (last point judgement) |
| Backward walking pull-outs | Unsafe while watching the screen [S10] | Pull-outs only at table scale; room-scale reveals use reveal-from-behind or a pan instead |

Implications for the shot plan (judgement):
- Default every food step to table scale (under 50 cm of travel) and every room step to eye-level static, pan or a
  short walk-in. Reserve orbit and truck for steps where a surface supports the phone.
- Mark slow-mo intent only on pour, cheese-pull and steam steps, and only when daylight is likely; the AI edit should
  treat slow-mo as optional.
- Never require two people unless the step says so (cheese-pull and sip-reaction work best with a helper).
