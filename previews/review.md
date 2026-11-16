# Step preview review

Catalog: 304 steps. Status: {"approved": 252, "reused": 52}.

Visitor-access constraint: Visitor-accessible camera viewpoint only: place the camera in an ordinary customer area. Never place the camera behind a staff counter or till, inside a working kitchen, at a staff-only prep bench, or in another restricted area. Show staff activity from the customer side or through a public viewing window. Do not assume special access. Adapt any conflicting shot direction to a visitor-side view, using a served item or customer-facing hand-off if the work is not visible from a public area. Close and top-down framing must remain physically possible without crossing the customer boundary.
Hand-count constraint: At most two visible hands total in the entire image, counted across all people, including partial and background hands. Zero or one hand is fine. Keep hands anatomically plausible and attached to their owners. No extra, duplicated or detached hands. Frame all other hands out of the composition.
Makeup style constraint: When makeup or cosmetic application is shown, draw it more schematically: simple face contours, minimal eye, lip and brow marks, flat accent areas for cosmetics, and a recognizable brush or applicator. Keep the application action clear at thumbnail size. Avoid realistic skin texture, individual lashes, detailed eyes and glossy beauty-ad shading. Do not reduce the subject to generic geometric symbols.
Earlier approval statuses predate this rule. See viewpoint-audit.md for flagged viewpoints; export validation does not certify visitor access.

PNG masters follow the phase 02 brief. Matching .jpg exports preserve imageURL filenames without changing the catalog.
Existing images are upscaled from 720 x 1280; generated originals are preserved at the source paths recorded in manifest.json.
Export normalization uses Lanczos resizing and a centered fit to 9:16; scene generation uses the built-in image tool.

Reuse audit: 276 unique illustrations for 304 steps; 28 additional steps share a canonical image. 24 original project illustrations serve 38 steps.
reuse-map.json records canonical resources. shared_catalog.json applies those imageURL aliases for integration; the research catalog and all compatibility step filenames remain available.

## Images requiring replacement

- `salon-transformation_work`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.
- `salon-quick-tour_details`: approved. Strip checked: single-view detail replaces collage, room and tools readable at thumbnail size, no text.
- `cafe-first-visit_pour`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.
- `restaurant-date-night_room`: approved. Whole script strip visually inspected: subject and starting framing readable at 72 px, coherent palette, no baked text.
- `restaurant-date-night_outro`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.
- `restaurant-chef-pick_hands`: approved. Whole script strip inspected: subject and starting framing legible at thumbnail size, coherent palette, no text or depicted filming device.
- `restaurant-chef-pick_cook`: approved. Whole script strip inspected: subject and starting framing legible at thumbnail size, coherent palette, no text or depicted filming device.
- `restaurant-chef-pick_plate`: approved. Whole script strip inspected: subject and starting framing legible at thumbnail size, coherent palette, no text or depicted filming device.
- `restaurant-chef-pick_outro`: approved. Whole script strip inspected: subject and starting framing legible at thumbnail size, coherent palette, no text or depicted filming device.
- `bar-night-out_pour`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.
- `bar-night-out_cheers`: approved. Whole script strip visually reviewed: coherent palette, readable shot subject at 72 px and no baked text.
- `bar-tasting_flight`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.
- `bar-tasting_favorite`: approved. Whole script strip visually reviewed: coherent palette, readable shot subject at 72 px and no baked text.
- `bar-tasting_outro`: approved. Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.

## Reused illustrations

