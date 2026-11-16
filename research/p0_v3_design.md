# P0 v3 design: script kinds, step roles, variants, guides and texts

Status: design reviewed by the owner 2026-11-16 (answers recorded in section 11); review closed 2026-11-16 (alcohol P1, CTA stickers allowed). Catalog v3 built 2026-11-16 in `scripts/v3/` (section 12); v2 is snapshotted in
`scripts/versions/v2_2026-11-16/` and the backend doc in `../doc_versions/v2_2026-11-16/`.

Source of the redesign: Figma "Loca — Video Studio · Step flow", node 291:3905 (40 screens), reviewed with the owner
2026-11-16. Marks: **Agreed** (owner said so, with date), **Assumed** (my reading, not contradicted yet), **Open**.

## 1. What the Figma changes

| Figma | v2 catalog | Status |
|---|---|---|
| Script list: From menu, Food, Drinks, Venue, Locations | first-visit, food-review, food-review-typed | Agreed 2026-11-16: two review types in the app, food review and venue review |
| Food / Drinks sheet: type the name, pick tags | typed dish, no tags | Agreed 2026-11-16: typed name plus one-tap kind chip; the Figma tags are kinds, no descriptor tags |
| From menu: item list with menu-section tabs | menu pick | Agreed |
| Venue | first visit | Agreed 2026-11-16: "treat first visit as Venue" |
| Locations | first-visit arrive | Agreed 2026-11-16: skip for now |
| Optional steps (Order "Optional"), skip, retake, continue later | every step required | Agreed 2026-11-16: optional steps exist (replaces the handoff rule "steps stay required") |
| Verdict chips good / amazing / tasty / okay / your words / Not for me | verdict_answer (Certainly, Absolutely, Maybe..., Once was enough, Not for me) | Agreed 2026-11-16: 5 levels per opinion step, wording fits the step and kind, plus typing your own (section 5) |
| Editor: subtitles from the prompter, extra text, stickers, filters, mute surround, music list | kit editor | Assumed: app work, no catalog change except the sticker rule below |

Figma copy that breaks the v2 line rules is treated as layout only (Assumed): "Worth the $8.50" (judgement outside
the slot, L3), "I'll be honest with you" (filler), "people queue at Lviv Croissants... the queue is worth it" (crowd
claim L1 plus judgement L3), chips with no negative answer, a "Call to action" sticker (captions ban calls to action;
a sticker the creator adds is their own choice: Open).

## 2. Script kinds and identity (Agreed 2026-11-16)

The app shows two review types (food review, venue review). The backend has four kinds; `kind` is the script's
identity (no `id`, no `type`).

| kind | Entry in the app | Subjects | Dish source |
|---|---|---|---|
| `dish-review` | Food review, Food card | dish kinds | typed name + kind chip |
| `drink-review` | Food review, Drinks card | drink kinds | typed name + kind chip |
| `menu-item-review` | Food review, From menu | from the menu section (dish or drink kind) | menu pick: name, price, kind from the section |
| `venue-review` | Venue review | venue subjects (section 6) | none |

- No mapping from the v2 ids (Agreed 2026-11-16: nothing runs on the real backend yet; v3 starts clean).
- Analytics, drafts and AI requests record `kind` plus the catalog version.
- `dishSource.kind` is renamed `dishSource.from` (`menu` | `typed`) so "kind" means one thing per level (Assumed).
- `menu-item-review` uses the dish or drink steps of the derived kind; it stays a kind for the UI and analytics.

## 3. Step roles (Agreed 2026-11-16)

One sequence for every kind. The kind and subject decide what each role films.

| Role | Required | Food review (dish / drink) | Venue review |
|---|---|---|---|
| `arrive` | yes | entrance, or the truck from across the street | same |
| `place` | yes | room, counter and display, or truck, by service kind | room or subject interior |
| `before` | no | Ordering | getting ready / before / browse / meet the team |
| `main` | yes (dish, drink, menu item: Agreed 2026-11-16) | The dish / The drink | the service in action (pattern decides) |
| `after` | no | First bite / First sip | the result / the moment after / the takeaway |
| `amenities` | no | chips | chips |
| `verdict` | yes | about the dish or drink | about the place or service |

