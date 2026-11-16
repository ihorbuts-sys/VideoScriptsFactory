---
name: script-writer
description: Writes the shooting directions, on-screen texts and prompter lines for the steps of a short venue video script (cafe, restaurant, bakery, bar, salon). Use when a request lists script steps to fill.
---

# Writing a venue video script

A content creator records a short vertical video (15-60 s) about a venue, one step at a time,
reading from a prompter. You write, for each requested step, what and how to film, the text
shown on the video, and the lines to say.

## Input

- **Venue**: facts about the venue (name, kind, description, location, price, amenities, review
  summary, menu or website link), or "unknown".
- **Request** (JSON): `venueKind`, `language`, optional `mood`, `targetSeconds` (the length of
  the whole video), the `script` (title, summary) and
  its `steps` in order. A step has `id`, `title`, `shot` (wide, medium, close, detail, selfie),
  `seconds`, the current `direction` and `prompter`, `pip` (the front camera films the creator
  in a window while the back camera films the scene) and `isOwn` (the creator wrote the step).
  `only`, when present, lists the step ids to write; the other steps are context.
  `menuItem`, when present, is the dish or drink the video reviews (name, description, section,
  price, dietary tags).
  A step may carry `opinion` (`set`, `options`: the answers the creator can pick, such as "Certainly.",
  "Maybe, for the price.", "Not for me"): the step ends on the creator's own judgement.
  `daypart`, when present, is the time of day the video is filmed: `morning` (opening to 11:00),
  `midday` (11:00-16:00) or `evening` (16:00 to close), in the venue's time zone. The server sets it
  from the app's capture time, else from the menu item's section (breakfast, lunch, dinner).

## Output

One entry per step to write, same `id`, in script order:

- `seconds`: how long the step runs, whole seconds from 2 to 15. All steps of the script
  together (the steps you write plus the `seconds` of the steps given as context) come within 10%
  of `targetSeconds`; give more time to the steps that carry the story.
- `direction`: what to film and how, 1-2 sentences, under 220 characters. Name the subject, the
  camera position (eye level, low, high, overhead), the distance matching `shot`, and the
  movement (static, slow push in, pan, follow). With `pip`, say what the back camera films and
  that the creator talks to the front camera.
- `onScreenText`: 2-5 words shown on the video, or null when the picture says it alone or the
  creator is talking and text would compete. Facts only: the venue name, the dish, the price, what
  the step shows ("Ordered: {menuItem.name}"). Never an opinion, a question or a call to action. No
  hashtags, no emoji, no quotation marks.
- `card`: at most 6 words, shown instead of the spoken line when the creator films silently;
  written style, the same slots as the line, and the same `{opinion}` slot when the step has one
  ("Would I come back? {opinion}"). Null for a step the picture explains alone.
- `prompter`: what the creator says, as parts:
  - `{"type": "say", "text": "..."}` words to read,
  - `{"type": "pause", "seconds": 0.5-1.5}` a breath between two thoughts, never first or last,
  - `{"type": "cue", "text": "..."}` a short action or look ("smile", "lift the cup"), not read
    aloud; at most two per step.
  Never empty: a b-roll step (`detail`, `wide` without `pip`) gets a voice-over the creator says
  while filming.

## Rules

- Fill the time: speaking takes 40-80% of the step's `seconds`, counting 2.5 words a second plus
  the pauses. A 10 s step has 10-20 words.
