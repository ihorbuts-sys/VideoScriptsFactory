# food-review-table: Review a spread

## Guided v0 (2026-11-10, p0/tasks/09)

Story: You show the whole table from above, catch the food cooking, explain how ordering works, take the first bite and give the price per person.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| spread | dining, fast-food | complex | silent opening over the spread | table_spread_orbit, pancake_clear_path | - | (none) | (none) | The whole table from above, every plate in frame. |
| action | dining, fast-food | easy | a hold while the food cooks; the creator can talk | (none) | grill_low_hold, plate_moment_low_hold | The {menuItem.name} just hit the grill. Listen to that. | {menuItem.name} | The food cooking or being served, close and low. |
| how | dining, fast-food | easy | how ordering works, said over a slow pan | room_seated_pan | table_talk_front | Here's how ordering works and what comes to the table. | How it works | The table and the room, while you explain how ordering works. |
| bite | dining, fast-food | easy | the reaction | bite_selfie_eye, bite_pip_dish, bite_friend_three_quarter | - | First bite of the {menuItem.name}. Okay, that is good. | First bite | You taking the first bite, your face and the food in frame. |
| verdict | dining, fast-food | easy | price per person | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | {menuItem.price} per person at {venue.name}. Worth it with friends. | {menuItem.price} per person | You, looking at the lens, saying the price per person. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.


Kinds: dining, fast-food. `featuresMenuItem: true`. 5 steps, 26 s.
Review kinds covered: shared tables (KPOT hot pot and Korean BBQ, La Fruta Feliz parrilladas, Lucky Robot's
tasting for two) and breakfast and brunch (9 venues: chilaquiles, migas, benedicts, pancakes, breakfast tacos).

## Idea
Some orders are the whole table. Show it from above, the sizzle or the yolk, how ordering works, the bite, and
the price per person.

## Audience moment
A group planning a dinner or a brunch. "How does it work" (all you can eat, cook it yourself, a set for two)
and the price per person decide it.

## Why this order
1. `spread`: flat-lay-reveal, the whole table is the hook.
2. `action`: the sizzle on the grill, the dip in the broth, the yolk or the syrup.
3. `how`: the format explained, both cameras on.
4. `bite`: the first bite.
5. `verdict`: price per person.

## Shot plan as a sequence
- `spread`: flat-lay-reveal, top-down, detail to wide pull-out. Cut low.
- `action`: hero-push at grill height, close to detail. Pull-back-reveal: the next shot starts on the same
  detail.
- `how`: eye-level, detail to wide pull-out until the creator and the table are in frame.
- `bite`: front camera, medium to close; the camera flips.
- `verdict`: arm's length from slightly above (high), static, friends in frame only if they agree.

## Notes
- flat-lay-reveal is "phone hard" (commercial_shots.md): the direction asks the creator to stand and rise
  slowly; the AI edit can trim a shaky start.

## Alternatives considered
- Separate breakfast and hot pot scripts: the shape is the same (spread, action, how, bite, price).
