# food-review-handheld: Review a burger or taco

## Guided v0 (2026-11-10, p0/tasks/09)

Story: You walk up to {venue.name} for the {menuItem.name}, show it close, take a two-hand first bite and say whether one is enough for {menuItem.price}.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| window | fast-food, dining, entertainment | easy | the hook spoken on the walk up | entrance_door_low, entrance_sign_tilt, entrance_walk_in | - | Lunch at {venue.name}. I'm here for the {menuItem.name}. | {venue.name} | The counter or the truck window, so people can find it. |
| cut | fast-food, dining, entertainment | complex | silent visual beat on the example plate (was pull apart) | plate_high_orbit, plate_tissue_slide | plate_rise_overhead | (none) | (none) | The food close up, so people see what is inside. |
| bite | fast-food, dining, entertainment | easy | the reaction | bite_selfie_eye, bite_pip_dish, bite_friend_three_quarter | - | Two hands for the {menuItem.name}. First bite. | First bite | You taking a big first bite, your face and the food in frame. |
| verdict | fast-food, dining, entertainment | easy | price and portion | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | {menuItem.price} at {venue.name}. Here's whether one is enough. | {menuItem.name} · {menuItem.price} | You, looking at the lens, saying the price and if it fills you up. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.


Kinds: fast-food, dining, entertainment. `featuresMenuItem: true`. 4 steps, 20 s.
Review kinds covered: handhelds (burgers, tacos, burritos, tortas, sandwiches; 7 venues) and pizza (Conans Pizza
North, KachCafe).

## Idea
A handheld is judged by its inside and by how messy it is. Walk up to the counter or truck, pull it apart for
the cross-section, take the two-hand bite, and give the price and whether one is enough.

## Audience moment
Lunch, quick, cheap. The viewer wants the size, the filling, the price, and whether there is a line.

## Why this order
1. `window`: the counter or truck and its menu board, so the viewer knows what kind of place it is.
2. `cut`: the cross-section or the cheese pull, the proof.
3. `bite`: the honest bite.
4. `verdict`: price and fullness.

## Shot plan as a sequence
- `window`: eye-level walk-up, wide to medium push-in. Whip down to the food in hand.
- `cut`: hero-push and cut-reveal combined, low and close: the halves come apart toward the lens (cheese-pull
  when there is cheese).
- `bite`: front camera, medium to close.
- `verdict`: static selfie with the truck behind.

## Alternatives considered
- Opening on the cut: stronger hook, but a food truck viewer first needs to know where it is; the window opens
  instead and the whip keeps the pace.