- Speak like a real person filming on their phone: first person, present tense, short sentences.
- Tell one story across the steps: arrive, order, show, the creator's reaction, the verdict.
- The script is written before the visit: you supply the frame and the facts, the creator supplies
  the judgement. Never write how it tastes, whether it is good, whether the creator liked it or will
  come back, or what the staff or other people said ("the barista says", "everyone told me",
  "their famous"). With an `opinion` on the step, end its spoken text with exactly one `{opinion}`
  slot after a neutral frame ("First bite of the {menuItem.name}. {opinion}", "Would I come
  back? {opinion}"); the slot never goes into `onScreenText`. Without one, end on a fact or a
  plain question the creator answers in their own words, and never write the slot.
- Slots: `{venue.name}`, `{menuItem.name}`, `{menuItem.price}` and `{opinion}` only. There are no
  short names, so keep the frame short enough that a long venue and dish name still fit 8 s.
- No teaser tails that promise without saying ("Here's how it tastes", "Here's why I'd come
  back", "Let's see if it's worth the hype"); say the thing or ask the question.
- Directions use US units ("about 2 feet away") and ask only for what the script has: the price
  only with a `menuItem` price, never the street or opening hours.
- Use only venue facts from the input or the one page you may open. Never invent dishes, prices,
  awards or opening hours. With an unknown venue, stay generic and never make up a name.
- You may open the venue's menu or website once (WebFetch) when the brief has a link and naming a
  real dish or drink would help. Skip it otherwise.
- `mood` sets the tone: cozy is warm and slow, energetic is quick and upbeat, premium is calm and
  precise, playful is light and funny. No mood: match the venue kind.
- For `isOwn` steps the creator's title and direction are the brief: keep the subject, make the
  direction concrete.
- A `menuItem` with `"source": "typed"` is a name the creator typed (no menu to pick from): only its name is known.
  Use `{menuItem.name}` without "the" before it, never describe it, never assume a plate, fork, cup or hand, and
  never say, show or ask for a price (the server refuses `{menuItem.price}` and "say the price" for it, and for any
  menu item without a price).
- With a `menuItem`, the whole script is about that item: name it in the hook or the order step,
  describe it only from its description, say the price once (in the verdict when there is one),
  and give its hero shot (steam, pour, cut, cheese pull, garnish) in the directions. Keep its
  name as written, even in another language.
- With a `daypart`, write the lines and on-screen text for that time of day, from venue facts only:
  morning ("Starting my morning here", "first coffee of the day"), midday ("My lunch break spot",
  "a quick bite mid-day"), evening ("Ending the day here", "my evening drink"). Never add opening
  hours, a time or a menu the facts do not give. Without a `daypart`, never say or show a time of
  day (no "this morning", "tonight", "lunch break").
- Every limit above still holds with a `daypart`; the server refuses a line over 8 s (2.5 words a
  second plus a 1 s tail, counting the longest `opinion` answer in the slot) or 140 characters, and
  a step that breaks the judgement, hearsay, teaser, caption or slot rules.
- Write `direction`, `onScreenText` and `prompter` in `language`.

## Catalog version 3 requests (2026-11-16)

A request with `kind` (`dish-review`, `drink-review`, `menu-item-review`, `venue-review`) is a v3 request. The server
sends the steps of that kind as the app shows them in the request's context (the first matching variant applied):
key, role, title, whether the step is silent, its direction, its choice set and two example versions.

- Write 3 to 5 versions for every step asked: `line`, `card`, `caption`. A silent step has `line: null`.
- The structure is fixed; only the wording varies, so two videos rarely sound the same. Keep each version in the
  same role and meaning as the examples.
- Slots: `{venue.name}`, `{menuItem.name}`; `{menuItem.price}` only when the context has `price: true`; `{opinion}`
  only where the step has an opinion choice set, at most once; `{amenity}` only in the amenities step.
- Opinion sets have 3 levels (neutral, good, very good) and no negative level; a line must read naturally with
  each of them and with the creator's own words. Never write a negative judgement into a line: a bad experience
  goes to Not for me on the verdict.
- The judgement is the creator's: no adjectives about the food, drink or place outside the slot. No hearsay, no
  teasers, no calls to action, no claims, no time of day unless the request has a daypart. Captions are facts.
- Visit (health, legal, business services): no outcome claims (cured, won my case, guaranteed), no clients in frame.
- Kinds and subjects: `dishKind` (dish-review), `drinkKind` (drink-review; beer and wine, cocktails are P1 and
  refused), `subject` (venue-review: dineIn, counter, truck, result, shopping, experience, visit). A menu-item request
  derives dish or drink and the kind from `menuItem.section`.
- Every version is checked against the catalog rules (`v3_catalog.written_errors`); one failing version fails the step.
