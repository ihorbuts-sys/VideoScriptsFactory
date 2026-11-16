# v3 guide queue (2026-11-16)

Render order: independent guides first, the truck guides together once `model_refferences/objects/food_truck/lineart/`
exists (the approvals agent builds it), blocked ones last; the four result guides wait for the mirror line-art approval.
Run each with the guide-animator agent: give it the request path.

| # | Request | Status |
|---|---|---|
| 1 | `guides/revisions/2026-11-16-v3/verdict/verdict_plate_after_push/request.md` | now |
| 2 | `guides/revisions/2026-11-16-v3/counter/counter_display_truck/request.md` | now |
| 3 | `guides/revisions/2026-11-16-v3/bowl/bowl_steam_overhead/request.md` | now |
| 4 | `guides/revisions/2026-11-16-v3/bowl/spoon_lift_toward_lens/request.md` | now |
| 5 | `guides/revisions/2026-11-16-v3/handheld/handheld_hold_turn/request.md` | now |
| 6 | `guides/revisions/2026-11-16-v3/handheld/handheld_paper_open/request.md` | now |
| 7 | `guides/revisions/2026-11-16-v3/handheld/hand_bite_handheld/request.md` | now |
| 8 | `guides/revisions/2026-11-16-v3/drink/glass_sip_lift/request.md` | now |
| 9 | `guides/revisions/2026-11-16-v3/amenity/amenity_point_hold/request.md` | now |
| 10 | `guides/revisions/2026-11-16-v3/venue/venue_order_placed/request.md` | now |
| 11 | `guides/revisions/2026-11-16-v3/venue/venue_order_arrives/request.md` | now |
| 12 | `guides/revisions/2026-11-16-v3/venue/venue_settle_in/request.md` | now |
| 13 | `guides/revisions/2026-11-16-v3/experience/experience_floor_pan/request.md` | now |
| 14 | `guides/revisions/2026-11-16-v3/experience/experience_gear_up/request.md` | now |
| 15 | `guides/revisions/2026-11-16-v3/experience/experience_in_action/request.md` | now |
| 16 | `guides/revisions/2026-11-16-v3/experience/experience_selfie_after/request.md` | now |
| 17 | `guides/revisions/2026-11-16-v3/visit/visit_reception_pan/request.md` | now |
| 18 | `guides/revisions/2026-11-16-v3/visit/visit_front_desk_hello/request.md` | now |
| 19 | `guides/revisions/2026-11-16-v3/visit/visit_tools_no_clients/request.md` | now |
| 20 | `guides/revisions/2026-11-16-v3/visit/visit_selfie_takeaway/request.md` | now |
| 21 | `guides/revisions/2026-11-16-v3/shopping/shop_shelf_pan/request.md` | blocked: generic product box (object request; animator check 2026-11-16: empty shelves do not read) |
| 22 | `guides/revisions/2026-11-16-v3/truck/truck_across_street/request.md` | after truck cache |
| 23 | `guides/revisions/2026-11-16-v3/truck/truck_window_line/request.md` | after truck cache |
| 24 | `guides/revisions/2026-11-16-v3/truck/truck_order_window/request.md` | after truck cache |
| 25 | `guides/revisions/2026-11-16-v3/truck/truck_window_handoff/request.md` | after truck cache |
| 26 | `guides/revisions/2026-11-16-v3/shopping/shop_shelf_walk/request.md` | blocked: generic product box (object request) |
| 27 | `guides/revisions/2026-11-16-v3/shopping/shop_hold_the_find/request.md` | blocked: generic product box (object request) |
| 28 | `guides/revisions/2026-11-16-v3/shopping/shop_checkout_bag/request.md` | blocked: paper shopping bag (object request) |
| 29 | `guides/revisions/2026-11-16-v3/result/result_salon_pan/request.md` | blocked: mirror line-art approval |
| 30 | `guides/revisions/2026-11-16-v3/result/result_before_chair/request.md` | blocked: mirror line-art approval |
| 31 | `guides/revisions/2026-11-16-v3/result/result_hands_at_work/request.md` | blocked: mirror line-art approval |
| 32 | `guides/revisions/2026-11-16-v3/result/result_after_mirror/request.md` | blocked: mirror line-art approval |

Object requests to write before the blocked shopping guides: generic product box, paper shopping bag.
