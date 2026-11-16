# Catalog v3 guide work list (2026-11-16)

Steps in `scripts/_parts/v3` that have no guide yet. The step still works: every v3 step allows "No guide"
(the carousel always starts with "No guide"), so the app shows the step with no overlay until the guide is rendered. Objects go through
`OBJECTS.md` requests and the owner's line-art approval first (guide-objects skill); nothing here is rendered.

| Gap | Guide needed | Objects | Used by | Status |
|---|---|---|---|---|
| amenity-detail | point at the amenity and hold | none | dish-review/amenities; drink-review/amenities; venue-review/amenities | filled 2026-11-16: `amenity_point_hold` (owner approved) |
| bowl-main | hero shot over a bowl (steam, overhead) | bowl (Tripo serving_bowl, line art unapproved) | dish-review/main | filled 2026-11-16: `bowl_steam_overhead` (owner approved) |
| counter-display | the counter display, slow lateral move | display case | dish-review/place; drink-review/place; venue-review/place | filled 2026-11-16: `counter_display_truck` (owner approved) |
| experience-after | selfie right after | none | venue-review/after | filled 2026-11-16: `experience_selfie_after` (owner approved) |
| experience-before | gear or briefing | generic gear | venue-review/before | open |
| experience-main | action wide then POV | stand-in person in motion | venue-review/main | open |
| experience-place | the space wide | open floor | venue-review/place | open |
| glass-sip | sip from a glass (with straw for iced, juices) | straw (optional) | drink-review/after | filled 2026-11-16: `glass_sip_lift` (owner approved) |
| hand-after | bite by hand: handheld, pastry, pizza slice | none beyond the dishes; CC0 hand grips | dish-review/after | open |
| handheld-main | hold up and turn, paper open | paper wrap and tray (requested), burger line art approval | dish-review/main | open |
| result-after | the result at the mirror | mirror | venue-review/after | open |
| result-before | before, in the chair | salon chair and mirror | venue-review/before | open |
| result-main | hands at work, side view | salon chair, stand-in client | venue-review/main | open |
| result-place | salon interior pan | salon chair and mirror | venue-review/place | open |
| shopping-after | bag or receipt at checkout | checkout counter, bag | venue-review/after | open |
| shopping-before | walk along a shelf | shelves | venue-review/before | open |
| shopping-main | hold up the find | generic product box | venue-review/main | open |
| shopping-place | shop interior pan | shelves | venue-review/place | open |
| spoon-after | spoonful lifted toward the lens | spoon (teaspoon/dessert spoon request open), bowl | dish-review/after | filled 2026-11-16: `spoon_lift_toward_lens` (owner approved) |
| truck-arrive | truck exterior from across the street | food truck with a service window | dish-review/arrive; drink-review/arrive; venue-review/arrive | filled 2026-11-16: `truck_across_street` (owner approved) |
| truck-handoff | hand-off through the window | food truck, paper wrap and tray | venue-review/main | open |
| truck-order | ordering at the truck window | food truck | dish-review/order; drink-review/order; venue-review/before | open |
| truck-place | the truck, its window and the line | food truck | dish-review/place; drink-review/place; venue-review/place | open |
| venue-after | generic fallback: settling in | none | venue-review/after | filled 2026-11-16: `venue_settle_in` (owner approved) |
| venue-before | generic fallback: order being placed | none | venue-review/before | filled 2026-11-16: `venue_order_placed` (owner approved) |
| venue-main | generic fallback: getting the order | none | venue-review/main | open |
| visit-after | selfie takeaway | none | venue-review/after | filled 2026-11-16: `visit_selfie_takeaway` (owner approved) |
| visit-before | front desk, staff hello | reception desk | venue-review/before | filled 2026-11-16: `visit_front_desk_hello` (owner approved) |
| visit-main | the space and tools, no clients | generic desk and tools | venue-review/main | filled 2026-11-16: `visit_tools_no_clients` (owner approved) |
| visit-place | reception or room | reception desk | venue-review/place | open |

30 gaps: 12 filled by owner-approved guides on 2026-11-16, 18 open.

`gap` is authoring information only: the client catalog build (`check_scripts.py --v3 --merge`) strips it; a step with no guide ships an empty `guides` list (the carousel then shows only "No guide", which is always its first item). The verdict also gained the face-free `verdict_plate_after_push` (dish-review). `abstract_food_morph` is the generic dish version of the plate guides (guide format 3.0b), not a step guide. Face-free verdict guide: still pending (L13 warning on every verdict; `verdict_plate_after_push` briefed 2026-11-13).
