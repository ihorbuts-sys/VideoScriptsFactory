# Spoken line patterns per step

Built 2026-11-11 from `corpus.md` (201 rows: 191 creator lines, 10 guidance or mocked phrases) and the guidance in
`sources.md` (LR ids). Each pattern names its sources; "Sources" counts distinct LR ids, and "Words" is the range of the
evidenced examples. Anything not backed by a row is marked **(judgement)**. No video was watched: every creator line is a
transcript, an article quote or caption text (see the evidence column in `corpus.md`).

Loca limits used for "Fit": spoken line 8-14 words (owner target), hard limit 17 words and 140 characters (step length =
words / 2.5 + 1 s, max 8 s); a slot reads as a two-word name; one person filming, first-time creator; the venue offers a
Loca deal; the line is written before the visit, so it cannot know the real taste, size or crowd.

## The finding that shapes everything

1. **Real reviewers name the sensation; fixed lines cannot.** The strongest bite and sip lines carry a specific word
   ("So so good, light, crispy" LR9; "smooth, perfectly balanced" LR36; "Doughy" LR8). A prompter line is written
   before the visit, so it can only frame the moment ("First bite of {menuItem.name}.") and leave the sensation to
   the creator, or prefill a word that may be false. Every live line that ends in "here's how it tastes" is this
   tension (see `audit_live_lines.md`). Decided (owner 2026-11-13, opinions handoff): the judgement is the creator's, through an `{opinion}` slot filled from a shared set (`scripts/opinion_sets.json`); nothing is prefilled.
2. **Price is mostly on screen, not spoken.** Of the price evidence, the amount sits in a caption or on-screen text in
   LR23, LR24, LR28, LR57, LR62; spoken price lines exist but are short and paired with a qualifier (LR29, LR35, LR48,
   LR49, LR67). Loca already puts `{menuItem.price}` in the verdict caption, which matches.
3. **Credibility comes from the reviewer paying and judging freely.** Keith Lee's "I pay for my food like everybody
   else" (LR11) and the two-part honest verdict (LR13, LR22, LR23) are the trust devices. A Loca creator who used the
   venue's deal cannot say the first, and a prefilled positive ending works against the second. See Disclosure.

## Disclosure and claims (applies to every step)

- US (FTC): free or discounted products or services are a material connection; disclose it in the video itself (audio
  and on-screen text are both noticed), with words like "ad", "sponsored" or "Thanks to {venue.name} for the free
  {item}"; not "sp", "spon", "collab" [LR68] [N21]. You cannot talk about an experience you did not have, and if you
  thought it was bad you cannot say it is great [LR68].
- US (FTC review rule, effective 2024-10-21): an incentive conditioned, expressly or by implication, on a review of a
  particular sentiment is banned; unconditioned incentives are allowed but must be disclosed [LR69] [N22].
- UK (ASA/CAP/CMA, updated 2026-10): gifted products count as payment; label upfront with #Ad / #Advert; "Sponsored",
  "Spon", "Sp" and "Gifted" are insufficient; paid content must reflect the creator's genuine experience [LR70] [LR71].
- Consequence for Loca **(judgement, needs the owner and legal review)**: if a creator gets the deal, a reward or any
  perk for posting, the video needs an in-video disclosure (caption or spoken); wording and placement stay with the
  owner and legal. A script that supplies praise to an incentivised creator reads as a sentiment condition, so
  (owner 2026-11-13, replacing the 2026-11-11 "editable positive default") no verdict word is prefilled: the verdict
  slot is never preselected, every set has a neutral option and the creator's own words, and the verdict has a private
  "Not for me" path. Catalog v3 (D-3-levels, owner 2026-11-16): sets have 3 levels (neutral, good, very good) and no
  negative level; Not for me on the verdict is the only negative, a private funnel. The script's own positive word is the first option in its `order`, not a default.