- `bakery-fresh-batch_shelf` -> `bakery-fresh-batch_shelf`: Original project image fits the step subject and starting view; reuse preferred.
- `bakery-fresh-batch_break` -> `bakery-fresh-batch_break`: Original project image fits the step subject and starting view; reuse preferred.
- `bakery-morning-shift_dough` -> `bakery-ask-the-baker_hands`: Top-down close view of dough being worked at the bench.
- `bakery-morning-shift_first` -> `bakery-fresh-batch_outro`: High medium selfie holding a pastry and bakery bag.
- `bakery-sell-out_break` -> `bakery-fresh-batch_break`: Pastry torn toward the lens; eye-level close view.
- `bakery-sell-out_verdict` -> `bakery-fresh-batch_outro`: High medium selfie with the purchased pastry and venue behind.
- `bakery-box_case` -> `bakery-fresh-batch_shelf`: Bakery display case at shelf height; medium view.
- `bakery-ask-the-baker_answer` -> `bakery-fresh-batch_pick`: Customer POV following tongs toward the chosen pastry.
- `bakery-ask-the-baker_inside` -> `bakery-fresh-batch_break`: Pastry torn toward the lens; eye-level close view.
- `bakery-ask-the-baker_verdict` -> `bakery-fresh-batch_outro`: High medium selfie with the purchased pastry and venue behind.
- `salon-transformation_reveal` -> `salon-transformation_reveal`: Original project image fits the step subject and starting view; reuse preferred.
- `salon-meet-stylist_book` -> `salon-transformation_book`: High medium view of the salon booking desk and service list.
- `cafe-first-visit_counter` -> `cafe-first-visit_counter`: Original project image fits the step subject and starting view; reuse preferred.
- `cafe-first-visit_outro` -> `cafe-first-visit_outro`: Original project image fits the step subject and starting view; reuse preferred.
- `cafe-work-spot_room` -> `cafe-morning-ritual_light`: Eye-level wide cafe interior showing seating and tables.
- `cafe-work-spot_desk` -> `cafe-morning-ritual_corner`: Customer POV medium view of laptop and coffee at a cafe table.
- `bar-night-out_hook` -> `bar-happy-hour_hook`: Eye-level medium bar selfie with a cocktail.
- `bar-happy-hour_room` -> `bar-night-out_crowd`: Eye-level wide view of a busy bar interior.
- `bar-happy-hour_verdict` -> `bar-night-out_outro`: Eye-level medium front-camera bar recommendation with a drink.
- `quick-late-night_griddle` -> `quick-the-build_grill`: High close view of burger patties cooking on the griddle.
- `quick-the-build_inside` -> `quick-order-rate_inside`: High close view of a cheeseburger cross-section.
- `food-review-drink_pour` -> `cafe-first-visit_pour`: Top-down close view of latte milk pouring into the cup.
- `food-review-drink_order` -> `cafe-first-visit_counter`: Medium view from the customer side of the coffee counter.
- `food-review-drink_sip` -> `cafe-first-visit_taste`: Eye-level medium front-camera first sip at a cafe.
- `food-review-drink_verdict` -> `cafe-first-visit_outro`: Eye-level medium cafe selfie with cup in frame.
- `food-review-sweet_case` -> `bakery-fresh-batch_shelf`: Bakery pastry display; medium view before choosing a sweet item.
- `food-review-handheld_verdict` -> `quick-order-rate_hook`: Eye-level medium burger-counter selfie holding the burger.
- `pro-what-it-costs_quote` -> `pro-before-after_quote`: Eye-level medium view of the phone repair professional explaining a quote.
- `shop-try-on_sign` -> `shop-find-of-the-day_shopfront`: Low medium view of a clothing shop sign and entrance.
- `shop-tour_find` -> `shop-find-of-the-day_tag`: High detail view of a terracotta jacket and its blank price tag.
- `fit-coach-move_copy` -> `fit-first-class_reps`: Low wide view of one creator performing a kettlebell squat.
- `fit-coach-move_verdict` -> `fit-first-class_after`: High medium post-workout selfie in the same gym setting.
- `fit-coach-move_class` -> `fit-first-class_book`: Eye-level medium view of a class schedule highlighting the kettlebell row.

Superseded exports and metadata are preserved under reuse-audit/superseded/.

## Generated images redone after review