For venue review the subject's pattern says which of before, main, after carries the payoff and is required
(section 6). Owner 2026-11-16: "Ordering (optional), The dish, First bite (optional), Amenities (optional)".

## 4. Variants and text versions (Agreed 2026-11-16)

Two mechanisms, kept apart:

1. **Variants** (structural, automatic): one ordered list on the step; the first matching entry overrides the base
   fields (`title`, `direction`, `guides`, `seconds`, and the version pool when the wording must change). `when` keys
   are the kind and data, never the serving form (Agreed 2026-11-16: "kind - drink review, not form - cup"); forms
   are used only to choose guides.

```json
"variants": [
  { "when": { "serviceKind": "truck" }, "guides": ["truck_window_pan"], "direction": "..." },
  { "when": { "kind": "drink-review" }, "title": "First sip", "versions": [ ... ] },
  { "when": { "price": false }, "versions": [ ... ] }
]
```

   `when` keys: `kind`, `subject`, `dishKind`, `drinkKind`, `serviceKind` (dineIn | counter | truck), `price`
   (true | false), later `pattern`. A `when` with several keys needs all of them.

2. **Text versions** (variety, creator-facing; Agreed 2026-11-16: "the structure is defined, but texts should be
   slightly different"): every step carries a pool of `versions`, each a `line` with its `caption` and `card`, and
   optional `tags` (`daypart`, `menuSection`, `dishKind`, `drinkKind`). The app preselects the most relevant version
   and offers the others as "Other options" in the prompter editor (Figma 291:5122). Preselection: versions whose
   tags match the context rank first (daypart from capture time, menu section, kind); among equals the app rotates or
   picks at random, so two videos rarely sound the same. Daypart is not an automatic switch (Agreed 2026-11-16): a
   morning or Breakfast-tagged version is just a version in the pool, preselected when it matches, otherwise offered
   as another option. Replaces v2 `lineVariants`, `noPrice` (a `price: false` variant with its own pool) and the
   caption `captions` options.

```json
"versions": [
  { "line": "{venue.name}. I came here for {menuItem.name}.", "caption": "{venue.name}", "card": "{venue.name}" },
  { "line": "Morning stop at {venue.name}.", "caption": "{venue.name}", "card": "Morning at {venue.name}", "tags": { "daypart": "morning" } },
  { "line": "Breakfast at {venue.name}.", "caption": "{venue.name}", "card": "{venue.name}", "tags": { "menuSection": "breakfast" } }
]
```

The checker runs L1-L14 on every version of every variant and times the step by its longest version, with the
longest choice option and the 40-character typed name in.

## 5. Choice sets: opinions and amenities (Agreed 2026-11-16)

`opinionSets` become `choiceSets`; a step's `choice: {set, preselect, order}` fills one slot in its line and card.

- Opinion steps (Agreed 2026-11-16): every opinion step offers **5 levels** from negative to positive plus typing
  your own. The words are not one fixed list: each step and kind gets synonyms that fit it (a dish verdict, a drink
  verdict, a venue subject's verdict, a first bite). Modelled as a choice set with 5 ordered levels:

```json
{ "id": "verdict_dish", "kind": "verdict", "levels": [
    { "level": 1, "tone": "negative", "text": "Not again." },
    { "level": 2, "tone": "negative", "text": "Once was enough." },
    { "level": 3, "tone": "neutral",  "text": "Maybe, to try more." },
    { "level": 4, "tone": "positive", "text": "I would." },
    { "level": 5, "tone": "positive", "text": "Definitely." } ],
  "allowCustom": true, "preselect": null, "privateFeedback": { "label": "Not for me" } }
```

  Words above are placeholders for the shape; the v3 rewrite writes the per-step sets. Nothing is preselected on a
  verdict. "Not for me" (private feedback) stays as an extra chip beside the 5 levels (Agreed 2026-11-16).
  Levels and tones are for analytics only and never affect the edit, music or ranking.
- New kind `amenity`, slot `{amenity}`: options are the platform amenities from the business `amenityList`
  (`id title iconUrl slug sort`); the business's own come preselected; custom text allowed; every option tone is
  neutral (a fact). Example line: "{amenity} here." / "Free Wi-Fi here."
- Prod data 2026-11-16: 44 of 652 venues list amenities, 5 kinds only: parking_available 35, free_wifi 24,
  non_smoking 20, pet_friendly 20, baby_friendly 11. A creator may pick one the business does not list, as their own
  filmed observation (Agreed 2026-11-16). The list grows from the backend without app work.
- Non-smoking cannot really be filmed (owner 2026-11-16: "how can user show it? IDK"). Agreed 2026-11-16:
  P0 offers 4 chips (parking, free Wi-Fi, pet friendly, baby friendly); non_smoking goes to the AI writer as a fact
  only.
- Owner 2026-11-16: amenities in P0 "if we can", "texts with opinion on UI (where user can select or type)".

## 6. Subjects

### Dish and drink kinds (Agreed 2026-11-16)

One kind, a one-tap chip (single choice), drives guides and texts (Agreed 2026-11-16). No descriptor tags: the
Figma's Fresh and Unique meant kinds (fresh juice, signature cocktails); "signature" is a label, not a kind (a
signature cocktail is a cocktail, a signature latte is coffee). Owner 2026-11-16: "Overall your list looks better."

| Dish kind | Serving form |
|---|---|
| starters and sides | plated |
| soups | bowl (spoon) |
| bowls and sushi (Asian) | bowl or plated (chopsticks or fork) |
| mains | plated |
| salads | plated |
| pizza | plated (cut, one slice pulled) |
| handhelds (burgers, tacos, sandwiches, wraps) | handheld |
| pastry and bakery | plated, dessert plate, no cutlery |
| desserts | plated, dessert plate |
| breakfast | plated, dessert plate for pancakes |

| Drink kind | Covers | Serving form | Example words for the 5 opinion levels (low to high) |
|---|---|---|---|
| coffee | espresso, latte, cappuccino, flat white | cup | too bitter, not my cup, decent, smooth, perfect brew |
| tea and matcha | tea, chai, matcha | cup | too weak, plain, nice, fragrant, so soothing |
| iced and cold coffee | iced latte, cold brew, frappe, bubble tea | glass with straw | too sweet, watery, fine, refreshing, so good |
| juices and smoothies | fresh juice, smoothies | glass with straw | too sour, plain, fresh, fruity, just right |
| soft drinks and lemonades | lemonade, soda, kombucha, iced tea | glass | flat, too sweet, okay, refreshing, perfect |
| beer and wine | draft, cans, flights, wine by the glass | glass, pour | not for me, plain, decent, crisp, great pour |
| cocktails and mocktails | cocktails, signature drinks, shots, mocktails | glass, garnish | too strong, plain, balanced, great mix, perfect |

Soups and bowls are separate because soup is spooned and bowls or sushi are eaten with chopsticks or a fork; hot and
iced coffee are separate because the form differs (cup with steam vs glass with straw); coffee and tea are separate
for their opinion words and the writer's vocabulary. Kind names and their examples double as menu-section keywords.
Alcohol kinds (beer and wine, cocktails): P1 (Agreed 2026-11-16, owner: "Alcohol in P1"; US rules summarised in the doc's Decisions tab). Mocktails move under soft drinks and lemonades for P0 (Assumed 2026-11-16).

Wraps are handhelds (Agreed 2026-11-16).

Menu section -> kind: a mapping table of section names (English and Ukrainian stems, as the daypart mapping does);
unknown sections give plain "dish" plus a one-tap kind chip (Agreed 2026-11-16).

### Venue subjects (Agreed 2026-11-16, chosen by category)

| Subject | Pattern | Categories | Live venues |
|---|---|---|---|
| dineIn | product | dining, food-and-drinks, food-and-drinks-family, craft-beer | ~410 |
| counter | product | coffee, bakery, fast-food | ~60 |
| truck | product | food-truck | 23 |
| result | before -> process -> **after** | beauty, beauty-salon, beauty-barbershop, beauty-nails, services-cleaning, cars, shopping-auto, garden-n-landscaping, services-pet, services-photography | ~140 |
| shopping | browse -> **the find** -> checkout or bag | shopping, clothing-shops, shopping-music, shopping-pet-store, book-stores, thrift-shops, vintage-shop, knick-knacks, grocery, farmers-market, beauty-products, shopping-recreational, shopping-other, arts-and-crafts | ~135 |
| experience | getting ready -> **in action** -> after | sport_health, entertainment, recreational, recreational-other, events, events-*, parks, site-seeing, places, services-education | ~100 |
| visit | meet the team -> **what they do** -> the takeaway | services-health, services-legal, business-services, real-estate, career-n-business, services, services-other | ~50 |

Counts from prod 2026-11-16 (652 venues, a venue can have several categories). Child care is out of P0 (Agreed). A
venue with food and non-food categories: food first (Agreed 2026-11-16).

### Visit: no clients in frame (Agreed approach 2026-11-16)

1. Script layer: steps ask only for staff, the space and tools; no before/after of a person; after = the takeaway
   (creator speaking, a leaflet); directions say "keep other visitors out of frame"; guides show no second person but
   staff. Checker: new rule against health or legal outcome claims ("cured my...", "won my case").
2. Consent screen before a Visit review: "Only staff who agreed and the space. No patients, clients or children."
   Checkbox, recorded with the draft. The business approves every video before it goes live.
3. P1: on-device face detection (Vision) with blur-all-but-me.

## 7. Part 2: guides - generic or specific

A guide teaches a camera move. The food on screen matters only where the move depends on how the food is served or
eaten. So guides key on the **serving form** (plated, bowl, handheld, cup, glass), not on the dish; the dish kind only
chooses a cosmetic dish on that form when one is rendered, else the form's default.

| Role | Keyed by | Generic is enough | Needs a specific version |
|---|---|---|---|
| arrive | serviceKind | door and sign for dineIn and counter; all subjects share | truck: the truck from across the street (new scene, truck object) |
| place | serviceKind / venue subject | today's room guides for dineIn | counter and display (counter exists, display case new); truck and standing area; 4 neutral interiors for result, shopping, experience, visit |
| before (food) | serviceKind | menu card at the table (dineIn), menu board at the counter | truck window order |
| main (food) | form | plated: the dish guides with the dish versions (pasta default; pastry, pancakes, pizza, salad drafts 2026-11-14/15) | bowl (steam over a bowl), cup (steam, top orbit: exist), glass (glass slide: exists), handheld (hold and turn, paper open: briefed) |
| after (food) | form | none: the move is the bite | fork (plated: exists), spoon (bowl, dessert), hand (handheld, pastry, pizza slice), sip from cup (exists), sip from glass / straw |
| main / before / after (non-food) | pattern | stand-ins: a person in a chair, a generic product box, a person in motion, a desk | one set of about 3 per pattern |
| amenities | none | one detail guide (point at the thing: sign, bowl, high chair) | parking: one exterior pan |
| verdict | subject | creator to camera; object in frame by form optional | owner doubt 2026-11-15 on the held plate: plate-on-table version under review |

Decisions this implies:
- Dish versions are cosmetic only and never block a step: a kind without a rendered dish uses the form default.
- Food and drink do not need separate guide libraries: they share arrive, place, before, amenities and verdict; only
  main and after switch by form.
- Owner 2026-11-16: "let's make generic as possible" for the new non-food guides.

Work list (estimate, all objects as OBJECTS.md requests first, owner approves line art):

| Item | Guides | New objects |
|---|---|---|
| truck (arrive, place, before) | 3 | food truck with a service window |
| counter display (place) | 1 | display case |
| bowl form (main, after) | 2 | bowl approval (Tripo serving_bowl exists, unapproved), spoon (teaspoon request open) |
| glass sip (after) | 1 | straw (optional) |
| handheld (main, after) | 3 (2 briefed) | paper wrap and tray (requested), burger approval |
| non-food interiors (place) | 4 | salon chair and mirror, shelves, reception desk |
| non-food patterns (before, main, after) | about 12 | generic product box, stand-in poses |
| amenities | 2 | none |
| total | about 28 | about 8 |

## 8. Part 3: texts - by name, kind, subject

| Level | Where it changes the text | Where it does not |
|---|---|---|
| Dish name `{menuItem.name}` | a slot only: order line, main card, after line, verdict caption | never authored text per name (infinite and unknown) |
| Dish or drink kind | 3 places, as `variants` keyed by kind (never by form): the after line and title (First bite / First sip / First spoonful), the main direction (pour, break it open, cut, top-down), the opinion words (5 levels worded for the kind) | arrive, place, before, amenities |
| Subject (dish, drink, venue subject) | verdict object ("Would I come back for it?" vs "...here?"), step titles, the pattern's before/main/after lines | arrive |
| Service kind | place and before directions and lines ("at the window" / "at the counter" / "at the table") | main, after, verdict |
| Price | `price: false` variant (no price, no "worth the price") | everything else |
| Daypart, menu section | tagged versions in the step's pool: preselected when they match, otherwise offered as other options (Agreed 2026-11-16) | the neutral versions |
| Variety | every step has a pool of versions; the app preselects one and offers the rest (Agreed 2026-11-16) | the structure (steps, roles, guides) |

So: a name needs no texts; a kind needs about 3 variants per script (via `kind`, `dishKind` or `drinkKind` in
`variants`); every step has a pool of a few versions for variety. Typed names are timed at the 40-character cap as in v2.

## 9. Open items

| Id | Question | Status |
|---|---|---|
| v3-verdict-chips | Figma adjectives or v2 answers | Agreed 2026-11-16: 5 levels from negative to positive, synonyms fitted to each step and kind, plus your own words; "Not for me" kept beside them (Assumed, owner to confirm) |
| v3-locations | Locations script | Agreed 2026-11-16: skipped for now |
| v3-rolls | "rolls" | Agreed 2026-11-16: sushi -> dish kind "sushi and Asian"; wraps -> handhelds |
| v3-menu-fallback | unknown menu section -> plain dish + kind chip | Agreed 2026-11-16 |
| v3-amenity-unlisted | a creator may pick an amenity the business does not list | Agreed 2026-11-16 |
| v3-amenity-nonsmoking | non-smoking cannot be filmed: 4 chips in P0, non_smoking to the AI writer as a fact | Agreed 2026-11-16 |
| v3-drink-kinds | drink and dish kind lists (section 6) | Agreed 2026-11-16: owner "your list looks better" |
| v3-alcohol | beer and wine, cocktails in P0 or P1 (US alcohol advertising rules, see the doc's Decisions tab) | Agreed 2026-11-16: P1; mocktails under soft drinks for P0 (Assumed) |
| v3-text-versions | per-step version pools, preselect by tags then rotate | Agreed 2026-11-16 |
| v3-sticker-cta | A "Call to action" sticker is a sticker the creator places in the editor with words like "Visit us" or "Order now". Our caption rule (L4) bans calls to action in captions we write. Proposal: allow CTA stickers as the creator's own choice; the catalog never writes one | Agreed 2026-11-16: allowed as the creator's own choice; the catalog never writes a call to action |
| v3-mixed-venue | venue with food and non-food categories: food first | Agreed 2026-11-16 |
| v3-guide-work | the work list in section 7 (about 28 guides, about 8 objects) | Agreed 2026-11-16: approved; objects still go through OBJECTS.md approval |
| v3-old-ids | mapping from v2 ids | Agreed 2026-11-16: dropped, nothing on the real backend yet |

## 10. What the v3 catalog rewrite will do (next step, after the owner reviews this file)

Snapshot first (done: `scripts/versions/v2_2026-11-16/`). Then: four kind scripts in `scripts/_parts`; step roles
and `required`; `variants` replacing lineVariants, noPrice and servingVariants; `choiceSets` with the amenity set;
dish and drink kind tables, per-step 5-level opinion sets, per-step version pools, menu-section mapping, venue subject table by category; checker rules for roles, variants,
choice sets and the Visit claims rule; build_bundle and the Scriptwriter writer; catalog version 3; review site; app
handoff rewrite; CHANGELOG entry.

## 11. Owner answers 2026-11-16 (summary)

1. Opinion chips: 5 levels per opinion step plus typing your own; wording fitted per step and kind.
2. Text variety: a pool of versions per step; preselect the most relevant, others as "Other options".
3. Role `main` is required for dish, drink and menu item.
4. Variant `when` keys use the kind, not the serving form; daypart and menu section tag versions, no automatic switch.
5. Non-smoking: cannot be filmed; proposal recorded (4 chips).
6. Fresh and Unique are kinds, not descriptors; one-tap kind chip.
7. Daypart texts: offered as other options, preselected when they match.
9. Verdict: 5 levels with fitting synonyms; rolls = sushi; menu fallback, unlisted amenity, mixed venue agreed; guide
   work approved; old ids dropped; sticker CTA explained, open.

9a. 2026-11-16 (closing the review): alcohol kinds in P1; creator-placed call-to-action stickers allowed; "Not for me" kept; non-smoking as an AI fact only.

## 12. Catalog v3 built (2026-11-16)

- Source: `scripts/_parts/v3/` (`dish-review.json`, `drink-review.json`, `menu-item-review.json`, `venue-review.json`
  written by `author.py`; `choice_sets.json`, `tables.json`). Built by `check_scripts.py --v3 --merge` into
  `scripts/catalog_v3.json` (0 errors); bundled by `build_bundle.py --catalog-version 3` as `catalog_v3.json` (not
  published). v2 is built and served unchanged.
- 4 kinds, 21 steps, 271 versions (bases and variants), 18 choice sets (7 verdict sets, 9 first-bite or first-sip
  sets, `place_word`, `amenities`).
- Checker: `scripts/tools/v3_catalog.py` (V1-V12 plus L1-L14 on every version of every variant), tests
  `scripts/tools/test_v3.py` (21). Menu section mapping `v3_catalog.menu_kind`.
- Guide gaps: `research/v3_guide_work.md` (30 gaps; every step allows "No guide").
- Assumed: mocktails count as soft drinks and lemonades in P0; the verdict and reaction level words (owner to review).

## 13. No step pictures (Agreed 2026-11-17)

D-no-step-pictures (owner 2026-11-17: "we don't use any pictures anymore (see designs)"). Figma 291:3905 shows each
step as an icon in the progress list and the guide carousel in the camera; there is no step picture anywhere. Motivation:
the design has no slot for one, the guide carousel already shows what to film, and dropping the pictures saves art
production and payload. v3 steps carry no `imageURL`, `picture` or `preview` field; the v3 checker rejects them
(V1). Menu-item photos in the dish list come from the venue's menu, not from the catalog. The step-previews skill is
not used for v3 (kept for v2 and reference). v2 keeps its step art as the rollback.


## 14. No guide descriptions in the client (Agreed 2026-11-17)

D-no-guide-descriptions (owner 2026-11-17: "we also don't have animation descriptions on designs"). The Figma camera
screens (291:4718, 4759, 4800, 4839) show the guide carousel with only a short label per guide ("No guide", "Door,
low", "Sign tilt", "Walk in"). Motivation: the design shows only that label; the animation itself is the instruction.
The client payload of a guide carries: id, `label` (about 2-3 words, at most 14 characters), animation and poster,
durationSec, startTrigger, phoneOrientation, camera and capture preset, showsFace, needsHelper, guideVisibleToCreator,
units and zoomHint, forSteps, serviceKind or subject, dishVariants, availability. Title, invariant, technique, beats
text and sourceSetup are authoring-only: they stay in the repo records and are not sent. Beats: today's app shows beat
text while recording a complex step (ScriptStudio StepCameraView, "1/3 · ..."); the design has no such text, so beats
leave the payload entirely (no timing-only beats: nothing in the design uses their timing). Proposed labels for every
guide: guides/p0/guide_labels.json (proposed, owner review).

## 15. "No guide" is always first; one guide list per step (Agreed 2026-11-16)

- **D-no-guide-always-first.** The guide carousel starts with "None / No guide" on every step, as in the design
  (Figma 291:4718, 4759, 4800, 4839). The catalog drops `noGuideAllowed` (it was always true); an empty `guides` list is
  valid and means the carousel shows only "No guide". Motivation: the flag told the client nothing.
- **One guide list per step.** The client shows the `guides` of the first variant whose `when` matches, else the base
  `guides`. Sample step files no longer carry a flattened `variantGuides` list; they show each variant's `when` and
  `guides`. Motivation: a merged list lost which venue each guide belongs to.

## 16. Frozen kinds, two request shapes, the backend resolves (Agreed 2026-11-16)

- **D-kinds-frozen.** Dish kind ids: starters-sides, soups, bowls-sushi, mains, salads, pizza, handhelds,
  pastry-bakery, desserts, breakfast. Drink kind ids: coffee, tea-matcha, iced-coffee, juices-smoothies, soft-drinks,
  beer-wine (P1), cocktails (P1). Ids are never renamed or removed: a new kind is a new id (bump `kindsVersion`); a
  removed kind stays with `deprecated: true` and `replacedBy`. Labels (`labels.en`, `labels.uk`) are separate from ids
  and may change. Frozen list: `scripts/kinds_frozen.json`; checker rule V13 rejects a renamed, removed or unlisted id.
  Motivation: the ids travel through the API in both directions (app to backend, backend from menu items), so a rename
  would silently break old drafts, analytics and venue settings.
- **D-two-request-shapes.** Same ids in both. A) The app knows the kind: `{kind, dishKind | drinkKind, serviceKind |
  subject, price, businessAmenities?}` (`daypart`, `typedName` optional, they do not change the steps). B) From a menu
  item: `{kind: "menu-item-review", serviceKind, menuItem: {name, price, section, videoKind?}, kindChip?}`; the kind is
  taken in this order: the creator's kind chip, the item's `videoKind` (proposed optional field the venue sets), the
  menu section keyword match (`tables.menuSectionMapping`), the fallback (dish review, no kind, the app shows the
  chip). The chip choice is sent back with the request and stored with the draft. Motivation: either side may know
  the kind first; one id set covers both.
- **D-backend-resolves.** Replaces "the app evaluates the variants" (section 4, 2026-11-16). The backend applies the
  first matching variant per step, inlines the choice set and returns the script in the shape of
  `backend_examples/v3/resolved_*.json`. The reference resolver and 7 fixtures are the spec:
  `backend_examples/v3/resolver/` (`test_fixtures.py`, 7 of 7 pass). The app keeps the full catalog only as an offline
  fallback and runs the same logic there. Version preselection (tags first, random among equals) stays in the app.
  Motivation: one place to change resolution rules and to read analytics; the app stays thin.
