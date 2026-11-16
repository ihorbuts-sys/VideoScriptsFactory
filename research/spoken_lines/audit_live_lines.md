# Audit: live spoken lines vs the evidence patterns

> Superseded 2026-11-13 (opinions handoff): a missing positive ending is no longer a fault; judgements move into `{opinion}` slots the creator fills, nothing is prefilled. The P0 rewrite and its rule per line are in `research/p0_opinion_rewrite_changes.md` and `scripts/tools/line_lint.py`.

2026-11-11. The 28 spoken lines of the 7 live scripts (`scripts/_parts/food-review.json`: food-review, -drink, -pour,
-sweet, -handheld, -table; `scripts/_parts/coffee.json`: first-visit; the other coffee templates have no spoken lines)
checked against `patterns.md`. Words and seconds from `scripts/tools/step_fields.py` (`slotted_words`, `line_seconds`).
Every rewrite is a **proposal only**; nothing in the scripts was changed. All proposals were measured: 7-15 words,
under 80 characters, 4-7 s.

Verdicts: **matches** (follows a fitting pattern), **weaker** (a fitting pattern does the job better), **breaks** (breaks a
rule in `patterns.md`: a claim a visitor cannot make, a teaser with no payoff [F11], or no positive ending where the owner
wants one).

## Summary

| Result | Lines |
|---|---|
| Matches | 12 |
| Weaker | 11 |
| Breaks | 5 |

Main issues, by count:
1. Teaser tails with no payoff ("Here's how it tastes", "Here's the texture", "Here's whether one is enough", "Here's why
   I'd come back", "Here's when happy hour starts"): 9 lines. Real reviewers say the sensation itself (B1, S1); a fixed line cannot know it (patterns.md,
   finding 1). This needs an owner decision, not only rewrites: keep a short neutral frame and let the creator add the
   reaction, or use a question that stays true whatever the answer (B4, V1).
2. Claims a first visit may not support: "the one everyone told me about", "The barista says it's their best", "Come
   early, they sell out", "Here's when happy hour starts", "a table by the window": 5 lines.
3. Verdict endings: three verdicts end on no positive word (pour, sweet, handheld) and one more teases (first-visit);
   "Certainly" (food-review) has no evidence. Proposed endings, one per template, all evidenced: Absolutely (LR13),
   Definitely (LR36, LR38), Cheers (LR39), Worth every bite (LR62), Legit (LR8), Worth it (LR67), Highly recommend
   (LR9, LR37).
4. No line mentions the Loca deal, and none carries a disclosure; see patterns.md "Disclosure and claims" (owner and
   legal decision).
5. Repeated wording across templates: "First sip of the {menuItem.name}. Here's how it tastes / what it tastes like"
   (drink, pour) and "I'm here for the {menuItem.name}" (food-review, handheld). Same pattern is fine; the same words in
   sibling templates make the family feel canned **(judgement)**.

## Line by line