- `bakery-ask-the-baker_ask`: Rejected: camera was on the baker side, looking at the customer; the baker must face the lens. Current status: approved.
- `salon-fade_reveal`: Rejected: long-haired woman in reveal instead of the male client with short fade. Current status: approved.
- `salon-nail-set_turns`: Rejected: visible phone in shot; preview must show only the filmed hand and nail work. Current status: approved.
- `salon-brows_before`: Rejected: face rendered more fully than the shared schematic style; brow preview needs minimal eye and brow marks. Current status: approved.
- `salon-brows_reveal`: Rejected: blank face and covering palm hide the brows and lashes that this step must show. Current status: approved.
- `salon-brows_book`: Rejected: booking sheet shows haircuts rather than the brow and lash service. Current status: approved.
- `cafe-first-visit_pour`: Rejected: phone and filming hands dominate the shot instead of a close top-down view of the latte pour. Current status: approved.
- `restaurant-date-night_outro`: Rejected: creator holds a visible phone in what must be the front-camera closing shot. Current status: approved.
- `restaurant-chef-pick_bite`: Rejected: tasting shot switches to scallops instead of the salmon in the preparation and plate shots. Current status: approved.
- `restaurant-weekend-brunch_spread`: Rejected: visible phone and photographer in frame; the close top-down starting plate must fill the image. Current status: approved.
- `restaurant-room-tour_seat`: Rejected: third-person view of creator using a phone instead of the high-angle view of the table. Current status: approved.
- `restaurant-lunch-deal_plate`: Rejected: plate switches to salmon while the rest of this lunch script shows grilled chicken. Current status: approved.
- `bar-night-out_pour`: Rejected: view too wide and includes a phone; glass and pouring action must fill the close frame. Current status: approved.
- `bar-tasting_flight`: Rejected: a photographer and phone dominate instead of a close view of the tasting glasses. Current status: approved.
- `bar-tasting_outro`: Rejected: whole flight and bar already visible; starting detail framing requires one glass filling the view. Current status: approved.
- `bar-happy-hour_pour`: Rejected: A filming phone is visible in the pour close-up. Current status: approved.
- `fun-first-try_verdict`: Rejected: Venue drift: closing selfie is outside a cafe instead of the amusement park. Current status: approved.
- `fun-group-challenge_hook`: Rejected: Venue drift: go-kart start line instead of the bowling game selected for the action shot. Current status: approved.
- `fun-group-challenge_reaction`: Rejected: Venue drift: bakery staff and pastries instead of friends reacting at the bowling lane. Current status: approved.
- `fun-group-challenge_score`: Rejected: Scoreboard has baked-in numerals; keep scoreboard schematic without text. Current status: approved.
- `fun-group-challenge_verdict`: Rejected: Venue drift: escape-room lobby instead of the same bowling venue. Current status: approved.
- `quick-order-rate_hold`: Rejected: Venue and item drift: use one cheeseburger at a burger counter throughout the script, not bakery pastries. Current status: approved.
- `quick-order-rate_hook`: Rejected: Venue and item drift: use one cheeseburger at a burger counter throughout the script, not bakery pastries. Current status: approved.
- `quick-order-rate_inside`: Rejected: Venue and item drift: use one cheeseburger at a burger counter throughout the script, not bakery pastries. Current status: approved.
- `quick-order-rate_menu`: Rejected: Venue and item drift: use one cheeseburger at a burger counter throughout the script, not bakery pastries. Current status: approved.
- `quick-order-rate_score`: Rejected: Venue and item drift: use one cheeseburger at a burger counter throughout the script, not bakery pastries. Current status: approved.
- `quick-budget-run_receipt`: Food continuity or framing mismatch: bakery pastry/filming device appeared instead of the ordered burger or receipt. Current status: approved.
- `quick-budget-run_best`: Food continuity or framing mismatch: bakery pastry/filming device appeared instead of the ordered burger or receipt. Current status: approved.
- `quick-late-night_bite`: Food continuity or framing mismatch: bakery pastry/filming device appeared instead of the ordered burger or receipt. Current status: approved.
- `quick-the-build_inside`: Food continuity or framing mismatch: bakery pastry/filming device appeared instead of the ordered burger or receipt. Current status: reused.
- `quick-the-build_bite`: Food continuity or framing mismatch: bakery pastry/filming device appeared instead of the ordered burger or receipt. Current status: approved.
- `food-review-handheld_bite`: Strip review: framing too wide, stray filming device, or extra selfie arm. Recompose with a direct, tighter subject view. Current status: approved.
- `food-review-table_action`: Strip review: framing too wide, stray filming device, or extra selfie arm. Recompose with a direct, tighter subject view. Current status: approved.
- `pro-meet-the-owner_hands`: Strip review: framing too wide, stray filming device, or extra selfie arm. Recompose with a direct, tighter subject view. Current status: approved.
- `pro-meet-the-owner_bench`: Strip review: framing too wide, stray filming device, or extra selfie arm. Recompose with a direct, tighter subject view. Current status: approved.
- `pro-meet-the-owner_prices`: Strip review: framing too wide, stray filming device, or extra selfie arm. Recompose with a direct, tighter subject view. Current status: approved.
- `pro-first-lesson_hands`: Framing too wide for planned close shot; recompose around hands and keyboard. Current status: approved.
- `pro-first-lesson_correction`: Framing too wide for planned close shot; recompose around hands and keyboard. Current status: approved.
- `pro-first-lesson_win`: Framing too wide for planned close shot; recompose around hands and keyboard. Current status: approved.
- `shop-try-on_reveal`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-try-on_second`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-music-demo_chord`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-music-demo_player`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-music-demo_try`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-music-demo_tip`: Planned detail/close framing or try-on action not shown clearly. Regenerate a tight subject view or the outfit being worn. Current status: approved.
- `shop-tour_inside`: Framing too wide for a detail/close view, or the wrong person faces the lens. Recompose around the planned subject. Current status: approved.
- `shop-tour_find`: Framing too wide for a detail/close view, or the wrong person faces the lens. Recompose around the planned subject. Current status: reused.
- `fit-first-class_book`: Framing too wide for a detail/close view, or the wrong person faces the lens. Recompose around the planned subject. Current status: approved.
- `fit-gym-tour_owner`: Framing too wide for a detail/close view, or the wrong person faces the lens. Recompose around the planned subject. Current status: approved.
- `fit-sauna-session_price`: The people dominate the price-list shot. Make the session price list the main medium-frame subject. Current status: approved.
- `fit-coach-move_coach`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-coach-move_stance`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-coach-move_copy`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: reused.
- `fit-coach-move_class`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: reused.
- `fit-treatment_room`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-treatment_menu`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-treatment_walkthrough`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-treatment_during`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.
- `fit-first-appointment_price`: Final strip review: close framing, camera-facing subject or solo/empty-room requirement missed. Regenerate with exact starting composition. Current status: approved.

