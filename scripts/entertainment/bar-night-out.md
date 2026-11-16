# bar-night-out: Night out

Kinds: entertainment. `featuresMenuItem: false`. 5 steps, 25 s. Night-out family.
Kept from the kit catalog (was `craft-beer`, which is now an alias of `entertainment`). Step ids kept:
`crowd`, `pour`, `cheers`, `outro`; one step added (`hook`).

## Idea
A first round at a bar: the pour, the creator saying where they are, the room, cheers with friends, and an
invite that names the place and its happy hour or pint price.

## Audience moment
Someone deciding where to go tonight or this weekend, scrolling with friends in a group chat. They want to see
the room at the hour they would go, what a drink looks like and costs, and whether it suits their group.

## Why these steps in this order
1. `pour`: moved to the front. The best-practice notes say start on a lit drink, never on a dark room; the pour
   is the bar staple hook (best_practices/entertainment.md, "Hooks").
2. `hook`: new. The old script had no spoken line until the end; a face and a line inside 6 s is the platform
   rule. The glass from the pour carries into the selfie.
3. `crowd`: the room and the crowd are the product for this kind, shown wide and without close faces.
4. `cheers`: friends, one toast. One drink each; nothing that reads as heavy drinking.
5. `outro`: name, happy hour or pint price, neighborhood. The old line had 8 words in 4 s; it now says what
   the viewer needs to act on, in 6 s.

## Shot plan as a sequence
- `pour`: pour-detail, eye-level close, static with the phone braced on the bar. Match-cut on the glass.
- `hook`: selfie at arm's length, eye-level medium, static, the same glass now beside the face. Cut (camera flip).
- `crowd`: room-pan, eye-level wide, pan-right, ending in a whip.
- `cheers`: enters on the whip, low angle from the table edge, medium, static while the glasses meet. Cut.
- `outro`: static selfie at arm's length. End card.
Deliberate transitions: match-cut and whip (2).

## Changes from the kit version
- Totals were 13 s; now 25 s. Each just-film step was 3 s; now 4 to 5 s so the move can finish.
- Old overlays (`crowd_high_angle`, `tap_pour_glass`, ...) are cleared; the guides agent refills them.
- `crowd` is eye-level, not the old high angle: a high angle over a crowd films strangers' faces from above
  and is hard to hold in a packed room.

## Alternatives considered
- Crowd first (the old order): a dark wide room is the weakest possible first second.
- A dance-floor dutch shot for energy: one more move, and it puts strangers in close frames.
- Ordering a round of shots for the toast: excluded, the brief and the best practices rule out heavy drinking.
