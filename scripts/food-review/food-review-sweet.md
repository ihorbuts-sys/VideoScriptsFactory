# food-review-sweet: Review a pastry or dessert

## Guided v0 (2026-11-10, p0/tasks/09)

Story: You pick the {menuItem.name} from the case, show it close on the plate, take the first bite and give the price and when to come before it sells out.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| case | bakery, coffee, dining | easy | picking it, said aloud | (none) | case_slide_to_item, case_hold_shelf | Picking the {menuItem.name} from the case. | {menuItem.name} | The display case, ending on the one you are getting. |
| break | bakery, coffee, dining | complex | silent visual beat on the example plate (was tear or cut) | plate_high_orbit, plate_tissue_slide | plate_rise_overhead | (none) | (none) | The pastry on the plate, close enough to see the inside. |
| taste | bakery, coffee, dining | easy | the texture, said | bite_selfie_eye, bite_pip_dish, bite_friend_three_quarter | - | First bite of the {menuItem.name}. Here's the texture. | First bite | You taking the first bite, your face and the pastry in frame. |
| verdict | bakery, coffee, dining | easy | price and when to come | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | {menuItem.price} at {venue.name}. Come early, they sell out. | {menuItem.name} · {menuItem.price} | You, looking at the lens, saying the price and when to come. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.


Kinds: bakery, coffee, dining. `featuresMenuItem: true`. 4 steps, 20 s.
Review kinds covered: pastries and donuts (Angel Donuts and Treats, Mozart's: raised ring donuts, kolaches,
croissants, scones) and desserts (14 of 17 venues: tortes, carrot cake, macarons, helados, brownies).

## Idea
A pastry is chosen at the case and proven by its inside. Show the case, break it open, taste it, and say the
price with a tip on when to come before it sells out.

## Audience moment
A weekend morning, someone choosing a bakery or a dessert stop. The inside (layers, filling, crumb) decides it.

## Why this order
1. `case`: a full case reads as fresh and plentiful; the pick is the hook.
2. `break`: the cross-section, the proof (cut-reveal).
3. `taste`: texture and sweetness in plain words.
4. `verdict`: price and the sell-out tip.

## Shot plan as a sequence
- `case`: eye-level at shelf height, medium to close push-in on the one pastry. Push-through: the next shot
  starts filled with the same pastry on the plate.
- `break`: cut-reveal from a high angle, close to detail, as it is torn open. Cut, camera flips.
- `taste`: sip-reaction shape on the front camera.
- `verdict`: static selfie.

## Alternatives considered
- rail-truck along the case: a sideways slide plus a stop is two moves; one slow push-in keeps it to one move.
- Opening on the break: stronger in the first second, but the push-through from the case needs the case first.
