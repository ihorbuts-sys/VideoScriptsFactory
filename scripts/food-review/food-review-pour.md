# food-review-pour: Review a beer or cocktail

## Guided v0 (2026-11-10, p0/tasks/09)

Story: At the bar, you watch the {menuItem.name} poured, show the full glass against the lights, take the first sip and give the price and the happy hour.

| Step | Kinds | Level | Why | Guides (recommended first) | Pending | line | caption | idea |
|---|---|---|---|---|---|---|---|---|
| build | entertainment, dining | easy | a hold at the bar edge while it is poured | pour_side_low | tap_pour_low | Here comes the {menuItem.name}. Watch them pour it. | {menuItem.name} | Your drink being poured or mixed, close at glass height. |
| glass | entertainment, dining | complex | silent visual beat with the glass | glass_slide_close | glass_raise_light | (none) | (none) | The full glass close up, with the bar lights behind it. |
| sip | entertainment, dining | easy | the reaction | sip_selfie_eye, sip_high_lean, sip_friend_side | - | First sip of the {menuItem.name}. Here's what it tastes like. | First sip | You taking the first sip, your face and the glass in frame. |
| verdict | entertainment, dining | easy | price and happy hour | verdict_eye_level, verdict_high_plate, verdict_friend_eye | - | {menuItem.price} at {venue.name}. Here's when happy hour starts. | {menuItem.name} · {menuItem.price} | You, looking at the lens, saying the price and when to come. |

Every step required, PiP removed, step ids unchanged; old prompter/captions kept for older builds. Beats are in `guides/p0/guide_levels.json`.


Kinds: entertainment, dining. `featuresMenuItem: true`. 4 steps, 20 s.
Review kinds covered: beer (drafts, flights, cans; 6 venues, Workhouse Wellness alone lists 37 local drafts)
and cocktails and spirits (5 venues; Kelly's Irish Pub lists 85 whiskeys).

## Idea
At a bar the drink is built in front of you: the tap pour and the head settling, or the shake, strain and
garnish. Open on that, then the glass against the light, the sip and the price with the happy hour.

## Audience moment
Planning a night out, deciding between two bars. They want the drink, the room behind it, and the price,
because happy hour is often the reason to pick a place.

## Why this order
1. `build`: the pour or the build is the hook (best_practices/entertainment.md).
2. `glass`: the colour against the bar lights; local or house-brewed is said here.
3. `sip`: the taste in three words.
4. `verdict`: price and happy hour.

## Shot plan as a sequence
- `build`: hero-push from the bar edge (low), close to detail as the glass fills. Match-cut on the glass.
- `glass`: eye-level, close, tilt-down as the glass is lowered onto the bar; the rim drops into the frame.
- `sip`: sip-reaction on the front camera; the camera flips, so a plain cut works.
- `verdict`: static selfie with the taps behind.

## Notes
- Only 4 steps and 20 s, the minimum total: bar light is low and night footage gets shaky, so fewer, longer
  steps are easier (judgement).
- Lines never encourage heavy drinking; the price and happy hour are the facts.

## Alternatives considered
- A flight of four beers: covered by the existing `bar-tasting` script.