## Hook / arrive (28 creator lines, 25 sources, 3-29 words, median 12)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| H1 | `First time at {venue.name}. Let's see if it's worth the hype.` (the stated test) | "One bite, everyone knows the rules!" LR1; "I got it. Let's try it and rate it one through 10." LR10, LR11, LR13; "Is it worth the hype ...?" LR52; "Which gas station has the cheesiest item?" LR21 | 5 | 5-15 | Fits: one person, any venue, 8-12 words. "the hype" assumes the place is talked about (minor claim). |
| H2 | `{venue.name}. I came here for the {menuItem.name}.` (deadpan intent) | "Today, I wanted to eat a croissant. So I went to a place that sells croissant." LR43; "Let's go into Crispy and get us a slice, shall we?" LR48; "We are getting ready to enjoy the all you can eat Korean barbecue and hot pot." LR63 | 3 | 11-20 | Fits best for menu-item scripts: true for anyone who chose the item. |
| H3 | `Have you been to {venue.name} yet?` (question with "you") | "Have you been to Junbi Matcha & Tea in Livermore yet?" LR36; "Have you been to Boba Studio in Walnut Creek yet?" LR37; "If you live in [City] and have not tried this, you are missing out" LR73 (template) | 2 (one creator) + guidance LR72 | 8-11 | Fits the limits; LR72 links "you" in the first 5 s to higher intent (ad study, directional). Thin creator evidence: one creator. |
| H4 | `{Who} told me to try {venue.name}, so here I am.` (reason for the visit) | "Austin's been talkin' this place up" LR7; "She said she was gonna bug me until she hugged me." LR13; "You said the portions are huge, so we're going to find out." LR23; "I was going to an event in Irvine ... and I found all that shabu." LR35; "So a few months ago, I got this month-long membership ..." LR41 | 5 | 6-27 | Fits only as an optional variant: the reason must be true, so a fixed line cannot assert who sent the creator. A neutral form ("Found {venue.name} on my way to ...") still asserts a route **(judgement)**. |
| H5 | `{menuItem.price} for the {menuItem.name}. Let's see if it's worth it.` (price first) | "It ain't cheap. It's not that easy to get a table." LR49; "We spent a lot of money ordering all the most popular items on the menu." LR20; "1-dollar pizza vs 100-dollar pizza. Which is actually better?" LR73 (template) | 3 | 9-13 | Fits the limits; spoken price is rarer than caption price (finding 2). Good for a value-led variant. |
| -- | Greeting opener ("What's good, everybody?" LR19; "Hey everyone, I hope you're having an amazing day." LR61) | | 2 | 3-10 | Does not fit: it spends the 3-6 s proposition window [F1] [LR77] on nothing. |
| -- | Series count ("There are over 100 coffee shops in Baltimore ... every single one" LR54; "When I said I would try every coffee shop in D.C., I meant it." LR56; "part 9" LR55) | | 3 | 3-17 | Does not fit a one-off first-time creator. |

