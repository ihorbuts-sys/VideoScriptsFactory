# P0 opinion rewrite: changed lines (2026-11-13)

Source: `HANDOFF_scripts_agent_opinions_faceless_linter.md` (Loca task folder). Old values from
`archive/2026-11-13_opinion_rewrite/scripts/_parts/`, new ones from `scripts/_parts/`. "Rule fixed" names the linter
rule (`scripts/tools/line_lint.py`) the old text breaks; "new field" is a field the handoff adds; seconds follow the
step length rule with the longest opinion option and the `noPrice` line in. Every step also gains `key` (= its id).
Captions and prompters are the older builds' texts (composer rule 8) and are rewritten to pass the same rules.

Opinion sets: `scripts/opinion_sets.json` (verdict_answer, bite_reaction used in P0; taste_descriptors, place_word,
value_word written for P1). Differences from the handoff's starting sets: `verdict_answer` adds a second neutral
option `maybe_again` ("Maybe, to try more.") because "Maybe, for the price." does not read after first-visit's
verdict, which has no price; `place_word` spells "cozy" (US English) where the handoff wrote "cosy".

Verdict order (the script's own positive word first, never preselected): food-review `certainly, maybe, not_for_me`;
first-visit `absolutely, maybe_again, not_for_me`. Reaction slots (`bite_reaction`, neutral "Okay." preselected):
food-review/bite, first-visit/sip, first-visit/forkful. First sip uses `bite_reaction` in P0, since the handoff puts
`taste_descriptors` in P1.

## first-visit

| Step | Field | Old | New | Rule fixed |
|---|---|---|---|---|
| entrance | line | First time at {venue.name}. Let's see if it's worth the hype. | First time at {venue.name}. Walking in to see what's on the menu. | L2, L3 |
| entrance | captions[0] | Found it / Found the place everyone keeps telling me about. | Found it / Found it. First time at {venue.name}. | L1 |
| entrance | captions[1] | New spot / New spot on my walk to work. Had to stop and try it. | New spot / New spot for me. Walking in to try it. | L5, L8 |
| entrance | card | None | First time at {venue.name} | L14 |
| entrance | seconds | 6 | 7 | timing (L8, longest option in) |
| counter | line | Asking the barista what first timers should order here. | Asking the barista what first-timers usually order here. | wording; direction now matches it |
| counter | prompter | Here is what I'm ordering, the barista's pick for first timers. | Asking the barista what first-timers usually order here. | L1, L8 |
| counter | direction | Hold the phone still over your shoulder toward the menu board and the barista, and say what you order. | Hold the phone still over your shoulder toward the menu board and the barista, and ask what first-timers order. | direction matches the line |
| counter | captions[0] | The order / Here is what I'm ordering, the barista's pick for first timers. | The order / Asking the barista what first-timers usually order here. | L1, L8 |
| counter | captions[1] | Barista's pick / Asked the barista what to get first, and this is what they said. | At the counter / At the counter, picking my first order here. | L1, L8 |
| counter | card | None | Ordering at the counter | L14 |
| menu | line | Asking the kitchen what they are known for. Lots of options here. | Picking from the menu for my first visit here. | L1 |
| menu | captions[0] | The menu / Here is the menu, and this is the dish I am ordering. | The menu / This is the menu, and the dish I am ordering. | L8 (fits the 5 s step) |
| menu | captions[1] | What to order / Asked what to get on a first visit, and this was the answer. | What to order / Reading the menu. This is the one I am ordering. | L8 |
| menu | card | None | The menu | L14 |
| menu | seconds | 6 | 5 | timing (L8, longest option in) |
| drink | captions[0] | First time here / First time at this place, and the pour already looks right. | First time here / First time at {venue.name}. This is my cup. | L3 |
| drink | captions[1] | Watch the pour / Watch the milk go in. This is the cup I came for. | My order / My order, on the table at {venue.name}. | direction match: the step films the cup on the table, not the pour |
| drink | captions[2] | Look at this / Look at this before I tell you anything about the place. | (none) | L2 |
| drink | card | None | First cup at {venue.name} | L14 |
| drink | seconds | 6 | 5 | timing (L8, longest option in) |
| plate | captions[0] | Here it comes / Here it comes. Our server said this is the plate to order. | Here it comes / Here it comes. My first plate at {venue.name}. | L1 |
| plate | captions[1] | The plate / This plate, and you can see why we ordered it. | The plate / The plate, on the table at {venue.name}. | L3 ("you can see why") |
| plate | captions[2] | Two plates, one table / Two plates, one table, and we are sharing both. | (none) | claim the script cannot back (a second person, two plates) |
| plate | card | None | First plate at {venue.name} | L14 |
| plate | seconds | 6 | 5 | timing (L8, longest option in) |
| sip | line | Okay, first sip. Here's how it tastes. | First sip at {venue.name}. {opinion} | L2 |
| sip | prompter | Okay, first sip. Smooth, not bitter, and the milk is silky. | First sip at {venue.name}. {opinion} | L3, L8 |
| sip | direction | Front camera at arm's length with the cup in frame. Take a sip, lean in a little and react honestly. | Front camera at arm's length with the cup in frame. Take a sip, lean in a little and react in your own words. | the reaction is the creator's own words (L3 frame) |
| sip | captions[0] | First sip / Okay, first sip. Smooth, not bitter, and the milk is silky. | First sip / First sip at {venue.name}. {opinion} | L3, L8 |
| sip | captions[1] | Moment of truth / Moment of truth. Strong enough to taste the coffee through the milk. | My cup / Trying my first cup here. {opinion} | L2, L4, L8 |
| sip | card | None | First sip: {opinion} | L14 |
| sip | opinion | (none) | {"set": "bite_reaction", "preselect": "okay", "order": ["okay", "good", "not_sure"]} | new field |
| sip | seconds | 4 | 5 | timing (L8, longest option in) |
| forkful | line | First forkful of what they told me to order. Okay. | First forkful at {venue.name}. {opinion} | L1 |
| forkful | prompter | First forkful of the dish they told me to order. Okay, wow. | First forkful at {venue.name}. {opinion} | L1, L3, L8 |
| forkful | direction | Front camera at arm's length, eyes level. Lift the first forkful toward the lens and react honestly. | Front camera at arm's length, eyes level. Lift the first forkful toward the lens and react in your own words. | the reaction is the creator's own words (L3 frame) |
| forkful | captions[0] | First bite / First forkful of the dish they told me to order. Okay, wow. | First bite / First forkful at {venue.name}. {opinion} | L1, L3, L8 |
| forkful | captions[1] | Not what I expected / Not what I expected. Better. I am finishing all of this. | My plate / Trying my first plate here. {opinion} | L3, L4, L8 |
| forkful | card | None | First bite: {opinion} | L14 |
| forkful | opinion | (none) | {"set": "bite_reaction", "preselect": "okay", "order": ["okay", "good", "not_sure"]} | new field |
| room | line | Grabbed a table. Love the vibe in here. | Grabbed a table. This is the view from my seat. | L3 |
| room | captions[0] | Look at this room / Look at this room. This is the mood for tonight. | The room / Grabbed a table. This is the view from my seat. | L5 |
| room | captions[1] | Can we talk here? / Here is how loud it gets. Can we actually talk in here? | My seat / This is where I'm sitting at {venue.name}. | L4, L8 |
| room | captions[2] | Pick your seat / Here is the seat to ask for when you book. | (none) | L12 (invented booking advice) |
| room | card | None | The view from my seat | L14 |
| verdict | line | That's {venue.name}. Here's why I'd come back. | That's {venue.name}. Would I come back? {opinion} | L2 |
| verdict | prompter | Here is the price, the street, and why I'm coming back. | That's {venue.name}. Would I come back? {opinion} | L2 teaser; L6 (no price or street in the script) |
| verdict | direction | Front camera at arm's length, eyes level. Say the price, the street, and why you would come back. | Front camera at arm's length, eyes level. Say where you are and whether you would come back. | L6 |
| verdict | captions[0] | Why I'm back / Here is the price, the street, and why I'm coming back. | {venue.name} / That's {venue.name}. Would I come back? {opinion} | L2 teaser; L6 (no price or street in the script) |
| verdict | captions[1] | Go try it / Go try it and tell me what you ordered. I want to know. | First visit / First visit to {venue.name} done. Coming back? {opinion} | L4, L8 |
| verdict | card | None | Would I come back? {opinion} | L14 |
| verdict | opinion | (none) | {"set": "verdict_answer", "preselect": null, "order": ["absolutely", "maybe_again", "not_for_me"]} | new field |

## food-review

| Step | Field | Old | New | Rule fixed |
|---|---|---|---|---|
| arrive | captions[0] | Found it / Found the place everyone keeps telling me about. | Found it / Found it. Look for the sign by the door. | L1 |
| arrive | captions[1] | This is the spot / This is the spot. Easy to walk past, so look for the sign. | This is the spot / This is the spot. I came here for the {menuItem.name}. | L8 |
| arrive | card | None | {venue.name} | L14 |
| order | line | Getting the {menuItem.name}, the one everyone told me about. | Picking from the menu. Getting the {menuItem.name}. | L1 |
| order | prompter | I'm getting the one everyone talks about, let's see why. | Picking from the menu. Getting the {menuItem.name}. | L1, L2 |
| order | captions[0] | The order / I'm getting the one everyone talks about, let's see why. | The order / Picking from the menu. Getting the {menuItem.name}. | L1, L2 |
| order | captions[1] | Server's pick / Asked what I should get, and they all said this one. | On the menu / Found it on the menu. Getting the {menuItem.name}. | L1, L8 |
| order | card | None | Ordered: {menuItem.name} | L14 |
| dish | captions[0] | Worth the hype? / Let's find out if this one is worth the hype. | {menuItem.name} / The {menuItem.name}, the dish I came here for. | L2, L3, L4 |
| dish | captions[1] | Came for one dish / I came here for one dish, and this is it. | The dish / Here is the {menuItem.name} at {venue.name}. | fact with slots instead of a generic frame |
| dish | captions[2] | Look at this plate / Look at this plate before I tell you anything about it. | (none) | L2 |
| dish | card | None | {menuItem.name} | L14 |
| dish | seconds | 6 | 5 | timing (L8, longest option in) |
| bite | line | First bite of the {menuItem.name}. Okay, here's my honest reaction. | First bite of the {menuItem.name}. {opinion} | L2 |
| bite | prompter | First bite. Okay, I am going to be honest with you. | First bite of the {menuItem.name}. {opinion} | L2 |
| bite | direction | Back camera on the dish, you on the front camera: lift the first bite toward the lens and react honestly. | Back camera on the dish, you on the front camera: lift the first bite toward the lens and react in your own words. | the reaction is the creator's own words (L3 frame) |
| bite | captions[0] | First bite / First bite. Okay, I am going to be honest with you. | First bite / First bite of the {menuItem.name}. {opinion} | L2 |
| bite | captions[1] | Moment of truth / Moment of truth. Here is what I really think of it. | {menuItem.name} / Trying the {menuItem.name} first. {opinion} | L2, L4 |
| bite | card | None | First bite: {opinion} | L14 |
| bite | opinion | (none) | {"set": "bite_reaction", "preselect": "okay", "order": ["okay", "good", "not_sure"]} | new field |
| bite | seconds | 6 | 5 | timing (L8, longest option in) |
| verdict | line | {menuItem.price} at {venue.name}. Would I come back for it? Certainly. | {menuItem.price} at {venue.name}. Would I come back? {opinion} | L3 |
| verdict | prompter | My verdict, what it costs, and where to find it. | {menuItem.price} at {venue.name}. Would I come back? {opinion} | L2 teaser (says what comes, not the thing) |
| verdict | direction | Hold the phone at arm's length with the plate in frame. Give your verdict, the price, and where it is. | Hold the phone at arm's length with the plate in frame. Say the price, where you are, and whether you would come back. | direction matches the line |
| verdict | captions[0] | The verdict / My verdict, what it costs, and where to find it. | {menuItem.name} · {menuItem.price} / {menuItem.price} at {venue.name}. Would I come back? {opinion} | L2 teaser; caption text now the fact |
| verdict | captions[1] | Would I come back / Would I come back for this? Here is my honest answer. | {venue.name} / {menuItem.price} at {venue.name}. Coming back? {opinion} | L2 |
| verdict | card | None | Would I come back? {opinion} | L14 |
| verdict | opinion | (none) | {"set": "verdict_answer", "preselect": null, "order": ["certainly", "maybe", "not_for_me"]} | new field |
| verdict | noPrice | (none) | {"line": "{venue.name}. Would I come back? {opinion}", "card": "Would I come back? {opinion}", "caption": "{menuItem.name}"} | L10 |
| verdict | seconds | 6 | 8 | timing (L8, longest option in) |

## Guide metadata (guides/p0/guide_levels.json, the 42 guides P0 steps use)

- `showsFace` true: bite_friend_three_quarter_v2, bite_selfie_eye_v2, sip_friend_side_v2, sip_high_lean_v2,
  sip_selfie_eye_v2, verdict_eye_level_v2, verdict_friend_eye_v2, verdict_high_plate_v2, verdict_propped_rear.
  Face-free alternatives that already exist: first bite `bite_pip_dish_v2` (fork toward the lens, food only), first
  sip `sip_cup_only`. The verdict has none: `verdict_plate_after_push` is pending (L13 shows as a warning until it
  renders).
- `needsHelper` true: entrance_friend_static, counter_over_shoulder_v2, bite_friend_three_quarter_v2,
  sip_friend_side_v2, verdict_friend_eye_v2.
- `guideVisibleToCreator` false: the five helper guides and verdict_propped_rear (the screen faces away).
- `units` metric (the guide text gives centimetres or metres; to convert, owner go-ahead needed because the texts are
  published): bite_friend_three_quarter_v2 (85 cm), counter_edge_to_pass_v2 (15 cm), counter_over_shoulder (40 cm),
  counter_over_shoulder_v2 (20 cm), entrance_friend_static (3-4 m), entrance_sign_tilt (45 cm), menu_card_top
  (12 cm), sip_friend_side_v2 (85 cm), steam_slide_pull_out (30 cm), steam_top_orbit (30 cm), verdict_friend_eye_v2
  (1.3 m), verdict_propped_rear (1.2 m). Proposed US texts: 85 cm "about 3 feet", 15 cm "about 6 inches", 40 cm
  "about 16 inches", 20 cm "about 8 inches", 3-4 m "10-13 feet", 45 cm "about 18 inches", 12 cm "about 5 inches",
  30 cm "about a foot", 1.3 m "about 4 feet", 1.2 m "about 4 feet". All other P0 guides: `us`.
- `zoomHint` "2x (closer)": menu_board_static, menu_board_tilt_down, menu_board_tilt_up_v2 (their text says "2x").

Duplicate guide titles (rename proposed, published ids unchanged):

| Guides | Title today | Proposed |
|---|---|---|
| entrance_sign_tilt, entrance_sign_tilt_v2 | Sign down to the door | "Sign down to the door, close" / "Sign down to the door, across the street" |
| counter_edge_to_pass, counter_edge_to_pass_v2 | Along the counter to the pass | "Low along the counter" / "Along the counter edge, 6 inches up" |
| counter_over_shoulder, counter_over_shoulder_v2 | Over your shoulder at the counter | "Over your shoulder, slide" / "A friend films over your shoulder" |

## Missing guides and objects (briefed, nothing rendered or generated)

- `verdict_plate_after_push`: face-free verdict, easy, back camera; request
  `scripts/food-review/food-review/requests/verdict_plate_after_push.md`; pending in `guide_levels.json` for
  food-review/verdict and first-visit/verdict.
- `handheld_hold_turn`, `handheld_paper_open`: complex handheld dish guides for bakery and quick bites; requests in
  the same folder; pending without a step (the handheld step variant is an owner decision, below).
- Objects (`OBJECTS.md` requests): a neutral example dish replacing the pasta (with a "finished" state for the
  face-free verdict), and a paper wrap plus serving tray for handheld food.
- First bite face-free: already covered by `bite_pip_dish_v2`; no request.

## Owner answers 2026-11-13 (second round)

- Verdict lines shortened so a long real venue and dish name still fit 8 s with the longest answer (no short names
  exist): line, prompter and captions[0] `{menuItem.price} at {venue.name}. Would I come back? {opinion}`,
  captions[1] `{menuItem.price} at {venue.name}. Coming back? {opinion}`, noPrice `{venue.name}. Would I come back?
  {opinion}`; the step goes from 8 s to 6 s. Rule L9 (line).
- Long captions (L9 caption) are a warning, not an error: the app wraps them (open question oq-caption-wrap).
- Food review dish, bite, verdict: `servingVariants.handheld` for bakery and fast-food (where and how to film only;
  texts unchanged). Dish guides `handheld_hold_turn`, `handheld_paper_open` pending; no handheld bite guide yet.
- "centred" -> "centered" in the arrive and entrance directions (US English; the same word in other templates of
  coffee.json changed too).
- Guide texts in US units: 19 instructions (`p0_catalog.us_units`, applied to every registry guide) and 3 beats in
  `guide_levels.json`; the 12 guides marked metric are now `units: us`. check_scripts fails on any metric guide text.

## Typed dish: food-review-typed (owner 2026-11-13, third round)

Owner: "Make some more generic script so the user will type just this dish before reviewing (if no menu for picking
is available)." Replaces the dish-kind picker idea.