| Template / step | Live line | Words / s | Result | Pattern and why | Proposal |
|---|---|---|---|---|---|
| food-review / arrive | {venue.name}. I came here for one thing: the {menuItem.name}. | 11 / 6 | matches | H2 deadpan intent (LR43, LR48, LR63); true for anyone who picked the item. | keep |
| food-review / order | Getting the {menuItem.name}, the one everyone told me about. | 10 / 5 | breaks | O1 plain order, but "everyone told me about" is a claim the creator may not be able to make (H4 needs a true reason). | Getting the {menuItem.name}. I picked it off the menu myself. |
| food-review / bite | First bite of the {menuItem.name}. Okay, here's my honest reaction. | 11 / 6 | weaker | B1 frame, but the tail announces a reaction instead of giving one (teaser). | First bite of the {menuItem.name}. Okay. Does it taste as good as it looks? (15 words, 7 s; step is 6 s) |
| food-review / verdict | {menuItem.price} at {venue.name}. Would I come back for it? Certainly. | 11 / 6 | weaker | P1 + V1, the best-fitting verdict shape; "Certainly" has no evidence, "Absolutely" does (LR13). | {menuItem.price} at {venue.name}. Would I come back for it? Absolutely. |
| food-review-drink / order | Getting the {menuItem.name}. The barista says it's their best. | 10 / 5 | breaks | O1, but it puts a superlative in the barista's mouth; only true if said. | Getting the {menuItem.name}. Asked the barista what they recommend. |
| food-review-drink / pour | Watching them make the {menuItem.name}. Look at that pour. | 10 / 5 | matches | D1 point the viewer (LR37, LR47, LR61). | keep |
| food-review-drink / sip | First sip of the {menuItem.name}. Here's how it tastes. | 10 / 5 | weaker | S1 evidence names descriptors (LR36, LR37, LR54, LR55); the tail is a teaser. | First sip of the {menuItem.name}. Okay, let me tell you. (V6 lead-in, LR35; the creator finishes it) |
| food-review-drink / verdict | {menuItem.price} at {venue.name}. Would I order it again? Definitely. | 10 / 5 | matches | P1 + V1; "Definitely" evidenced as an adverb (LR36, LR38). | keep |
| food-review-pour / build | Here comes the {menuItem.name}. Watch them pour it. | 9 / 5 | matches | D1 point the viewer. | keep |
| food-review-pour / sip | First sip of the {menuItem.name}. Here's what it tastes like. | 11 / 6 | weaker | Same teaser as drink/sip, near-identical words. Pint lines end on one word (LR57, LR64). | First sip of the {menuItem.name}. Does it taste as good as it looks? |
| food-review-pour / verdict | {menuItem.price} at {venue.name}. Here's when happy hour starts. | 9 / 5 | breaks | Assumes a happy hour exists and does not say when (teaser, claim); no positive ending. | {menuItem.price} at {venue.name}. Would I get another round? Cheers to that. (12 words, 6 s) |
| food-review-sweet / case | Picking the {menuItem.name} from the case. | 7 / 4 | matches | O1 with an action; under the 8-word target but fits a 4 s step. | keep |
| food-review-sweet / taste | First bite of the {menuItem.name}. Here's the texture. | 9 / 5 | weaker | B2 names the texture (LR3, LR8, LR37, LR48); this teases it. | First bite of the {menuItem.name}. Okay, look at that inside. (D1 on the break; 11 words, 6 s) |
| food-review-sweet / verdict | {menuItem.price} at {venue.name}. Come early, they sell out. | 9 / 5 | breaks | A first-timer cannot know it sells out; no positive ending. | {menuItem.price} at {venue.name}. Honestly? Worth every bite. (P4, LR62) |
| food-review-handheld / window | Lunch at {venue.name}. I'm here for the {menuItem.name}. | 10 / 5 | matches | H2; "Lunch" assumes the time of day (minor). | keep, or drop "Lunch" if filmed at night |
| food-review-handheld / bite | Two hands for the {menuItem.name}. First bite. | 8 / 5 | matches | B1 frame with a size cue (LR7). | keep |
| food-review-handheld / verdict | {menuItem.price} at {venue.name}. Here's whether one is enough. | 9 / 5 | weaker | Portion is a real value frame (LR23, LR62), but the line withholds the answer; no positive ending. | {menuItem.price} at {venue.name}. Big enough for lunch, and legit good. (P3 + "legit" LR8; still a prefilled claim) |
| food-review-table / action | The {menuItem.name} just hit the grill. Listen to that. | 10 / 5 | matches | D1 point the viewer (sound). Assumes a grill: only true for grill tables. Note: 10 words need 5 s and the step has 4 s; `check_scripts.py` reports no error, so check how it counts. | keep for grill venues |
| food-review-table / how | Here's how ordering works and what comes to the table. | 10 / 5 | weaker | O2 gives the fact ("It's 90 minutes, all you can eat" LR35; "2-hour time frame" LR63); this line only promises it. A fixed fact would be a claim; owner decision (a venue field or ad-lib). | How it works here, in my own words. (judgement, main agent 2026-11-11: a frame the creator finishes with the real ordering fact; no evidenced line exists) |
| food-review-table / bite | First bite of the {menuItem.name}. Okay, that is good. | 10 / 5 | matches | B1 ("that's really good" LR47, "Pretty good" LR2); the tail is a prefilled opinion. | keep |
| food-review-table / verdict | {menuItem.price} per person at {venue.name}. Worth it with friends. | 10 / 5 | matches | P2 value against the format (LR67, LR35, LR28): the best-evidenced value frame. | keep |
| first-visit / entrance | First time at {venue.name}. Let's see if it's worth the hype. | 12 / 6 | matches | H1 stated test (LR52, LR48, LR10); pairs with V4. | keep |
| first-visit / counter | Asking the barista what first timers should order here. | 9 / 5 | weaker | Narrates an action (honest), but no corpus line shows asking staff (judgement); O1 names the order. Coffee only. | First time here, so I asked the barista what to get. (judgement, main agent 2026-11-11: says why they ask, no claim about the answer; no corpus line shows asking staff) |
| first-visit / menu | Asking what the kitchen here is known for. | 8 / 5 | weaker | Same shape as the counter line one step earlier; M1 talks about the menu itself (LR35, LR37). | Asking the kitchen what they are known for. Lots of options here. (12 words, 6 s; "lots of options" is a mild claim) |
| first-visit / sip | Okay, first sip. Here's how it tastes. | 7 / 4 | weaker | Teaser (S1). | Okay, first sip. Let me tell you. (7 words, 4 s) |
| first-visit / forkful | First forkful of what they told me to order. Okay. | 10 / 5 | matches | B1 with a neutral tail; ties back to the counter step. | keep |
| first-visit / room | Grabbed a table by the window. Here's the room. | 9 / 5 | breaks | "by the window" may be false; "Here's the room" names no feature (R1, R2). | Grabbed a table. Love the vibe in here. (R2, LR5, LR9; 8 words) |
| first-visit / verdict | That's {venue.name}. Here's why I'd come back. | 8 / 5 | weaker | Teaser with no reason and no positive word; C1 / V3 close softly (LR35, LR36, LR9, LR37). | That's {venue.name}. If you're nearby, I'd highly recommend it. (13 words, 7 s; step is 6 s) |

Proposals that need longer steps (7 s against 6 s now): food-review/bite and first-visit/verdict. Shorter alternatives
if the step must stay: "First bite of the {menuItem.name}. Okay. As good as it looks?" (owner choice).
