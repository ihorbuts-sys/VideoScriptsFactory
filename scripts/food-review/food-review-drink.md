# food-review-drink: Review a drink

## Guided v0 (2026-11-10, p0/tasks/09)

Story: You order the {menuItem.name} at the counter, watch it being made, show the cup on your table, take the first sip and say whether it is worth {menuItem.price}.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| order | coffee, bakery, dining, fast-food | easy | the drink's name said aloud | counter_over_shoulder, counter_edge_to_pass | - | Getting the {menuItem.name}. The barista says it's their best. | Ordered: {menuItem.name} | Where you order, with the menu or the barista in view. |
| pour | coffee, bakery, dining, fast-food | easy | the pour is a hold; the creator can talk over it | pour_top_down_latte, pour_side_low | - | Watching them make the {menuItem.name}. Look at that pour. | {menuItem.name} | Your drink being made, the pour or the ice close up. |
| cup | coffee, bakery, dining, fast-food | complex | silent visual beat: orbit or slide | steam_orbit_eye, steam_slide_pull_out | - | (none) | (none) | Your drink on the table, close enough to see it. |
| sip | coffee, bakery, dining, fast-food | easy | the reaction | sip_selfie_eye, sip_high_lean, sip_friend_side | - | First sip of the {menuItem.name}. Here's how it tastes. | First sip | You taking the first sip, your face and the cup in frame. |
| verdict | coffee, bakery, dining, fast-food | easy | price and the call | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | {menuItem.price} at {venue.name}. Would I order it again? Definitely. | {menuItem.name} · {menuItem.price} | You, looking at the lens, saying if it is worth the price. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.


Kinds: coffee, bakery, dining, fast-food. `featuresMenuItem: true`. 5 steps, 25 s.
Review kinds covered: hot drinks (espresso, latte, tea, matcha, chai) and cold drinks (iced coffee, boba,
smoothies, juices, aguas frescas, mocktails). 6 of 17 sampled venues sell hot drinks, 13 sell cold ones.

## Idea
A drink opens on its pour, not on a bite: the latte art spreading, the milk swirling into iced coffee, the
boba stirred. Then the barista's pick, the cup, the sip and the price.

## Audience moment
A morning or afternoon scroller choosing a coffee stop near them. They want to see the drink being made, hear
how it tastes (strength, sweetness, milk) and know the price before they walk over.

## Why this order
1. `pour`: the motion that sells a drink (best_practices/coffee.md).
2. `order`: the barista and the drink's name said aloud; the human in the place.
3. `cup`: the finished drink on its own, so the viewer can picture it on their table.
4. `sip`: the taste in plain words.
5. `verdict`: price and "would I order it again".

## Shot plan as a sequence
- `pour`: pour-detail from above (top-down), close to detail push-in. Match-cut on the cup.
- `order`: counter-over-shoulder held static at medium: the cup is handed across the counter.
- `cup`: orbit-hero at cup height, close, orbit-right: the handle or straw comes around. Cut, camera flips.
- `sip`: sip-reaction on the front camera, medium to close.
- `verdict`: static selfie at arm's length.

## Alternatives considered
- Separate hot and cold scripts: the only difference is the pour shot, which the direction already names
  (latte art, or ice and colour), so one script covers both.
- Steam-hold for the cup step: steam only works for hot drinks against a dark background; the orbit works for
  both.
