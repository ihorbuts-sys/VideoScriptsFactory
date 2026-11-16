# Venue kinds: production categories mapped to script kinds

Source: `categories_creator.graphql.loca.us.json` (the 20 creator-facing slugs). Venue counts are from
`businessCollection` on production, fetched 2026-10-24 (648 venues; one venue carries several slugs, so counts
overlap). Venues also carry slugs outside the creator list (`craft-beer`, `beauty-barbershop`, `beauty-nails`,
`events-*`, `shopping-pet-store` and more, 36 in all); the mapping below names the ones that matter as aliases.

A kind groups categories whose video would be filmed the same way: same first shot, same hero subject, same
reason a first-time visitor comes. Nine kinds; the kind id is the production slug of its main category, so the
app can match on slugs without a translation table (the existing `craft-beer` id is replaced, see below).

| Kind id | Title in the app | SF Symbol | Production slugs covered | Venue aliases (non-creator slugs) | Venues |
|---|---|---|---|---|---|
| `coffee` | Cafe | `cup.and.saucer.fill` | coffee | | 21 |
| `bakery` | Bakery | `birthday.cake.fill` | bakery | | 21 |
| `dining` | Restaurant | `fork.knife` | dining, food-and-drinks, food-and-drinks-family | | 304 / 97 / 5 |
| `fast-food` | Quick bites | `takeoutbag.and.cup.and.straw.fill` | fast-food, food-truck | | 19 / 23 |
| `entertainment` | Going out | `music.note.house.fill` | entertainment | craft-beer, events-music-n-film, events-social | 20 (+7 craft-beer) |
| `beauty-salon` | Salon | `comb.fill` | beauty-salon, beauty | beauty-barbershop, beauty-nails, beauty-products | 46 / 63 |
| `sport_health` | Fitness and wellness | `figure.yoga` | sport_health, services-health | | 35 / 24 |
| `shopping` | Shop | `bag.fill` | shopping, clothing-shops, shopping-music | thrift-shops, vintage-shop, book-stores, shopping-other, knick-knacks | 76 / 12 / 12 |
| `services` | Local pro | `wrench.and.screwdriver.fill` | services, services-education, business-services | services-cleaning, services-photography, services-pet | 33 / 12 / 13 |

## Slugs with no scripts

| Slug | Title | Why |
|---|---|---|
| `services-other` | Other | The 12 venues share nothing a script could plan for (a consultancy, a bus terminal, movers, a tattoo studio, a spell caster). The creator gets a custom script, which is what the app already does when no kind matches. |
| `recreational-other` | Other | 8 venues: a parcel locker, a drag strip, a beverage distributor, an advertising affiliate. No common shot; same fallback. A venue here that also carries `entertainment` gets the Going out scripts. |

## Decisions and reasons

- **`craft-beer` (Bar) is not a creator category.** 7 venues carry it as a secondary slug (Blue Owl Brewing,
  On Rotation Brewery, Clive Bar, Placeholders Tiki Bar); bars and lounges otherwise sit under `entertainment`
  (PM Lounge, BitBar, Nico's Bar and Grill, Empire State Jazz Cafe, Green Light Social) or under `dining`
  (Kelly's Irish Pub). The two bar scripts move to `entertainment` (and stay available to `dining`), and
  `craft-beer` becomes an alias of `entertainment`. The kind is titled "Going out" because the same slug holds
  activity venues (a waterpark, laser tag, an adventure park, a casino); its scripts cover both a night at a bar
  and an activity.
- **Dining, food-and-drinks and food-and-drinks-family are one kind.** The video is the same: room, dish, bite,
  verdict. Family venues get a family-table script inside `dining` rather than their own kind (5 venues).
- **Fast-food and food-truck get their own kind, apart from dining.** A counter or a truck window, a handheld
  item, eating standing or in the car, speed and price: the shot order and the hook differ from a sit-down
  restaurant (judgement, backed by the best-practice notes in `best_practices/fast-food.md`).
- **Beauty and beauty-salon are one kind.** Both are hair, nails, brows, skin and barbers: the before/after
  reveal drives the video. Spas and massage studios listed under `beauty` also fit the wellness scripts; the
  app takes the first match, so they get Salon scripts, which still work (judgement).
- **Sport_health and services-health are one kind.** The production venues are gyms, yoga and sauna studios,
  massage, IV bars, skin clinics, a dental clinic and an emergency centre. Studios and treatments share the
  "try a class / try a session" shape. Clinics fit the "meet the team" script; scripts avoid medical claims.
- **Services, services-education and business-services are one kind.** Phone repair, tutoring, piano schools,
  security firms, salon software: the common video is a person and their work: meet the owner, watch the work,
  see the result, how to book. Business-services is the weakest fit (several B2B venues have nothing to film);
  kept because the owner-and-work script still applies (judgement).
- **Shopping, clothing-shops and shopping-music are one kind.** A rail, a shelf, a find, a try-on or a
  demo, the price. A music shop demo and a try-on are both "the product in use".

## Priority when a venue has several slugs

The app picks one kind per venue (`VideoStudio.venueKind(for:)` in Loca, today: coffee, bakery, beauty-salon,
dining). The specific kind wins over the general one. Proposed order, first match wins:

1. `coffee` (coffee)
2. `bakery` (bakery)
3. `entertainment` (entertainment, craft-beer, events-music-n-film, events-social)
4. `fast-food` (fast-food, food-truck)
5. `dining` (dining, food-and-drinks, food-and-drinks-family)
6. `beauty-salon` (beauty-salon, beauty, beauty-barbershop, beauty-nails, beauty-products)
7. `sport_health` (sport_health, services-health)
8. `shopping` (shopping, clothing-shops, shopping-music, thrift-shops, vintage-shop, book-stores, shopping-other, knick-knacks)
9. `services` (services, services-education, business-services, services-cleaning, services-photography, services-pet)

Why this order: a cafe that also lists `dining` is filmed as a cafe; a brewery that lists `dining` is filmed as
a night out; a pizza place listed as both `services` and `fast-food` (Uzy's NY Pizza, Pizza PieRos) is filmed as
food, so every food kind comes before the non-food kinds. Food-and-drinks venues listed under `shopping`
(Los 3 Regios Mexican Restaurant, Donut Taco Palace) also land on a food kind first.

This changes Loca code (`VideoStudio.venueKind(for:)`), which is outside this research; see `HANDOFF.md`.
