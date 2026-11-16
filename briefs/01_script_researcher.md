# Brief 01: script researcher

Skill to load: `script-research` (`Loca/.claude/skills/script-research/SKILL.md`).
Output folder: `ScriptsAndGuides/research/` and `ScriptsAndGuides/scripts/`.

## What to deliver

1. `research/venue_kinds.md`: every production category (the 20 slugs in
   `research/categories_creator.graphql.loca.us.json`) mapped to a script kind. Group where the creator's video
   would be the same (dining, food-and-drinks, food-and-drinks-family are one kind; services-* may be one or two).
   Each kind gets an id, a title the app shows, an SF Symbol name, and the slugs it covers. Say which production
   slugs get no scripts and why (for example `services-other`).
2. `research/best_practices/<kind>.md`: for each script kind, what makes a short venue video work on
   Instagram Reels, TikTok and YouTube Shorts in 2025 to 2026: the hooks that hold the first second, shot orders
   that read as a story, lengths, where the venue's name and offer appear, what first-time visitors want to see,
   what to avoid. Cite sources in `research/sources.md` (platform guidance, creator case studies, hospitality
   marketing studies); say when a point is your own judgement.
   Also `research/commercial_shots.md`: a deep analysis of how commercial food, drink, retail and service ads are
   shot: the recurring camera angles (low hero angle on a dish, top-down flat lay, eye-level over the counter,
   over-shoulder on the barista), the moves (slow push-in, pull-out reveal, orbit around the hero, tilt down from
   the sign, whip between details), typical shot lengths, and the transitions that join them (match cut on the
   object, whip, push-through, pull-back reveal). Give each a short name; these names are the vocabulary of the
   shot plan below. Note which of them a phone held by one person can do without rigs.
3. `scripts/script_templates.json`: at least 5 scripts per kind, in the kit's format, with ids, 3 to 7 steps each,
   lengths within the limits, `overlays` left empty (agent 03 fills them) and `imageURL` set to
   `<template id>_<step id>.jpg` (agent 02 produces the files). Keep the existing 10 scripts unless a better one
   replaces them; keep `food-review` and make its steps dish-kind aware where it helps.
4. `scripts/shot_plan.json`: for every step, the camera work in the vocabulary of `commercial_shots.md`: `angle`,
   `start` and `end` framing, `move`, `seconds`, `transitionOut`, and a one-line `reads` ("the cup grows until it
   fills the frame, then we cut on the cup to the pour"). Consecutive steps must chain: step N ends where step N+1
   can start, or `transitionOut` says how they join. The format is in the `script-research` skill.
5. `scripts/<kind>/<template id>.md`: for each script, the idea, the audience moment it serves, why these steps in
   this order, the shot plan explained as a sequence (angle, move, cut, next angle), and alternatives considered.
6. `research/menu_item_kinds.md`: an audit of dish and product kinds found in venue menus (query
   `menusByBusinessId` through the production GraphQL endpoint for a sample of venues per food kind, read section
   titles and item names), grouped into review kinds (hot drinks, pastries, mains, desserts, cocktails, and so on),
   with the shot and the line pattern a review of that kind needs. The food-review script, or a variant per
   kind, must cover each.

## How to work

- Start from the facts in `ScriptsAndGuides/README.md`; do not re-fetch what is there.
- The production endpoint is public for reads: `https://creator.graphql.loca.us/graphql`. Business and menu
  queries are shown in `VideoEditorKit/tools/scriptwriter/server.py` (`VENUE_QUERY`, `MENU_QUERY`).
- Write spoken lines as one person talking, 8 to 14 words per spoken step; "just film" steps carry the on-screen
  text options instead.
- Finish with `research/HANDOFF.md`: what is done, what is uncertain, what agents 02 and 03 need to know.

## Done when

Every production category is mapped; every step has a shot-plan entry and consecutive entries chain; each kind
has 5 or more scripts that validate against the kit's format
(`swift test --filter VideoScriptsTests` in VideoEditorKit after copying the JSON into
`Sources/VideoScripts/Resources/` passes, or the reason it cannot is written down); the menu audit names every
review kind with a script covering it.