- New P0 script `food-review-typed` ("Review a dish"), venue kinds coffee, dining, bakery, fast-food (the same as
  food-review). Script field `dishSource: {"kind": "typed", "maxLength": 40, "hint": "The dish or drink you are
  reviewing"}`: the creator types the name before filming, it fills `{menuItem.name}`; there is never a price, so no
  `{menuItem.price}` and no `noPrice`. Texts never assume a plate, fork, table or hand, and never put "the" before the
  typed name.
- food-review gains `dishSource: {"kind": "menu", "whenNoMenu": "food-review-typed"}`: the app offers food-review when
  the venue has a menu to pick from, food-review-typed when it does not. Nothing else in food-review changed.
- `verdict_answer` version 2 adds "Definitely." (positive) so the typed script has its own first positive word.

| Step | Seconds | Line | Card | Caption | Opinion |
|---|---|---|---|---|---|
| arrive | 5 | `{venue.name}. I came here for {menuItem.name}.` | `{venue.name}` | `{venue.name}` | |
| dish ("What I got", complex) | 5 | none (silent) | `{menuItem.name}` | none | |
| bite ("First taste") | 5 | `First taste of {menuItem.name}. {opinion}` | `First taste: {opinion}` | `First taste` | `bite_reaction`, preselect okay |
| verdict | 6 | `{venue.name}. Would I come back? {opinion}` | `Would I come back? {opinion}` | `{menuItem.name}` | `verdict_answer`, no preselect, order definitely / maybe_again / once / not_for_me |