## Steps without a reviewed image

None.

## Script strip review

Open index.html. Each row also has a saved contact strip under review-strips/.

- `bakery-fresh-batch`: 5/5 approved or retained.
- `bakery-morning-shift`: 5/5 approved or retained.
- `bakery-sell-out`: 5/5 approved or retained.
- `bakery-box`: 5/5 approved or retained.
- `bakery-ask-the-baker`: 5/5 approved or retained.
- `salon-transformation`: 5/5 approved or retained.
- `salon-quick-tour`: 5/5 approved or retained.
- `salon-fade`: 5/5 approved or retained.
- `salon-nail-set`: 5/5 approved or retained.
- `salon-brows`: 5/5 approved or retained.
- `salon-meet-stylist`: 5/5 approved or retained.
- `cafe-first-visit`: 5/5 approved or retained.
- `cafe-morning-ritual`: 4/4 approved or retained.
- `cafe-before-opening`: 5/5 approved or retained.
- `cafe-seasonal-drink`: 5/5 approved or retained.
- `cafe-work-spot`: 5/5 approved or retained.
- `restaurant-date-night`: 5/5 approved or retained.
- `restaurant-chef-pick`: 5/5 approved or retained.
- `restaurant-family-table`: 5/5 approved or retained.
- `restaurant-weekend-brunch`: 6/6 approved or retained.
- `restaurant-room-tour`: 6/6 approved or retained.
- `restaurant-lunch-deal`: 6/6 approved or retained.
- `bar-night-out`: 5/5 approved or retained.
- `bar-tasting`: 5/5 approved or retained.
- `night-live-music`: 6/6 approved or retained.
- `bar-happy-hour`: 6/6 approved or retained.
- `fun-first-try`: 5/5 approved or retained.
- `fun-group-challenge`: 5/5 approved or retained.
- `quick-order-rate`: 5/5 approved or retained.
- `quick-truck-find`: 6/6 approved or retained.
- `quick-budget-run`: 6/6 approved or retained.
- `quick-late-night`: 6/6 approved or retained.
- `quick-the-build`: 6/6 approved or retained.
- `food-review`: 5/5 approved or retained.
- `food-review-drink`: 5/5 approved or retained.
- `food-review-pour`: 4/4 approved or retained.
- `food-review-sweet`: 4/4 approved or retained.
- `food-review-handheld`: 4/4 approved or retained.
- `food-review-table`: 5/5 approved or retained.
- `pro-before-after`: 6/6 approved or retained.
- `pro-meet-the-owner`: 6/6 approved or retained.
- `pro-first-lesson`: 6/6 approved or retained.
- `pro-quick-tip`: 5/5 approved or retained.
- `pro-what-it-costs`: 6/6 approved or retained.
- `shop-find-of-the-day`: 6/6 approved or retained.
- `shop-try-on`: 7/7 approved or retained.
- `shop-budget-challenge`: 7/7 approved or retained.
- `shop-owner-pick`: 6/6 approved or retained.
- `shop-music-demo`: 6/6 approved or retained.
- `shop-tour`: 6/6 approved or retained.
- `fit-first-class`: 7/7 approved or retained.
- `fit-gym-tour`: 6/6 approved or retained.
- `fit-sauna-session`: 6/6 approved or retained.
- `fit-coach-move`: 6/6 approved or retained.
- `fit-treatment`: 6/6 approved or retained.
- `fit-first-appointment`: 6/6 approved or retained.
