# food-review: Food review (plates, bowls, starters)

## Guided v0 (2026-11-10, pilot for p0/tasks/09)

Story: you walk up to {venue.name}, order the {menuItem.name}, show it when it lands, take the first bite and say
whether it is worth {menuItem.price}.

Level rule used for every guide (`guides/p0/guide_levels.json`): **easy** when the creator can do it while talking
(a hold, or one steady walk, slide or tilt); **complex** when the camera needs their attention (an orbit, a prop, a
rise over a table). It follows the two Figma step examples (Arrive easy, The dish complex).

| # | Step | Level | Why | Guides (recommended first) | Camera | s |
|---|---|---|---|---|---|---|
| 1 | arrive | easy | The hook is spoken at the door: the place and the dish named in one breath; walking straight is easy to do while talking | entrance_door_low, entrance_sign_tilt, entrance_walk_in | back | 5 |
| 2 | order | easy | The dish's name said aloud is searchable speech; one even slide or tilt past the board | menu_board_truck, menu_board_tilt_up | back | 4 |
| 3 | dish | complex | The visual peak: silent, the orbit or the napkin slide needs the creator's attention; the editor labels it with the dish and price | plate_high_orbit, plate_tissue_slide (pending: plate_rise_overhead) | back | 5 |
| 4 | bite | easy | The reaction is the proof; the camera holds | bite_selfie_eye, bite_pip_dish, bite_friend_three_quarter | front (friend guide: back) | 5 |
| 5 | verdict | easy | Price, place and the call, to the lens | verdict_eye_level, verdict_high_plate, verdict_friend_eye | front (friend guide: back) | 6 |

Lines (2.5 words per second; a slot read as a two-word name) and the one caption per easy step, facts only:

| Step | line | caption | idea (shown with "No guide") |
|---|---|---|---|
| arrive | {venue.name}. I came here for one thing: the {menuItem.name}. | {venue.name} | The front of the place, so people can find it. |
| order | Getting the {menuItem.name}, the one everyone told me about. | Ordered: {menuItem.name} | What you are ordering, with the menu in view. |
| dish | (none) | (none) | The dish on the table, close enough to see what it is. |
| bite | First bite of the {menuItem.name}. Okay, here's my honest reaction. | First bite | You taking the first bite, your face and the food in frame. |
| verdict | {menuItem.price} at {venue.name}. Would I come back for it? Certainly. | {menuItem.name} · {menuItem.price} | You, looking at the lens, saying if it is worth the price. |

`titleFacts`: arrive `{venue.name}`, order and bite `{menuItem.name}`, dish `{menuItem.name} · {menuItem.price}`,
verdict `{venue.name} · {menuItem.price}`. Capture order 1-5 as listed; edit order keeps the dish first. Every step is
required; PiP is gone (bite, order and verdict were `camera: both`). Step ids are unchanged (same roles), so no
version bump. The old `prompter`/`captions` stay for older builds.

Beats of the complex guides:

- plate_high_orbit (5 s): 0.0 Elbows on the table, plate in the middle of the frame. / 1.0 Circle the phone around
  the plate at one even pace. / 3.5 Keep the plate centred until its far side shows.
- plate_tissue_slide (4 s): 0.0 Rest the phone's bottom edge on a napkin. / 1.0 Slide it left to right along the
  near table edge. / 3.0 Keep the lens on the dish; don't slide into it.

Owner rulings 2026-11-10: every guide a step offers has the step's level, so the order of spoken and silent steps
never changes with the guide picked; dish guides show one shared example dish (dinner plate with pasta) for every
dish kind, so `table_spread_orbit` (a shared spread) left the dish step. `plate_rise_overhead` is pending in
`guide_levels.json` with its spec. The verdict line still ends on "Yes" (an opinion in a spoken line, allowed).


Kinds: coffee, dining, bakery, fast-food, entertainment. `featuresMenuItem: true`. 5 steps, 27 s.
Review kinds covered (research/menu_item_kinds.md): plates and bowls (mains, curries, pasta, soups, sushi),
starters and sides. The other review kinds have their own variant.

## Idea
The existing kit script, kept: one dish from the venue's Loca menu, opened on the food, then the visit, the
order, the bite and a verdict with the price.

## Audience moment
Someone deciding where to eat tonight, scrolling with the sound off. They need the dish in the first second, the
name of the place, the price, and a person they trust saying whether it is worth it.

## Why this order
1. `dish`: the most appetising frame first, not the facade (best_practices/dining.md: hook on the food).
2. `arrive`: the place, after the hook has earned the viewer's next 4 s; carries the name on screen.
3. `order`: the dish's name said aloud (searchable speech) and the menu in frame.
4. `bite`: the honest reaction is the proof.
5. `verdict`: price and where, the call to action.

## Shot plan as a sequence
- `dish`: hero-push. Low angle, close to detail, push-in; the sauce or steam grows until it fills the frame.
  Whip out.
- `arrive`: a whip lands on the door; eye-level walk-in, wide to medium (door-push-through without the
  push-through join, so the counter is visible). Cut.
- `order`: counter-over-shoulder, medium to close push-in toward the menu. Match-cut on the dish.
- `bite`: sip-reaction shape for food, both cameras: medium to close as the creator leans into the bite. Cut.
- `verdict`: static arm's-length selfie, medium. The size steps back from close, so the cut is not a jump.

## Changes from the kit version
- `bite` and `verdict` were 10 s each, above the 8 s step limit: now 7 s each; total 35 s became 27 s.
- `order` had a prompter but `pip: false`, so the kit treated it as "just film" with words; it is now spoken
  (`pip: true`).
- Step images were borrowed from other scripts (`restaurant-date-night_dish.jpg` and so on); they now follow the
  `<template id>_<step id>.jpg` rule. Agent 02 may start from the borrowed images.

## Alternatives considered
- Arrive first, dish second: the classic order, but it spends the first second on a door (rejected).
- A separate "price" step: folded into the verdict to keep the script under 30 s.
