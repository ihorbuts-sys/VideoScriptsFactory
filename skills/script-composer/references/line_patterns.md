# Line patterns for spoken steps

Compiled 2026-11-11 from `research/spoken_lines/patterns.md` (evidence, counts, avoid lists) and `corpus.md` (191
creator lines, 67 creator sources plus 10 guidance sources; refs LR in `research/spoken_lines/sources.md`, F in
`research/sources.md`). Per step: templates easiest and most proven first. Every line must stay at 17 words / 140
characters or under (aim for 8-14), with slots read as two words.

## Rules that apply to every line

1. A line is written before the visit, so it frames the moment or asks a question; it never states a taste, size,
   crowd, staff quote or venue fact the creator may not witness (no "they sell out", "the barista says", "by the
   window"). Real reviewers name the sensation; leave that to the creator (patterns.md finding 1).
2. No teaser tail with no payoff ("Here's how it tastes") [F11]; say the thing or ask the question.
3. No greeting, series count, score, persona catchphrase, "hidden gem", "best in town", "life changing", "100% worth
   it", "must-try", "run, don't walk", "you have to try it" (LR74, LR75, F3, F11).
4. A judgement is never written for the creator (owner 2026-11-13, replaces the 2026-11-11 "positive default"): the
   line ends on an `{opinion}` slot the creator fills from a shared set in `scripts/opinion_sets.json` (verdict:
   `verdict_answer`, never preselected; first bite and first sip: `bite_reaction`, neutral "Okay." may be
   preselected). The script's own positive word goes first in the step's `opinion.order`. Price goes in the caption;
   the spoken price is a short fact, and a step that uses the price carries a `noPrice` variant.
5. A creator who gets the deal or any perk must disclose it in the video (wording with the owner and legal);
   incentives conditioned on positive sentiment are banned in the US (LR68, LR69, N21, N22; UK: LR70). No "I paid
   like everyone else" (LR11) with a deal.
6. Captions are facts only (name, dish, price, what the step shows); no opinion, question or call to action.
7. Every step has a `card` (at most 6 words, same slots and `{opinion}` as the line) for a silent take; complex steps
   have no line. `scripts/tools/line_lint.py` (L1-L14) checks all of this; P0 must pass it.

## Time-of-day variants (P1)

Owner 2026-11-12: `line` and `caption` are the time-neutral default, shown when the app knows no daypart. An easy
arrive, verdict or room step may add `lineVariants` with a `morning` (opening to 11:00), `midday` (11:00-16:00) or
`evening` (16:00 to close) `line` and `caption`, for example `Morning stop at {venue.name}. I came here for the
{menuItem.name}.`; skip a daypart that says nothing new (null). Same caps as any line (8-14 words, 17 words / 8 s,
140 characters, no clock times or opening hours), and the step's seconds come from its longest line, so a step's
length never depends on the daypart. The neutral `line` never names a time of day.

## Hook / arrive

1. `{venue.name}. I came here for the {menuItem.name}.` deadpan intent (LR43, LR48, LR63)
2. `First time at {venue.name}. Walking in to see what's on the menu.` stated visit (LR1, LR10, LR13); the old
   "Let's see if it's worth the hype" is a teaser and a crowd claim (L1, L2)
3. `{menuItem.price} for the {menuItem.name}.` price first, as a fact (LR20, LR49, LR73); needs a `noPrice` variant
4. `Have you been to {venue.name} yet?` question with "you" (LR36, LR37; one creator; LR72)

## Order

1. `Getting the {menuItem.name}.` + an action or a true reason (LR19, LR20, LR39, LR47)
2. `Here's how it works: {fact}.` only with the fact in the line (LR37, LR39, LR63)
3. Advice ("Order the X") belongs in the verdict, after tasting (LR45, LR49)

## Menu (thin evidence)

1. `Picking from the menu.` + what you are ordering (LR35, LR37, LR39); "So many options" is a judgement

## Dish reveal / pour / build

1. `Look at the {menuItem.name}.` / `Look at that pour.` / `Listen to that.` point the viewer (LR37, LR47, LR61)
2. `That looks {adj}.` is a judgement: P1 only, through an opinion slot (LR3, LR8, LR20, LR51)

## Sip

1. `First sip at {venue.name}. {opinion}` with `bite_reaction` (P0); P1 adds `taste_descriptors` (multi-select,
   never preselected) (LR35)
2. Descriptors ("smooth, balanced, not too sweet") are the creator's pick or own words, never prefilled (LR36, LR37,
   LR54, LR55)

## First bite

1. `First bite of the {menuItem.name}. {opinion}` with `bite_reaction` (LR2, LR8, LR9, LR47, LR48, LR60)
2. Texture or part named ("perfect crisp", "the crust") is the creator's ad-lib (LR3, LR8, LR35, LR37, LR48, LR49)

## Room

1. P0: `Grabbed a table. This is the view from my seat.` (fact, no adjective)
2. P1: `The room here: {opinion}` with `place_word` ("Love the vibe" LR5, LR9, LR62 is the evidence for the slot)

## Verdict and price

1. `{menuItem.price} at {venue.name}. Would I come back? {opinion}` with `verdict_answer`, never
   preselected; `noPrice`: `{venue.name}. Would I come back? {opinion}` (short frames so long real names fit 8 s; there are no short names) (LR13, LR5,
   LR22, LR23, LR59; price as fact LR29, LR48)
2. P2: `{menuItem.price} per person at {venue.name}. {opinion}` with `value_word` (LR28, LR35, LR67)
3. Prefilled endings ("Worth every bite", "I'd highly recommend it", "Now I see why people talk about it") are
   judgements or crowd claims: only as options the creator picks, never in the line.

Positive options with evidence (each script puts its own one first in `opinion.order`): Absolutely (LR13), Definitely
(LR36, LR38), worth a visit (LR35, LR36, LR38), worth it (LR62, LR67), so good (LR9, LR37), solid (LR14, LR53),
legit (LR8), Cheers (LR39, drinks). "Certainly" has no corpus evidence; it stays as the handoff's example option.

## Closing CTA

1. `If you're near {venue.name}, it's worth a visit.` is a judgement: only as a verdict option (LR35, LR36, LR38)
2. `Would you try it?` as a spoken tail only, never as a caption (captions are facts) (LR14, LR16; LR72, LR77)
3. `Cheers!` for drinks (LR39)
4. A Loca deal line: one factual sentence, what you get (no corpus evidence; judgement, shape of LR45)