Total 21 s. Directions: "Hold the phone low, about a foot away, and move in slowly until it fills the frame. Steam,
sauce or foam if it has it." / "take the first bite or sip toward the lens" / "with what you ordered in frame".
Step pictures reuse food-review's (`food-review_<step>.jpg`).

Checks: `line_lint.dish_source_rules` (kind menu or typed; typed has maxLength 10-60 and a hint of at most 60
characters without slots; a menu source's `whenNoMenu` must be a typed script covering its venue kinds); L6 fails a
`{menuItem.price}` in a typed script; L9 times a typed name at its cap ("Spicy chicken curry with rice and garlic",
40 characters). The writer refuses a price for a typed or priceless menu item (`menuItem.source: "typed"`).

Guides: the step guides are food-review's (plate reveal, fork bites, verdict at arm's length); every one shows a
plate or a fork. Gaps (guide requests, nothing rendered): a dish guide whose dish follows the venue kind; a
first-taste guide that works for a drink (today's sip guides are another shot type); a face-free verdict that is not
a finished plate. The pending `verdict_plate_after_push` is listed for this verdict too.

## First visit features a dish (owner comment 2026-11-14, fourth round)

Owner, on the menu step's "Reading the menu. This is the one I am ordering.": "This is the one - template dish picked
at the beginning of the flow (or entered manually)".

- first-visit: `featuresMenuItem` false -> true; new `dishSource: {"kind": "menu", "typedFallback": {"maxLength": 40,
  "hint": "The dish or drink you are ordering"}}`. The dish is picked from the menu at the start of the flow, or typed
  in the same script when the venue has no menu (food-review keeps its `whenNoMenu` script fallback).
- Menu step (dining), every text that pointed at "the dish I am ordering" now names it:

| Field | Old | New | Why |
|---|---|---|---|
| line | Picking from the menu for my first visit here. | Picking from the menu. I'm ordering {menuItem.name}. | owner comment |
| card | The menu | Ordering {menuItem.name} | same dish as the line |
| captions[0].script | This is the menu, and the dish I am ordering. | This is the menu. I'm getting {menuItem.name}. | owner comment |
| captions[1].script | Reading the menu. This is the one I am ordering. | Reading the menu. I'm ordering {menuItem.name}. | owner comment |

- Captions stay "The menu" / "What to order" (a dish name there would go over 32 characters).
- Checker: a menu source may carry `typedFallback` (maxLength 10-60, hint up to 60 characters without placeholders)
  or `whenNoMenu`, not both; a script whose dish may be typed never uses `{menuItem.price}`, and its lines are timed
  with the 40-character sample name. 22 line-checker tests pass; the catalog merges with 0 errors.
- No other first visit step names the dish (proposal: oq-first-visit-dish-steps).

## Open questions (the one canonical list)

Every open item for Video Studio content lives here; the review site's "Open questions" is generated from this table
(scratchpad/review-site-gen reads it). Keep the id when an item changes so comments stay attached. Status: open,
answered (owner decided, work done or under way), deferred (parked on purpose).

| Id | Area | Question | Status | Owner answer (date) |
|---|---|---|---|---|
| oq-delivery | Backend | Catalog delivery: one JSON bundle through a single GraphQL query (A), or GraphQL types (B)? | open | |
| oq-anim-format | Backend | Guide animation format: APNG is 2.4-5.2 MB per guide against a 1.5 MB target. Switch to video (HEVC with alpha, VP9) or a lighter codec? | open | |
| oq-music | Backend | Music for dining and fast food: a new Suno batch is needed, and the Suno licence terms are unchecked. | open | |
| oq-energy | Backend | Music energy on one absolute scale across batches (today it is relative within each batch). | open | |
| oq-analytics | Backend | Analytics: fields for mood, track and engine in the creation event. | open | |
| oq-flag | Backend | Feature flag key: one shared `video.editor`, or one per platform (`ios.video-editor`)? | open | |
| oq-verdict-order | Texts | Should a script's verdict `order` hide the answers it does not list? Example, first visit (no price in the script): its order is Absolutely. / Maybe, to try more. / Not for me. Today the app would show all set answers: Absolutely. / Maybe, to try more. / Certainly. / Maybe, for the price. / Once was enough. / your words / Not for me, so "Maybe, for the price." appears in a script that never names a price. Option A: the order is the full list (chips: Absolutely. / Maybe, to try more. / your words / Not for me; a negative answer then needs listing too, for example Once was enough.). Option B: keep showing all, listed ones first. A changes what the app reads. | open | |
| oq-caption-wrap | Texts | No short names exist, so with a long dish name the captions "Ordered: {menuItem.name}" and "{menuItem.name} · {menuItem.price}" go over 32 characters (35 and 37 with the sample "Iced Brown Sugar Oat Latte"). The linter now reports that as a warning and the app wraps the caption; the alternative is shorter captions (the dish name alone). Accept wrapping? | open | |
| oq-line-choices | Texts | Remaining line choices from the owner's script review. | open | |
| oq-fallback-words | Texts | Wording when a placeholder has no value ("this place", "this dish", "the price"). | answered | Food review verdict now has a no-price version; the fallback words stay only for older and AI-written lines (2026-11-13) |
| oq-sip | Texts | Sip and first bite: a fixed line cannot know the taste. | answered | Neutral frame + `{opinion}` from `bite_reaction`, handoff adopted (2026-11-13) |
| oq-time-neutral | Texts | Texts that only fit one time of day. | answered for P0 | P0 has none (first visit "the mood for tonight" removed 2026-11-13); the P1 ones (food review handheld "Lunch at", table "breakfast", pour "happy hour") go with the P1 rewrite |
| oq-short-names | Texts | Where would `venue.shortName` / `menuItem.shortName` come from? | deferred | Skip, we have none (2026-11-13). Slots removed from the linter, the writer and the app handoff |
| oq-handheld | Venue fit | Food review at bakery and quick-bite venues: every dish guide is a plated table shot. | answered | "Yes, let's try" (2026-11-13): food review dish, bite and verdict carry a `handheld` serving variant for bakery and fast-food; its two dish guides are briefed, not rendered |
| oq-handheld-bite | Venue fit | All first-bite guides show a fork. The handheld bite has no guide of its own; brief a two-hands bite guide? | folded into v3-guide-work | v3: `after` guides by form include a hand bite (design section 7) |
| oq-service-style | Venue fit | Where could service style (counter or table) come from? Candidates: the venue category, Google Places `dineIn`/`takeout`. | answered | v3 design (2026-11-16): from categories: food-truck = truck, coffee/bakery/fast-food = counter, other food = dineIn (`research/p0_v3_design.md` section 6) |
| oq-neutral-dish | Guides | Which dish do the dish guides show when no menu item is picked? | answered | v3 design (2026-11-16): guides key on the serving form; the dish kind picks a rendered dish on that form (pasta, pastry, pancakes, pizza, salad) else the form default |
| oq-burger | Guides | Approve the Tripo burger in line art for fast-food dish guides? Until then fast food shows the pasta. | open | |
| oq-typed-guides | Guides | food-review-typed reuses plated, fork-based guides. Brief a venue-kind dish guide, a drink first-taste guide and a non-plate face-free verdict? | open | |
| oq-typed-name | Texts | Typed dish name: 40 characters, trimmed, no placeholders. Should the app suggest a capital first letter, and should a blocked word list apply to what creators type? | open | |
| oq-definitely | Texts | "Definitely." added to the verdict answers so food-review-typed has its own first positive word (3 scripts, 3 words). Keep it? | open | |
| oq-units | Guides | Metric in published guide texts. | answered | No metric anywhere (2026-11-13): 19 instructions and 3 beats converted, staged, not published |
| oq-counter-receive | Guides | counter_hand_receive round 8 waits for review; the loop-start fade-in is not done and the counter depth (about 23 inches in the scene) needs confirming. | open | |
| oq-barista | Guides | Should the barista also appear behind the bar in the 4 menu-board shots and the 2 room shots? | open | |
| oq-fork | Guides | Use the new fork grip (tripod hold) on the friend-filmed first-bite guide too? | open | |
| oq-latte | Guides | Offer pour_top_down_latte on the first visit drink step? | open | |
| oq-previews | Pictures | Three first visit pictures were borrowed from other scripts (sip, drink, verdict) and need checking against their current guide lists. | open | |
| oq-first-visit-dish-steps | Texts | First visit now has a dish, but only the dining menu step names it; coffee venues (counter step, no menu step) never hear it. Name it also in: counter ("Asking the barista about {menuItem.name}." or "Ordering {menuItem.name}."), plate or drink card ("First {menuItem.name} at {venue.name}"), sip or forkful line ("First taste of {menuItem.name}. {opinion}"), verdict caption? The counter line "what first-timers usually order" also reads oddly once the dish is chosen in advance. | open | Proposal, not applied (2026-11-14) |
| oq-p1-rewrite | P1 | The 49 older scripts and the 5 hidden variants fail the linter; rewrite kind by kind after the P0 review. | open | Planned after P0 sign-off |
| v3-verdict-chips | Texts | Verdict chips: the Figma's adjectives or the v2 answers. | agreed | 2026-11-16: 5 levels from negative to positive, then replaced the same day by D-3-levels: neutral, good, very good, plus your own words; "Not for me" on verdicts is the only negative, a private funnel |
| v3-locations | Scripts | The Figma "Locations" script. | deferred | Skip for now (2026-11-16) |
| v3-rolls | Texts | Dish kind "rolls". | agreed | 2026-11-16: sushi -> "sushi and Asian"; wraps -> handhelds |
| v3-menu-fallback | Texts | A menu section that maps to no kind: plain dish plus a one-tap kind chip. | agreed | 2026-11-16 |
| v3-amenity-unlisted | Texts | May a creator pick an amenity the business does not list (their own filmed observation)? | agreed | 2026-11-16 |
| v3-sticker-cta | Texts | Figma "Call to action" stickers (creator-placed, e.g. "Visit us") vs the rule that our captions carry no call to action. | agreed | 2026-11-16: allowed as the creator's own choice; the catalog never writes a call to action (L4 stays for authored text) |
| v3-mixed-venue | Venue fit | A venue with food and non-food categories gets the food subject first. | agreed | 2026-11-16 |
| v3-guide-work | Guides | v3 work list: about 28 guides and 8 objects; objects still need owner approval of line art. | agreed | 2026-11-16 approved; `research/p0_v3_design.md` section 7 |
| v3-old-ids | Backend | v2 ids map to v3 kinds for drafts and analytics. | dropped | 2026-11-16: nothing on the real backend yet, v3 starts clean |
| v3-amenity-nonsmoking | Texts | Non-smoking cannot be filmed: P0 offers 4 amenity chips, non_smoking goes to the AI writer as a fact only. | agreed | 2026-11-16 (owner: "ok") |
| v3-drink-kinds | Texts | Drink kinds: coffee; tea and matcha; iced and cold coffee; juices and smoothies; soft drinks and lemonades; beer and wine; cocktails and mocktails (no "signature" kind). Dish kinds: starters and sides; soups; bowls and sushi (Asian); mains; salads; pizza; handhelds (incl. wraps); pastry and bakery; desserts; breakfast. | agreed | 2026-11-16 (owner: "your list looks better") |
| v3-alcohol | Texts | Beer and wine, cocktails in P0 or P1 (US alcohol advertising rules: doc Decisions tab). | agreed | 2026-11-16: P1. Mocktails move under soft drinks and lemonades for P0 (assumed) |
| v3-text-versions | Texts | Every step has a pool of line versions; the app preselects by tags (daypart, menu section, kind) then rotates, and offers the rest as other options. | agreed | 2026-11-16 |