Avoid at the hook: "hidden gem" and "best-kept secret" (mocked: "A hidden gem isn't so hidden if the line is down the
block" LR74; LR73 lists "best-kept secret" as a template, but it is a claim the footage cannot prove [F11]); "best
in [City]" [F11]; "you have to try this" / "run, don't walk" as the opener (LR74, LR75; pushy [F3]).

## Order (10 lines, 8 sources, 6-16 words, median 11)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| O1 | `Getting the {menuItem.name}.` + one true reason or none | "Let me get two Sweetie meals." LR19; "we've ordered slices of lamb beef tendon balls and pork blood" LR47; "I love their pandan foam, so I got extra for topping." LR39; "We spent a lot of money ordering all the most popular items on the menu." LR20 | 4 | 6-14 | Fits: plain and always true. Add 3-6 words of action ("from the case", "at the counter") to reach 8 words. |
| O2 | `Here's how it works: {fact}.` (ordering mechanics) | "You can place an order at the kiosk." LR37; "Choose from almost the entire menu of drinks to make your own custom flight." LR39; "Make sure everyone is here before you get seated because it is a 2-hour time frame." LR63 | 3 | 8-16 | Fits only when the fact is in the line; "Here's how ordering works" with no fact is a teaser (weaker). The fact varies per venue, so it needs a venue field or the creator's ad-lib **(judgement)**. |
| O3 | `Order the {menuItem.name}.` (advice) | "Get the Chinese Mai Tai, not the polished moon." LR45; "Order the Espresso Martini." LR45; "Medium rare to me is the ultimate pro move here." LR49 | 2 | 3-10 | Belongs after the bite, as a verdict (V4): advice before tasting is a claim the visitor cannot yet make. |
| -- | Paid-like-everyone ("I pay for my food like everybody else." LR11; "As you can see, I don't have any bag in my hands." LR11) | | 1 | 11-14 | Does not fit: a creator using the Loca deal cannot say it. |

No corpus line shows a reviewer asking staff what to order; the live "Asking the barista what first timers should order"
is **(judgement)**. Attributing a claim to staff ("The barista says it's their best") is only true if it was said.

## Menu (4 lines, 4 sources, 4-21 words) - thin

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| M1 | `So many options here, {fact}.` | "It's 90 minutes, all you can eat, and there were so many options." LR35; "They had a lot of different options, but I like that they also had a variety of topping options as well." LR37; "Choose from almost the entire menu of drinks ..." LR39 | 3 | 13-21 | Fits when trimmed to one clause. "So many options" is a claim about this menu; likely true for venues with a published menu (17 sampled venues hold 1,937 items, about 114 each on average, `../menu_item_kinds.md`), not for a small one **(judgement)**. |
| M2 | `I'll get the menu.` (bare action) | LR46 | 1 | 4 | Too short for the step on its own. |

## Dish reveal (15 lines, 12 sources, 2-20 words, median 11)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| D1 | `Look at the {menuItem.name}.` / `Look at that {thing}.` (point the viewer) | "And look at the cheese cream foam on my oolong tea." LR37; "all right look at all this food" LR47; "Oh man, that is a swimming pool of chilies." LR61 | 3 | 6-10 | Fits: true for any dish, works with a hold or a tilt. The live "Look at that pour" / "Listen to that" are this pattern. |
| D2 | `That looks {adj}.` (judge the look, then the bite) | "That looks....awesome" LR8; "pizza looks pretty good" LR3; "If we're just looking at this, this looks like it's gonna be knocking on the door of the 8's." LR8; "It looks really good, but really bitter." LR20; "Not only does it look delicious ..." LR51 | 4 | 3-20 | Fits: a look is something the visitor can judge on camera. |
| D3 | `My {menuItem.name} came with {detail}.` (what it is) | "My creme brulee boba came with a little spoon for the caramelized top." LR37; "So all of the components inside the two bowls are edible." LR44; "My favorite was their sea salt caramel banana matcha latte." LR36 | 3 | 10-13 | Needs a detail the script cannot know; creator ad-lib **(judgement)**. |
| D4 | `It's huge.` (size) | "It's huge" / "It's monster" LR7 | 1 | 2-3 | Claim; true only for big items. |

Dish steps are silent (complex) in the live scripts, so D patterns apply mostly to easy pour/build/action steps.

## Pour / sip (7 lines, 7 sources, 1-16 words, median 8; plus 2 verdict lines with sip descriptors)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| S1 | `First sip. {adj}, {adj}, not too {adj}.` (stacked descriptors, often with a "but") | "It's smooth, perfectly balanced, and has the right amount of vanilla to complement the earthy matcha." LR36; "I love how thick and luscious it was." LR37; "The Earl Grey is very fruity, but not in a bergamot way" LR55; "Caramel Latte: 8/10, Flavor's strong but balanced, nothing harsh, just a nice finish." LR54 | 4 | 8-16 | Fits the length, but the descriptors cannot be prefilled honestly (finding 1). |
| S2 | One-word pint verdict | "smooth / creamy" LR57; "gorgeous" LR64; "absolute creamer" LR65 | 3 | 1-2 | Fits a beer step as an ending word; "absolute creamer" is one creator's catchphrase (do not copy). |
| S3 | `It tastes like {comparison}.` | "It honestly just tasted like dessert in a cup." LR38 | 1 | 9 | Claim about taste; ad-lib only. |

## First bite (27 lines, 19 sources, 2-23 words, median 9)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| B1 | `First bite of the {menuItem.name}. {short reaction}.` (reaction word, then detail) | "Pretty good." LR2; "So so good, light, crispy." LR9; "Oh my god. Oh my god." LR48; "Man, I love tendons" LR60; "Tangy sauce. Good crust." LR8; "Okay, that is good" shape: "that's really good" LR47 | 6 | 2-8 | Fits best: short, leaves the sensation to the moment. A neutral tail ("Okay.") keeps it honest; a positive tail ("that is good") is a prefilled opinion **(judgement)**. |
| B2 | Name the part or the texture | "good undercarriage" LR3, LR33; "Big time undercarriage" LR8; "I don't think I've felt a crust like that before." LR48; "the seasoning on this was highly addictive and had a perfect crisp" LR37; "the sauce game was on point" LR35; "It's fresh meat cooked perfectly." LR49 | 6 | 2-14 | Fits as an ad-lib; the texture word depends on the item (`../menu_item_kinds.md` line patterns: flaky, crunchy, cheese pull). |
| B3 | Flavour list | "It's so delicious, it's super salty, super sweet amazing flavours." LR50; "It's spicy, salty, sweet, and fresh all at once." LR51 | 2 | 9-11 | Ad-lib only. |
| B4 | Expectation check | "Does this look heavy and eat light?" LR8; "I like this more than I thought I would coming out of the box." LR8; "it's actually getting better the more I taste it" LR29; "The fries aren't soggy." LR22 | 3 | 5-14 | Fits as a question asked before the bite ("Does it taste as good as it looks?"), which stays true whatever the answer **(judgement on the form)**. |

Avoid: creator personas copied word for word ("undercarriage" is Portnoy's; "Fuiyoh" Uncle Roger's), sexual or extreme
hyperbole ("The dirty, dirty things I would do ..." LR40; "I would sell my soul" LR40; "punch to the face" LR50),
which a first-time creator delivers badly **(judgement)**.

## Room (9 lines, 9 sources, 3-19 words, median 11)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| R1 | `Love the {feature} here. So {adj}.` (feature + adjective) | "This boba shop was so cute. I love their wall design." LR37; "The cups, merch, and overall aesthetics are so fun." LR36; "Environment: Super welcoming & very cozy." LR54 | 3 | 5-10 | Fits; the feature is creator-visible but unknown to the script, so a fixed line names a generic one (light, seats). |
| R2 | `Great vibes here.` (vibe word) | "Great vibes, though" LR5; "I like the vibes." LR9; "the vibes here definitely outshine the food." LR62 | 3 | 3-7 | Fits easily; often a "but" against the food (LR5, LR62), which a promo script should not imply. |
| R3 | Service note | "The staff all works together, and they are very good about making sure they're staying up on the meats" LR35 | 1 (+ negative LR11, LR12) | 19 | Too long; a claim about staff. |

Avoid: positions the creator may not have ("a table by the window"), and room comparisons ("This is a Golden Corral
disguised as a Chinese buffet" LR26).

## Verdict (78 lines, 45 sources, 1-34 words, median 11; 60 of 78 are 14 words or fewer)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| V1 | `Would I {come back / order it again}? {Absolutely}.` (question, then a one-word answer; two-part honest verdict) | "Is it the best rib I've ever had? No. Is it good? Absolutely" LR13; "Tastes good, eats good, a little greasy" LR5; "It's not bad. It's actually better than I expected it to be" LR22; "It tasted good, but it won't be in my top 5 favorites at all." LR23; "I mean, it was cool, but it wasn't crazy." LR59 | 5 | 6-14 | Fits best: short, ends on one word, and the question form leaves room for the creator's honest answer. Only "Absolutely" is evidenced as the one-word answer (LR13). |
| V2 | `I'd come back for the {menuItem.name}.` / `I could've had a second {cup}.` (would-again) | "I could've easily had a second cup." LR62; "and it was so good I can't wait to go visit again soon" LR37; "I could hammer the whole thing." LR9; "just call me when you make it" LR13 | 4 | 6-12 | Fits; a statement of intent, prefilled. |
| V3 | `I'd highly recommend the {menuItem.name}.` / `You can't go wrong here.` | "I like the spot, I'd highly recommend it" LR9; "I would also highly recommend the creamy Americano cloud." LR37; "Regardless of what you order, you really can't go wrong here." LR36; "Order the Espresso Martini." LR45 | 4 | 4-12 | Fits; "can't go wrong" is a claim about the whole menu after one dish **(judgement: weaker)**. |
| V4 | `Now I see why people talk about it.` (hype confirmed) | "I 100% see why 17,000 people told me to come here" LR13; "In this life, there are many things that are hyped and so few things really live up to them." LR48; "Shockingly good from the looks of it." LR8; "It's a pretty good matcha to me" LR52 | 4 | 6-18 | Pairs with hook H1; payoff matches the hook [F11]. |
| V5 | Scoped superlative: `Best {item} I've had {this week / in a while}.` | "Hands down, the best pizza I've had on this trip" LR5; "This was the best pint of Guinness I have ever had." LR58 | 2 | 10-10 | Fits only scoped to the creator's own experience; unscoped "best in town" is avoided [F11]. |
| V6 | `Let me tell you, {verdict}.` | "And let me tell you, it was all that." LR35 (also before the sauce line); "But low-key, I loved it." LR41 | 2 | 5-8 | Fits as a lead-in (3 words). |
| V7 | Score out of 10: `{N} out of 10.` / `This is getting a {N} from me.` | "This is getting a 9.1 from me." LR53; "This is an 8.7 out of 10." LR20; "solid 8" LR14; "This whole place, I give it 9.8 out of 10" LR17; "Honest rating: like a 3 out of 10." LR24; "7.9 review" LR9; "Nine." LR21; caption scores LR54, LR55, LR57 | 12+ | 2-9 | The most common verdict form overall, but it does not fit a prefilled line: the number is the creator's, a low number in a deal-backed video hurts the venue, and a prefilled high number is a fabricated opinion. Could fit as a creator-entered field **(judgement)**. |

### Price and value phrasing (8 sources)

| # | Template | Examples (ref) | Fit |
|---|---|---|---|
| P1 | `{menuItem.price} at {venue.name}.` then the verdict (price as a fact, caption repeats it) | "The cheese pizza is 40 bucks." LR48; "Donuts each cost about three dollars" LR29; "the single burger ... for eleven dollars it was the best burger in LA according to the experts" LR29 | Fits; the live verdict opener. |
| P2 | Value against the format: `{price} per person. Worth it with friends.` / `for all you can eat` / `if you share it` | "And for all you can eat, the meat quality was pretty good." LR35; "I would say it is worth the price if you share it between friends" LR67; "$13.43 for two people" format LR28 | Fits shared tables and big items; the strongest-evidenced value frame. |
| P3 | Plain value adjective: `Affordable, and the portions are big.` / `It ain't cheap.` | "The portions are huge, and the price is affordable." LR62 (written post); "It ain't cheap." LR49 | Claim about value; "affordable" is relative to the viewer **(judgement)**. |
| P4 | `Worth every {bite / penny}.` | "They're thick, gooey, and worth every bite." LR62 (written post); "worth every penny" LR67 (headline) | Fits as a short positive ending. |
| -- | Negative value: "Save your money." LR25 (caption); "this is an insane price." LR66 | Out of scope for venue-backed scripts. |

### Positive ending words with evidence

Evidence for the positive levels of the verdict sets (v2: `verdict_answer`); each script lists its own one first in its verdict `order`
(owner rule 2026-11-13), never as a preselection. Words in order of how cleanly they end a short line:

| Word / phrase | Evidence (ref) | Form seen |
|---|---|---|
| Absolutely | LR13 | one-word answer to the verdict question |
| Definitely | LR36, LR38 | adverb inside "definitely worth a visit / worth checking out" |
| Worth a visit / worth checking out | LR35, LR36, LR38 | closing line |
| Worth it / worth every bite | LR62, LR67 (and mocked as "100% worth it" LR74) | ending; keep it plain, never "100%" |
| So good | LR9, LR37 | reaction and closing |
| Highly recommend | LR9, LR37 | verdict |
| Solid | LR14, LR53 ("very, very solid") | verdict, often with a score |
| Legit | LR8 ("a legit, great pizza") | verdict |
| Delicious | LR13, LR50, LR51 | bite and verdict |
| Spectacular | LR9, LR49 | verdict |
| Fantastic | LR20 | verdict |
| Awesome | LR8 | reveal |
| Amazing / extraordinary | LR51, LR48 | bite / verdict |
| Gorgeous | LR64 | pint |
| On point | LR35 | bite |
| Cheers | LR39 | drink sign-off (a toast, not a judgement) |
| Fire / goated | LR21 / LR26 | slang; avoid for a general audience **(judgement)** |

"Certainly" (used in a live line) has no evidence in the corpus and reads formal **(judgement)**.

Avoid at the verdict: mocked superlatives ("life changing", "100% worth it", "must-try" LR74); unscoped "best in town"
[F11]; claims a first visit cannot support ("they sell out", "the best on the menu", "everyone orders this"); scores the
creator did not choose; "I pay for my food like everybody else" when a deal was used (LR11, LR68).

## Closing CTA (13 lines, 12 sources, 1-13 words, median 9)

| # | Template | Examples (ref) | Sources | Words | Fit |
|---|---|---|---|---|---|
| C1 | `If you're near {venue.name}, it's worth a visit.` | "If you're in the area, it's worth a visit." LR35; "definitely a spot worth checking out for matcha fans" LR36; "boba pup's labubu series is definitely worth a visit" LR38 | 3 (two creators) | 8-9 | Fits best: soft, local, 8-10 words; no hard sell. |
| C2 | Question to the viewer: `Would you try it?` | "would you try it ?" caption LR14, LR16 (Keith Lee) | 2 | 4 | Fits as a caption or a tail; matches the "specific CTA" advice [LR72] [LR77]. |
| C3 | Sign-off: `Cheers!` / city shout-out / `see ya` | "Cheers!" LR39; "Shoutout Pittsburgh coming in huge with some pizza." LR8; "all right guys enjoy your meal next time again invite me see ya" LR47; "I mean no harm" LR11 | 4 | 1-13 | "Cheers" fits drinks; personal sign-offs are a creator's brand, not a template. |
| C4 | Platform plug: `Every spot is on {app}.` | "Every spot is on Atmosfy." LR45 (platform's own account) | 1 | 5 | The only evidence for an app mention. A Loca deal mention would be this shape (fact, one sentence) **(judgement)**. |
| -- | Hard sell: "Great experience. Must do. You have to try it." LR63 (description); "run, don't walk" LR75 | | 2 | 3-8 | Avoid: pushy lines lose viewers [F3]; mocked (LR74, LR75). |

No corpus line mentions a venue deal or discount on camera. A deal line is **(judgement)**: one factual sentence with
what you get, plus the disclosure above when the creator benefits.

## Fit summary for Loca

| Fits (use first) | Fits with care | Does not fit |
|---|---|---|
| H1 stated test, H2 deadpan intent, O1 plain order, D1 point the viewer, B1 first-bite frame with a neutral tail, V1 question + one word, P1 price as fact, P2 value against the format, C1 worth a visit | H3 "have you been" (one creator), H5 price first, R1/R2 room adjective, V2-V5 prefilled opinions, S1 sip descriptors (ad-lib), O2 with a real fact | greetings, series counts, scores, personas and catchphrases, hype superlatives, "hidden gem", staff or crowd claims not witnessed, "I paid like everyone" with a deal, hard-sell CTAs |

Why: the fitting patterns are true for any visit (they frame an action or ask a question), land in 6-12 words, and
need no performance skill. The others need knowledge the script cannot have, a persona, or a claim the deal makes
unsafe.
