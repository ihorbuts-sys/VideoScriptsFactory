# Objects

The 3D objects guides may use, their status in the line-art style, and what is missing. Rules: `STYLE.md` "Objects".
Owner ruling 2026-11-10: the code-built P0 set and the outside pieces in active guides are the standard; any new
object, or a model new to line art, needs the owner's approval of a line-art render before a guide uses it. Agents
never generate, buy or reconstruct a model on their own; they add a request below and stop.

## Requests (open; the owner decides each)

| Request | For | Requested by | Date | Decision |
|---|---|---|---|---|
| Generic product box in P0 line art, as generic as possible (owner): an unlabelled retail carton, no print, logo or text, in two or three sizes (for example about 6 x 4 x 2 in / 15 x 10 x 5 cm, 8 x 5 x 3 in / 20 x 13 x 8 cm, 4 x 4 x 4 in / 10 cm cube), with a slight lid seam or tuck flap so it does not read as a plain block; stood in rows of 4-6 on a shelf and also held in one hand. Why: probe 2026-11-16 (`guides/revisions/2026-11-16-v3/shopping/shop_shelf_pan/scratch/probe1.png`, `probe2.png`): the approved Tripo wall shelf empty, stacked two high at chest height, reads as two small benches or side tables, not a shop; the approved display case carries its own pastries and reads as a bakery; no approved small object belongs on a shop shelf (takeaway cup, cake slice, burger, dumbbell, hair clipper, laptop all name another venue kind; the t-shirt v2 is not approved). Nearest existing: `p0_scenes.plain_card` (flat card), the procedural box-built counter and espresso block in `p0_scenes.counter`; the rejected legacy `pastry_box` / "Open food box with pastries" (a food box, wrong for a shop). Suggestion: a code-built `assets.product_box(w, d, h, flap=True)` (bevelled box plus a lid seam line), rendered once in line art as a row of mixed sizes on the approved wall shelf at chest height and one held box, for approval; no Tripo credits needed | shop_shelf_pan, shop_shelf_walk, shop_hold_the_find (v3 shopping) | guide-animator (shop_shelf_pan) | 2026-11-16 | code-built candidate rendered 2026-11-16, awaiting owner approval: `assets.product_box(w, d, h, flap=True)` (6x4x2, 8x5x3, 4x4x4 in; telescoping lid 2 mm proud draws the seam); renders `guides/review/objects_renders/product_boxes.png`, `_top.png`, `_side.png` |
| Paper shopping bag in P0 line art, generic, no print or logo: about 10 x 6 x 13 in (25 x 15 x 33 cm), gusseted sides folded in, folded top cuff, two twisted-rope handles. Nearest existing: none (paper_wrap and paper_tray are food packaging). Suggestion: code-built. | shop_checkout_bag (venue-review shopping, after) | v3 guide queue 2026-11-16 | 2026-11-16 | code-built candidate rendered 2026-11-16, awaiting owner approval: `assets.shopping_bag()`; renders `guides/review/objects_renders/shopping_bag.png`, `_top.png`, `_side.png` |
| Abstract generic food in yellow lines (owner request 2026-11-17, `guides/revisions/2026-11-16-v3/plate/abstract_food_morph/request.md`): code-built `drafts/abstract_food_morph.py` `food_mesh`, five rounded base-flattened pieces in one mesh, three forms as shape keys (heap: dollop mound with a second mound behind and three small pieces; stack: three discs with two small pieces; two pieces), drawn in the P0 light-edge yellow through the new per-object `p0_line_color` option in `render_p0.py` (default off). Stills for approval: `guides/revisions/2026-11-16-v3/plate/abstract_food_morph/stills.png`. Nearest existing: `assets.pasta`, the approved Tripo salad. Used only by the abstract_food_morph draft until approved | abstract_food_morph (pilot); later bowl_steam_overhead, spoon_lift_toward_lens | guide-animator | 2026-11-16 | superseded 2026-11-17 (owner round 2: the approved dishes cycle in yellow instead; round 1 builder and stills archived under `guides/revisions/2026-11-16-v3/plate/abstract_food_morph/archive/2026-11-16-r1/`) |
| (add one row per missing object; see the audit's list below) | | | | |
| Neutral example dish replacing the pasta (handoff 2026-11-13, section 5: "replace the pasta in dish guides with a neutral plate"): a dish that reads as food at any venue kind without naming one, for example a plated portion with a side and a sauce trace, plus a "finished" state (crumbs, fork across) for the face-free verdict. Nearest existing: `assets.py` `pasta` on `plate` (the current shared example, owner ruling 2026-11-10) and the approved Tripo salad. Suggestion: a procedural dish on the existing `plate`, rendered once in line art for approval; then re-render only the dish guides where the change shows (guide-objects rule 2026-11-11). Changes the 2026-11-10 `exampleDish` ruling: owner decides | plate-reveal and bite guides, verdict_plate_after_push | scripts agent (opinions handoff) | 2026-11-13 | open |
| Folding (bifold) menu: two hinged card panels with unlettered rows, closed cover to open spread; nearest existing: `p0_scenes.plain_card` (single flat A5 card). Suggestion: build it from two `plain_card` panels on a hinge in code and render one line-art still closed, half open and open for approval | menu_card_open (redo of menu_card_push; research menu-card variant 2, RA4/RA8/RA21) | menu guide agent | 2026-11-10 | open |
| One hand opening a menu cover from overhead (fingertips pinch the cover's free edge, wrist enters from the bottom edge, forearm fades); nearest existing: the CC0 `real_hands.py` pinch pose, approved only in its three owner-requested grips. Suggestion: refit the pinch pose to the cover edge and render the contact at closed, 45 deg and flat for approval | menu_card_open | menu guide agent | 2026-11-10 | open |
| Napkin in P0 line art: a folded cloth or paper napkin standing as a near blocker (about 0.20 x 0.20 m unfolded, folded to about 0.20 x 0.10 m, standing or draped 5-15 cm in front of the lens), plus the hand that pulls it sideways out of frame (pinch on the napkin's free corner, wrist entering from the side, forearm fades). Nearest existing: none for the napkin (audit row 19: "Missing"; plate_tissue_slide never built one); `p0_scenes.plain_card` is the nearest flat blocker but looks different; for the hand, the CC0 pinch pose in its approved grips. Suggestion: a procedural folded napkin (two thin bent panels, rounded corners) rendered in line art standing and mid-pull for approval, then the pinch refitted to its corner | plate_napkin_pull (plate-reveal 2, option B: phone still at 45 deg in portrait, a hand pulls the napkin out of frame; orientation fix of plate_tissue_slide; RA 2d, RA17, RA23; draft skipped) | guide-animator, plates family regeneration | 2026-11-10 | open |
| T-shirt, slim v2 (owner regenerated in Tripo, task 2d3fe51d, image_to_model v3.1, 30 API credits, 2026-11-16; prepared copies `model_refferences/objects/tshirt/slim-v2/tshirt-slim.glb` upright (0.50 x 0.65 m, 0.025 m deep, front -Y) and `tshirt-shelf-flat.glb` laid flat). Replaces the v1 candidate that read as a lumpy standing bulk (v1 render archived in `archive/2026-11-16_objects_approval/tshirt_v1_candidate/`). Renders `guides/review/objects_renders/candidate_tshirt_slim.png`, `_front`, `_side` (upright, as hanging) and `candidate_tshirt_flat.png`, `_top` (laid flat). | shopping scripts (try-on, find of the day) | owner | 2026-11-16 | owner-provided candidate, awaiting approval |
| Salon station mirror (owner-provided candidate: generated by the owner in Tripo, task 7388f97b, image_to_model v3.1, 30 API credits, 2026-11-16; prepared copy `model_refferences/objects/salon_mirror/salon-mirror.glb`, 0.6 m wide x 0.938 m tall incl. empty tool shelf, front -Y, origin at the mirror bottom on the wall plane; no reflection, glints in the model). Renders `guides/review/objects_renders/candidate_salon_mirror.png`, `_front`, `_side`. | venue review, Result subject (salon, barber): the place and before/after | owner | 2026-11-16 | owner-provided candidate, awaiting approval |
| Two hands holding a handheld in its opened paper wrap at chest height, back camera (both hands from below/sides, thumbs on the paper sleeve, fingers under the base, wrists entering from the bottom edge, forearms fade at a cuff of at most about 4 in), turning it a quarter turn about its vertical axis; at most two hands in frame. Nearest existing: the CC0 `real_hands.py` cylindrical power grasp (glass_slide_close, pancake_clear_path) and pinch pose, approved only in their three owner-requested grips; the creator rig's hands are approved only in the sip/bite person guides. Suggestion: refit the power grasp to the `assets.paper_wrap(opened=True)` sleeve (radius about 2.4 in) for a left and a right hand, render line-art stills at 0, 45 and 90 deg of the turn with the hand 2x crops and the hand-to-wrap distance check, for approval | handheld_hold_turn (v3, dish-review/main handhelds) | guide-animator | 2026-11-16 | open |
| Handheld with a cut side: the approved opened paper wrap (`assets.paper_wrap(opened=True)`) is a lathe, the same from every side, so a quarter turn shows no change and there is no cut face for the beat "Stop when the cut side faces you"; the approved Tripo `burger` is whole and unwrapped. Nearest existing: `assets.paper_wrap(opened=True)` (sleeve, filling, bun dome). Suggestion: a code-built variant parameter used only by this guide, `paper_wrap(opened=True, cut=True)`: the same sleeve and bun halved by a flat vertical plane, the cut face showing bun, filling and patty layer lines; one line-art render facing the lens and at 90 deg for approval. Alternative without a new object: drop the cut and change the beat to show the side profile (owner decides) | handheld_hold_turn | guide-animator | 2026-11-16 | open |
| One hand picking up the approved Tripo dumbbell (0.32 m / 12.6 in long, `dumbbell/tripo-generated/review/asset.blend`) by its handle, POV from the back camera at chest height looking down about 30 deg: the hand enters from the bottom edge, closes a power grasp around the horizontal handle (fingers under, thumb over, knuckles toward the lens about 30-45 deg off edge-on), lifts it off its rest and holds it up in front of the lens; forearm fades at a cuff of at most about 4 in; one hand in frame. Nearest existing: the CC0 `real_hands.py` `wrap` power grasp (glass_slide_close, pancake_clear_path), approved only in its three owner-requested grips, fitted to an upright glass (finger clamp radius 0.045 m), not a thin horizontal handle that moves with the hand. Suggestion: refit `wrap` to the dumbbell handle for a right hand; render line-art stills at reach, grasp (handle still on its rest) and lifted, with the hand 2x crops and the hand-to-dumbbell and hand-to-rest distance check, for approval | experience_gear_up (v3, venue-review/before, subject experience) | guide-animator | 2026-11-16 | open |
| Dumbbell floor rack in P0 line art: a low rack the approved Tripo dumbbell rests on before the pick-up (about 1.2 m / 4 ft wide, one or two tiers about 1-2 ft high, 2-3 dumbbells in a row, the picked one nearest the lens). Nearest existing: legacy procedural `venue_assets.rack(kind='dumbbell')` (two 2.2 m shelf blocks with the procedural `venue_assets.dumbbell`, which the owner rejected 2026-11-11; the rack frame was never rendered in P0 line art); no approved rack. Suggestion: a code-built builder used only by this guide: the legacy shelf frame cut to one 1.2 m tier with two rails, carrying copies of the approved Tripo dumbbell (default dot cleanup) instead of the rejected procedural one; one line-art still from the guide camera for approval. Alternative without a new object: the dumbbells rest on the floor with a single faint floor edge line (STYLE "no floor unless one edge explains the framing"), and the request text drops "rack" (owner decides) | experience_gear_up | guide-animator | 2026-11-16 | open |
| Creator overhead dumbbell press (person pose plus grip; both objects are approved, the motion is not): the canonical creator standing on an open floor, one hand closed around the approved Tripo dumbbell's handle (four fingers wrapped, thumb closing over the fingers, the dumbbell parented to the hand bone, no hand or forearm vertex inside the dumbbell), one rep from the shoulder rack to full overhead lockout and back over about 4 s, the free arm relaxed at the side; feet planted, no walk. Nearest existing: the creator's cup grip (`p0_people.py` `grip_digits(kind='cup')`, a cylindrical grasp approved only for the sip guides) and the CC0 `real_hands.py` power grasp (approved only in its three owner-requested grips); no creator pose above shoulder height exists. Suggestion: add a `handle` kind to `grip_digits` fitted to the dumbbell handle radius and an overhead arm path on the existing two-bone `ArmPose` solve; render one line-art still each at rack, mid-press and lockout, wide (full body) and waist-up, from a friend's chest-height back camera, for approval | experience_in_action (v3, venue-review/main, subject experience) | guide-animator | 2026-11-16 | open |


## Owner review 2026-11-11 (objects page decisions; no decision = approved, owner rule)

Source: `guides/review/decisions/objects.json`, renders in `guides/review/objects_renders/`. Approved library models
may be used in new guides; the dot cleanup below applies to every library model before use.

Owner follow-up 2026-11-11: shape changes to shared builders apply everywhere (every live guide that uses them is
re-rendered and shown before/after before publishing); croissant_oozing is rejected; the pastry box gets pastries from
existing approved models. Partition planes: the flat room dividers in room guides (depth without walls). Milk stream,
steam strands and light-edge cues are per-guide effects, approved, no standalone render. tshirt: shape decided with the
shopping scripts.

### Rejected (24) - do not use

- schematic mouthless bust
- Procedural burger
- Lettered paper card
- Open food box with pastries
- Held tongs with a hand
- Tool: brush
- Tool: tamper
- Tool: clippers
- Tool: scissors
- Pastry case (2.3 m, no glass)
- Salon chair
- Salon station with mirror
- Salon tools
- Garment on a hanger
- Garment rack
- Bottle shelf
- Bench
- Sauna bench
- Treatment bed
- Shopfront facade
- Food truck front
- Dumbbell
- Tabletop grill block with meat
- Acoustic guitar CC0

### Needs work (29)

| Object | Owner note |
|---|---|
| knife | lets make more natural dinner knife shape |
| water glass | lets show some liquid inside. lets maybe have high rocks-like glass |
| cocktail glass (shell, liquid surface, straw, 2 floating ice cubes) | lets add one ice cube  and position each on the different height in the liquid |
| pizza | lets make it sliced ( 8 chapters + one slice slightly shifted to outside so it become more obvious that its a pizza) |
| counter (+ optional cabinet), espresso machine block, card holder | lets place some glasses and cups to be here constantly on the machine (they are drying there - so upside down) |
| round table | lets draw inner circle so plate looks more natural |
| partition planes | what is it for specifically? |
| Dinner plate (Tripo) | lets cleanup some dots from surface (make surface smoother |
| takeaway_cup | cleanup dots from surface |
| drinking_glass | cleanup dots from surface |
| stemmed_glass | cleanup dots from surface |
| bottle | cleanup dots from surface |
| latte_cup | cleanup dots from surface |
| espresso_machine | cleanup dots from surface |
| coffee_grinder | cleanup dots from surface |
| portafilter | cleanup dots from surface |
| coffee_tamper | cleanup dots from surface |
| knock_box | cleanup dots from surface |
| brunch_toast | lets make egg yolk shape highlighted with yellow strokes |
| croissant_oozing | looks weird - REJECTED by owner follow-up 2026-11-11 |
| serving_bowl | cleanup dots from surface |
| kitchen_tongs | cleanup dots from surface |
| dining_table | cleanup dots from surface |
| dining_chair | cleanup dots from surface |
| bar_counter | cleanup dots from surface |
| bar_stool | cleanup dots from surface |
| pastry_box | no cakes inside. should they be there? |
| treatment_bed | remove the hole  at the last part of the bed. it should have just one for head |
| tshirt | how its supposed to be used? if it should lay on the table - should be mostly slim, if it's handing on the hanger - the same |

### Approved (50)

- cup(): ceramic cup, open handle, coffee surface, foam heart or rosetta
- saucer
- plate ("Plate with formed rim", 0.30 m)
- platter (broad flat plate)
- fork (four tines, 0.19 m)
- pasta (pasta plate with basil leaf)
- pastry (two-half croissant)
- bread loaf
- pancake stack (butter, cream, berry, syrup)
- salad portion
- milk pitcher
- gooseneck kettle
- milk stream, steam strands, light-edge cues (note: I see no preview)
- menu card (unlettered rows)
- menu board, three columns (unlettered bars, lamps)
- two-person dining table with settings
- long tabletop block
- dining chair
- window (frame only)
- glazed door with hinge
- venue sign, hanging bracket, downlight
- A-frame welcome stand, facade ground line
- pendant lamp
- floor plant
- canonical creator (65-bone rig, original hands)
- cropped anatomical hands (pinch, point, relaxed)
- Latte cup (functional, hollow)
- Saucer (TripoSR)
- Croissant approved-v2
- Serving tray
- Cake slice
- burger
- display_case
- pastry_rack
- bakery_oven
- glazed_door
- window
- wall_shelf
- menu_board
- pendant
- beer_tap
- laptop
- acoustic_guitar
- dumbbell
- hair_clipper
- salon_chair
- rack_shelf_tray
- plant (model_built)
- barista (65-bone rig, rest pose)
- friend_locs (65-bone rig, rest pose)

## Owner review 2026-11-16 (objects page candidates)

Owner: "ill regenerate t-shirt, other approved". Approved and moved to inventory 1a (rows marked 2026-11-16): food truck (cache `food_truck/lineart/asset.blend`), burger, cake slice, serving bowl, salon chair, wall shelf, display case, serving tray, treatment bed (one-hole copy), hair clipper, dumbbell, takeaway cup, laptop, reception desk composition (screen toward the staff side; the screen-to-visitor alternative was offered and not chosen), dessert spoon, teaspoon, dessert knife, paper wrap closed and opened, paper-lined tray. Known weak line-art reads approved as is: hair clipper upright looks like a foot, wall shelf reads as a slab, cake slice layer lines break into dashes, display case glass not drawn; small dashes on the burger bun and the treatment bed cushions. T-shirt: owner regenerating. Decisions in `guides/review/decisions/objects.json`.

Request rows closed by this review (moved here):

- Paper wrap and a serving tray for handheld food (wrap folded around a burger or pastry, about 0.25 x 0.25 m sheet; tray about 0.35 x 0.26 m). Nearest existing: none for the wrap; `p0_scenes.plain_card` for a flat sheet. 
- Teaspoon in P0 line art (about 0.13-0.14 m, oval bowl, slim handle; resting on the saucer and held in a stirring pinch). Nearest existing: the procedural `fork` in `assets.py` (same tube-and-lathe build) and the unapprov
- Dessert spoon and dessert knife in P0 line art, for the per-dish place setting (owner rule 2026-11-15: desserts on a dessert plate, ideally with a dessert spoon and knife beside it). Nearest existing: `assets.py` `knife`
- Food truck with a side service window (owner-provided candidate: the owner generated it in Tripo, task 51baebf5, image_to_model v3.1, 30 credits, 2026-11-16; `model_refferences/objects/food_truck/tripo/tripo-out/food-tru
- Existing Tripo model in P0 line art: burger, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_burger.png`
- Existing Tripo model in P0 line art: cake_slice, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_cake_slice.png`
- Existing Tripo model in P0 line art: serving_bowl, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_serving_bowl.png`
- Existing Tripo model in P0 line art: salon_chair, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_salon_chair.png`
- Existing Tripo model in P0 line art: wall_shelf, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_wall_shelf.png`
- Existing Tripo model in P0 line art: display_case, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_display_case.png`
- Existing Tripo model in P0 line art: serving_tray (+ `_top.png`), unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_serving_tray.png`
- Existing Tripo model in P0 line art: treatment_bed (owner-approved one-hole copy `treatment_bed/one-face-hole-v1`), unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_treatmen
- Existing Tripo model in P0 line art: hair_clipper, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_hair_clipper.png`
- Existing Tripo model in P0 line art: dumbbell, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_dumbbell.png`
- Existing Tripo model in P0 line art: takeaway_cup, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_takeaway_cup.png`
- Existing Tripo model in P0 line art: laptop, unchanged shape, default dot cleanup in memory; render `guides/review/objects_renders/candidate_laptop.png`
- Reception desk (composition): the approved procedural `p0_scenes.counter(body=True)` without the espresso block, drying cups and glasses and the card holder, with the Tripo laptop (default dot cleanup) on the counter top

## Audit (2026-11-10)

## 0. Key findings

1. **The approved P0 line-art collection is built almost entirely from procedural Blender geometry, not from the Tripo library.** All 37 active guides call helpers in `guides/blender_motion/assets.py`, `venue_assets.py`, `p0_scenes.py` and `p0_table_compositions.py`: lathe or tube cup, saucer, plate, fork, pasta, croissant, table, chair, window, door, pendant, plant, counter, board and cocktail glass. Only six external sources appear in active P0 scenes:
   - `milk_pitcher/functional`
   - `kettle/tripo-generated/review`
   - `pizza` (Tripo, through a line-art cache)
   - `salad_portion` (Tripo, through a line-art cache)
   - the canonical creator (`model_refferences/creator/lineart/asset.blend`)
   - the CC0 para/MakeHuman hand poses (`guides/blender_motion/vendor/para-fps-arms/hand-poses.blend`)
2. **The 4 November available-models list names different preferred assets from the ones P0 uses.** It recommends the Tripo functional cup, the `approved-v2` croissant and the Tripo dinner plate. P0 instead uses a procedural cup (about 0.108 m body), a procedural croissant and a procedural 0.30 m plate. So "the cup in our style" exists twice, at different scales.
3. **The owner's dish ruling of 2026-11-10 applies to every dish kind.** It says: one shared example dish, pasta on a dinner plate, "until per-kind variants are made" (`guides/p0/guide_levels.json` `exampleDish`). In code, "dinner plate" is the procedural `A.plate`, not the Tripo `dinner_plate`.
4. **Eight pending guides (`guides/p0/guide_levels.json` `pending`) need objects that do not exist in P0 line art:** tap plus pint glass, filled beer glass, a display case readable through glass, a table grill with meat, a yolk, sauce or broth action, and a creator bust at a table. Section 4 lists them as requests.
5. **Style rules live in at least seven places, and four of them still state superseded rules as current.** They cover the watercolor workflow, 65% opacity baked into the image, 25% white fills, and "parametric props rejected" next to procedural P0 props. See section 5.

## 1. Object inventory

Approval key:
- **approved**: used in an active, owner-reviewed P0 guide (`catalog/p0/README.md`, 37 guides, 10 Nov), or explicitly approved in a report.
- **study only**: passed checks in a review collection, not in an active guide.
- **unverified**: file exists, never rendered in P0 line art.
- **rejected**: owner ruling or status file.

### 1a. Objects in active P0 guides (approved style, by use)

| id / helper | Category | Format, path | Source | Status | Evidence |
|---|---|---|---|---|---|
| `cup()`: ceramic cup, open handle, coffee surface, foam heart or rosetta | drinkware | code: `guides/blender_motion/assets.py` `cup`, `p0_scenes.py` `cup` | procedural (lathe/tube) | approved | 20+ active guides (pour, steam, counter, menu, room, handoff, sip) |
| `saucer` | tableware | `assets.py` `saucer` | procedural | approved | always paired with the cup |
| `plate` ("Plate with formed rim", 0.30 m) | tableware | `assets.py` `plate` | procedural | approved | plate guides, table settings, table compositions |
| `platter` (broad flat plate) | tableware | `p0_table_compositions.py` `platter` | procedural | approved | table_spread_orbit, pancake_clear_path |
| `fork` (four tines, 0.19 m) | tableware | `assets.py` `fork` | procedural | approved | plate, menu-card and bite guides; hero in bite_pip_dish |
| knife | tableware | `assets.py` `knife` (0.236 m: rounded blade with a slight belly, bolster, handle; 2026-11-11 reshape), used by `p0_scenes` handoff_plate_lands, `drafts/counter_v2` and `venue_assets.dining_table` | procedural | approved, background only | handoff_plate_lands, room settings |
| water glass | drinkware | `geometry.py` `glass` (tall straight tumbler 0.08 x 0.125 m, water line 2/3 up; `water=False` for an empty glass; 2026-11-11 reshape) | procedural | approved, support | room guides, handoff_plate_lands |
| cocktail glass (shell, liquid surface, straw, 3 ice cubes at three depths since 2026-11-11) | drinkware | `p0_table_compositions.py` `cocktail` | procedural | approved | table_spread_orbit, glass_slide_close, pancake_clear_path (owner corrected the grip, `owner-corrections-report.md`) |
| `pasta` (pasta plate with basil leaf) | food | `assets.py` `pasta` | procedural | approved; owner's example dish for all kinds | `guide_levels.json` `exampleDish` |
| `pastry` (two-half croissant) | food | `assets.py` `pastry` | procedural | approved, support | steam_push_in_high, steam_slide_pull_out |
| bread loaf | food | `p0_table_compositions.py` `bread` | procedural | approved | table compositions |
| pancake stack (butter, cream, berry, syrup) | food | `p0_table_compositions.py` `pancakes` | procedural | approved | pancake_clear_path |
| pizza | food | `model_refferences/objects/pizza/tripo-generated/review/asset.blend`, cleaned cache at `pizza/lineart/asset.blend` (voxel remesh 1.5 mm, smooth, decimate 0.4, Z scale 0.55); cut in memory into 8 slices, one pulled out (`p0_table_compositions.slice_round`, 2026-11-11) | Tripo multiview from imagegen art | approved in P0 | table_spread_orbit; `table-composition-report.md` |
| salad portion | food | `salad_portion/tripo-generated/review`, cache at `salad_portion/lineart` | Tripo multiview | approved in P0 | table_spread_orbit, pancake_clear_path |
| milk pitcher | equipment | `milk_pitcher/functional/asset.blend` (+ spout anchor in `metadata.json`) | Tripo image, locally functionalised | approved in P0; the status file still says `functional_asset_pending_contact_validation` | pour_top_down_latte |
| gooseneck kettle | equipment | `kettle/tripo-generated/review/asset.blend` (remesh 1.2 mm, smooth, decimate 0.35) | Tripo image | approved in P0; status file `review_candidate`; the older parametric `kettle` at top level is `rejected_reference_mismatch` | pour_side_low, pour_upside_down; `followup-report.md` |
| milk stream, steam strands, light-edge cues | effects | `p0_scenes.py` (tubes, shape keys) | procedural | approved | pour, steam |
| menu card (unlettered rows) | venue | `p0_scenes.py` `plain_card` | procedural | approved | menu_card_*, room guides |
| menu board, three columns (unlettered bars, left-aligned ragged-right rows since 2026-11-11, lamps) | venue | `p0_scenes.py` `board` | procedural | approved | menu_board_*, counter_* |
| counter (+ optional cabinet), espresso machine block turned 90 deg clockwise to the barista side, seated on the counter, portafilters and baskets, no steam wand, 2 cups and 2 glasses drying upside down on top (owner 2026-11-11; per-shot `machine_offset`), card holder | venue/furniture | `p0_scenes.py` `counter` | procedural (box machine, not the Tripo machine) | approved | counter, pour, handoff_counter_cup, menu_board |
| round table | furniture | `assets.py` `table` (inner ring tried 2026-11-11, dropped by the owner) | procedural | approved | most table guides |
| two-person dining table with settings | furniture | `venue_assets.py` `dining_table` | procedural | approved | entrance and room guides |
| long tabletop block | furniture | `p0_table_compositions.py` | procedural | approved | pancake_clear_path |
| dining chair | furniture | `venue_assets.py` `chair` | procedural | approved, background | many |
| window (frame only) | venue | `venue_assets.py` `window` | procedural | approved | entrance, steam, pour, room, people |
| glazed door with hinge | venue | `venue_assets.py` `door` | procedural | approved | entrance_* |
| venue sign, hanging bracket, downlight | venue | `p0_scenes.py` `entry_sign` | procedural | approved | entrance_* |
| A-frame welcome stand, facade ground line | venue | `p0_scenes.py` `facade_ground_and_welcome` | procedural | approved | entrance_walk_in, entrance_sign_tilt |
| pendant lamp | venue | `venue_assets.py` `pendant` | procedural | approved | many |
| floor plant | decor | `venue_assets.py` `plant` (not `model_refferences/objects/plant/asset.blend`) | procedural | approved | steam, room_reveal_plant, people |
| partition planes | venue | `p0_scenes.py` `room` | procedural | approved | room guides |
| schematic mouthless bust | person | `assets.py` `portrait` | procedural | approved only as a faint static barista | counter_through_cup_handle (an explicit owner request, `followup-report.md`) |
| canonical creator (65-bone rig, original hands) | person | `model_refferences/creator/lineart/asset.blend` (welded, about 90k faces) from `creator/tripo-rigged/review/asset.blend` | Tripo rig on the approved creator mesh | approved, local/API only, not public | 8 people guides; `people-guides-report.md` |
| cropped anatomical hands (pinch, point, relaxed) | hands | `guides/blender_motion/vendor/para-fps-arms/hand-poses.blend` via `real_hands.py` | CC0 MakeHuman by para | approved only in the three owner-requested grips | bite_pip_dish (fork), glass_slide_close, pancake_clear_path |
| burger | food | `burger/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16; a few small dashes on the top bun, approved by the owner as is | render `candidate_burger.png`; no active guide yet |
| cake slice | food | `cake_slice/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16; known weak line-art read (layer lines break into dashes), approved by the owner as is | render `candidate_cake_slice.png`; no active guide yet |
| serving bowl | tableware | `serving_bowl/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_serving_bowl.png`; no active guide yet |
| salon chair | furniture | `salon_chair/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_salon_chair.png`; no active guide yet |
| wall shelf | furniture | `wall_shelf/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16; known weak line-art read (from 30 deg down it reads as a plain slab), approved by the owner as is | render `candidate_wall_shelf.png`; no active guide yet |
| display case | furniture | `display_case/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16; known weak line-art read (busy, glass panes not drawn), approved by the owner as is | render `candidate_display_case.png`; no active guide yet |
| serving tray | tableware | `serving_tray/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_serving_tray.png`; no active guide yet |
| hair clipper | tools | `hair_clipper/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16; known weak line-art read (upright it looks like a foot), approved by the owner as is | render `candidate_hair_clipper.png`; no active guide yet |
| dumbbell | equipment | `dumbbell/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_dumbbell.png`; no active guide yet |
| takeaway cup | drinkware | `takeaway_cup/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_takeaway_cup.png`; no active guide yet |
| laptop | equipment | `laptop/tripo-generated/review/asset.blend` (default dot cleanup in memory) | Tripo (existing model) | approved in P0 line art 2026-11-16 | render `candidate_laptop.png`; no active guide yet |
| treatment bed (one face hole) | furniture | `treatment_bed/one-face-hole-v1/asset.blend` (owner-approved one-hole copy) | Tripo + local one-hole edit | approved in P0 line art 2026-11-16; a few small dashes on the cushions, approved by the owner as is | render `candidate_treatment_bed.png`; no active guide yet |
| food truck (side service window) | venue | `food_truck/lineart/asset.blend` (cache: x2.5, 3.0 m tall, about 4.7 m long, decimate 0.1, dot cleanup, front +X, window +Y; `food_truck/prepare_lineart.py`) from the owner's Tripo download | Tripo image_to_model v3.1, owner-generated, task 51baebf5, 30 API credits | approved in P0 line art 2026-11-16 | renders `candidate_food_truck.png`, `_side`, `_street`; no active guide yet |
| reception desk (composition) | venue/furniture | code: `p0_scenes.counter(body=True)` without espresso block, drying cups and glasses, card holder; Tripo laptop on top, screen toward the staff side | procedural counter + Tripo laptop | approved 2026-11-16 as rendered (screen toward the staff side; the screen-to-visitor alternative was offered and not chosen) | render `candidate_reception_desk.png`; no active guide yet |
| dessert spoon | tableware | code: `guides/blender_motion/assets.py` `assets.spoon()` (0.18 m) | procedural | approved in P0 line art 2026-11-16 | render `dessert_spoon.png` (+ `_top`, `_side`); no active guide yet |
| teaspoon | tableware | code: `guides/blender_motion/assets.py` `assets.spoon(length=.135)` (0.14 m) | procedural | approved in P0 line art 2026-11-16 | render `teaspoon.png` (+ `_top`, `_side`); no active guide yet |
| dessert knife | tableware | code: `guides/blender_motion/assets.py` `assets.knife(length=.20)` (approved knife scaled; default unchanged) | procedural | approved in P0 line art 2026-11-16 | render `dessert_knife.png` (+ `_top`, `_side`); no active guide yet |
| paper wrap, closed | food packaging | code: `guides/blender_motion/assets.py` `assets.paper_wrap()` | procedural | approved in P0 line art 2026-11-16 | render `paper_wrap_closed.png` (+ `_top`, `_side`); no active guide yet |
| paper wrap, opened | food packaging | code: `guides/blender_motion/assets.py` `assets.paper_wrap(opened=True)` | procedural | approved in P0 line art 2026-11-16 | render `paper_wrap_open.png` (+ `_top`, `_side`); no active guide yet |
| paper-lined tray | tableware | code: `guides/blender_motion/assets.py` `assets.paper_tray()` (0.36 x 0.27 m) | procedural | approved in P0 line art 2026-11-16 | render `paper_tray.png` (+ `_top`, `_side`); no active guide yet |

### 1b. Line-art study only (passed checks 4 Nov, not in active P0)

Evidence: `catalog/lineart-study/objects/README.md`, `completion.json` (960 frames passed).

| id | Category | Path | Source | Status |
|---|---|---|---|---|
| latte_cup (functional, hollow) | drinkware | `model_refferences/objects/latte_cup/functional/asset.blend` | Tripo image + local functional prep | study only; status file `functional_asset_pending_contact_validation` |
| saucer | tableware | `saucer/reconstructed/asset.blend` | TripoSR from clay art | study only (`reviewed_for_scene_proof`) |
| croissant approved-v2 | food | `croissant/approved-v2/asset.blend` | Tripo plus local derivative | owner-approved shape (`local_approved_shape_derivative`); study only in line art |
| serving tray | tableware | `serving_tray/tripo-generated/review/asset.blend` | Tripo | study only |
| cake slice | food | `cake_slice/tripo-generated/review/asset.blend` (scaled to 80% in the study) | Tripo multiview (primary target) | study only |
| dinner plate (0.26 m) | tableware | `dinner_plate/tripo-generated/review/asset.blend` | Tripo multiview (primary target) | study only |

### 1c. Library models that exist but were never rendered in P0 line art

Formats: every `tripo-generated/review/` has `asset.blend` and `model.blend`, plus the original GLB under `tripo-out/`. The 16 primary targets also have normalized `model.glb`, `model.usdz`, `geometry-proxy.glb/.usdz` and `component.json` with anchors. They are served by `/v1/guide-objects`, index in `/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/guide-objects.json`.

Source: every Tripo job was `image_to_model` (14) or `multiview_to_model` (16) from built-in imagegen reference art. None is Tripo text-to-model (`model_refferences/tripo-cli/*.json`).

Status: every model below is `review_candidate` unless noted. None is approved in line art.

| Category | Models (status if not `review_candidate`) |
|---|---|
| Drinkware | takeaway_cup (0.126 x 0.16 m); drinking_glass `scene-ready` (`locally_corrected_scene_candidate`); stemmed_glass (primary target); bottle; latte_cup `tripo-generated/review` |
| Coffee equipment | espresso_machine `functional` (pending contact validation); coffee_grinder `functional`; portafilter `functional`; coffee_tamper; knock_box |
| Food | burger (primary); brunch_toast (primary); croissant_oozing `approved-v2` (used in older glass guides) |
| Tableware | serving_bowl (primary); kitchen_tongs (the tong *grip* was rejected, see 1d) |
| Furniture | dining_table; dining_chair (`rendered_pending_visual_review`); bar_counter; bar_stool `scene-ready` |
| Bakery | display_case (1.25 m; glass-pane occlusion pass not solved, `available-models.md`); pastry_rack; pastry_box; bakery_oven (primary) |
| Venue | glazed_door `scene-ready` (`derived_asset_pending_scene_validation`); window `scene-ready` and `full-height` (`native_full_height_window_ready`); wall_shelf `scene-ready`; menu_board; pendant; beer_tap (primary, 0.46 m) |
| Work | laptop (used in the glass-hologram work-corner guides) |
| Other venue kinds | acoustic_guitar, dumbbell, hair_clipper, salon_chair, treatment_bed, tshirt (all primary targets) |
| Supplemental local | rack_shelf_tray `reconstructed` (TripoSR); plant `asset.blend` (`model_built`) |
| Characters | barista and friend_locs `tripo-rigged/review` (65-bone rigs, `model_refferences/tripo-cli/README.md`), not used in P0; heads and bodies under `*/reconstructed` (TripoSR) |
| Legacy procedural, older glass/colour pipelines | `food_assets.py` burger, card, open_box, held_tongs, tool; `venue_assets.py` pastry_case (2.3 m, no glass), salon chair/station/tools, garment, rack, bench, treatment_bed, facade/food truck, dumbbell; tabletop grill block in `food_scenes.py`; guitar from `vendor/innerscene-guitar/guitar.glb` |

The TripoSR clay reconstructions of 28 Oct are 13 props, all `reviewed_for_scene_proof` (`model_refferences/objects/reconstructed-manifest.json`): croissant, croissant_oozing, dining_chair, dining_table, latte_cup, saucer, bar_counter, bar_stool, wall_shelf, bottle, drinking_glass, rack_shelf_tray, pastry_rack. Only the saucer reached the line-art study.

### 1d. Rejected or withdrawn (do not reuse without the owner)

| Item | Ruling | Evidence |
|---|---|---|
| 16 parametric prop prototypes (top-level `<id>/metadata.json` = `rejected_reference_mismatch`): bar_counter, bar_stool, croissant, croissant_oozing, cup_saucer, dining_chair, dining_table, drinking_glass, espresso_machine, kettle, kitchen_tongs, menu_board, pastry_box, pastry_rack, signboard, storefront | rejected for reference fidelity; builders need `--prototype` | `model_refferences/objects/README.md`, `inventory.md` |
| storefront `reconstructed` | `rejected_structural_fidelity` | metadata |
| cup_saucer `reconstructed` | `superseded_by_separate_vessels` | metadata |
| experimental barista rig; realistic MakeHuman actors (`vendor/makehuman-mpfb/people.blend`) | rejected as cast | `model_refferences/objects/README.md`, `inventory.md` |
| TripoSR character studies (creator, barista, friend_locs and heads, `*/reconstructed`) | "Unapproved character study ... excluded from guide publication" | `reconstructed-manifest.json` |
| coffee pickup cup grip and tong grip (scenes creator-coffee-present, creator-pack-box, creator-box-total) | rejected as unnatural; hand interaction deferred | `catalog/interaction-scenes/withdrawal/report.json` |
| hand-carried plate and airborne cup in the handoff guides | replaced by after-service still objects | `catalog/p0/revision-report.md` |
| talking, chewing, blinking | deferred: the creator has no facial controls | `people-guides-report.md` |
| public hosting of the 8 character guides | declined | `catalog/p0/README.md` |
| sprite and watercolor image guides; the `guides/watercolor/` batch | stopped or rejected | `README.md` (27 Oct section and the rules) |
| design sheets only, never built: cutlery, filled_croissant | none | `inventory.md` (`not_built`) |

## 2. Style audit

### 2a. Rendering correctly in the approved P0 line art

Everything in 1a passed the P0 checks: native strokes, no shaded surfaces, alpha, hero band, support and contact checks, browser playback (`catalog/p0/completion-checks.json`, `saved-scene-checks.json`).

The line-art study (1b) used a different render spec, so a 1b model is not proven at P0 settings. The P0 spec is 405 x 720 at 15 fps, with yellow lighting cues and role alpha from `p0_scenes.ROLE_ALPHA`. The study spec is 1080 x 1920 at 30 fps, 3 px white stroke over a 5 px black underlay at 55%, and no yellow.

### 2b. Made for older styles, unverified in line art

| Older style | Objects made or used for it | Status in line art |
|---|---|---|
| Clay / plasticine colour (TripoSR, 28 Oct) | 13 reconstructed props, pastry rack assembly, character studies | Unverified, except the saucer (study only) |
| Glass hologram, 65% (29 Oct to 2 Nov) | latte_cup functional (scaled 0.67 to 0.9), croissant/croissant_oozing approved-v2 (scaled 0.72 to 0.88), espresso machine, grinder, portafilter, milk pitcher, laptop, pastry rack; scenes in `catalog/glass-rollout/coffee/*/scene.blend` | Unverified, except the pitcher (P0) and cup/croissant (study) |
| Static colour ghost previews of the primary targets (29 Oct) | the 16 primary targets | Only pizza and salad reached P0; cake and plate study only |
| Older native colour pipeline (27 Oct) | `food_assets.py`, legacy `venue_assets.py` items, `food_scenes.py` grill | Unverified |

### 2c. Visible inconsistencies (judgement unless cited)

- **Scale, cup.** The procedural P0 cup body is about 0.108 m across and 0.118 m tall (`assets.py`). The Tripo latte_cup is 0.15 m wide with its handle and 0.09 to 0.11 m tall, and older scenes scaled it 0.67 to 0.9. A cup swapped into a P0 guide without recalibration will change the hero size and break the hero band.
- **Scale, plate.** The procedural plate is 0.30 m; the Tripo dinner_plate is 0.26 m. The cake had to be scaled to 80% to fit the Tripo plate (`lineart-study/objects/README.md`).
- **Scale, other.** The procedural pastry case is 2.3 m wide; the Tripo display_case is 1.25 m. The takeaway cup is 0.126 x 0.16 m, against the 0.09 x 0.13 m the plan wanted (`guides/p0/plan.json`, counter_edge_to_pass). The procedural cocktail glass is 0.19 m tall; the Tripo stemmed glass is 0.21 m and the drinking glass 0.105 m.
- **Detail level.** Procedural objects give a few clean, deliberate contours. Tripo meshes are noisy and are voxel-remeshed, smoothed and decimated at import (`p0_table_compositions.imported_food`, `p0_scenes.reused_pourer`). The line-art study notes that reconstructed edges "can still appear as broken segments" and removes strokes under 12 px. In table_spread_orbit the Tripo pizza and salad sit beside procedural bread, plates and glasses, which mixes two contour densities in one frame.
- **Topology that breaks contours.** Several things cause it:
  - TripoSR or Tripo internal surfaces and open shells: the pitcher is remeshed explicitly to "merge generated internal surfaces".
  - Handle-through-rim artefacts: the study fills the cup with coffee as occlusion geometry to hide them.
  - Glass panes acting as opaque blockers: display case, door, window (`available-models.md`).
  - Pizza flattened by a 0.55 Z scale.
  - The creator's eye texture marks, which become small contour patches (`people-guides-report.md`).
- **Same name, two objects.** "cup", "dinner plate", "croissant", "plant", "espresso machine" and "menu board" each exist as a procedural P0 helper and as a library model. Only the procedural ones are in the approved guides.

## 3. Usage map (active P0 guides)

Objects are read from the scene builders, which win over `plan.json` `sourceSetup` where they differ: for example, plan "takeaway cup" became the ceramic cup, plan "spoon" and "napkin" were not built, and plan hands in the handoffs were removed.

| Guide | Hero | Support / context objects |
|---|---|---|
| entrance_walk_in | door (closed) | sign, welcome stand, 2 windows, 3 dining tables with settings, pendants, plant |
| entrance_door_low | table + 2 chairs | door open 90°, 2 plates, fork, second table, window, plant, furnishings |
| entrance_sign_tilt | sign on bracket, door | welcome stand, furnishings |
| menu_board_truck, menu_board_tilt_up | board columns | counter, espresso block, card holder, 4 cups + saucers |
| counter_over_shoulder | board column + cup | same counter set |
| counter_edge_to_pass | cup + saucer | same counter set |
| counter_through_cup_handle | cup handle (foreground) | counter, faint bust barista, window |
| menu_card_top, menu_card_push | card | table, cup + saucer, fork |
| plate_low_push_in, plate_tissue_slide | pasta plate | table, fork, cup + saucer, chair |
| plate_high_orbit | pasta plate | the same, plus a second plate |
| handoff_plate_lands | pasta plate | table, fork, knife, water glass, chair |
| bite_pip_dish | fork + hanging pasta + 1 hand | pasta plate, table |
| handoff_counter_cup | cup + saucer | counter with cabinet |
| pour_top_down_latte | cup (rosetta) | counter, saucer, milk pitcher (functional), stream, window, chair |
| pour_side_low, pour_upside_down | cup | counter, saucer, kettle (Tripo), stream, window, chair |
| steam_low_backlit, steam_orbit_eye | cup + steam | table, saucer, window, chair, plant |
| steam_push_in_high, steam_slide_pull_out | cup + steam | the same, plus plate + procedural croissant |
| room_reveal_cup, room_seated_pan, room_reveal_plant | room table tops | 3 dining tables, water glasses, cards, pendants, window, plants, partitions, foreground cup; counter (pan); foreground plant (plant) |
| table_spread_orbit | pizza (Tripo) | platter, salad (Tripo) on plate, pasta plate (replaced the bread, published 2026-11-12), 2 cocktails, table, window, plant, chairs |
| glass_slide_close | cocktail rim + ice | 1 hand, plate + bread, table, background |
| pancake_clear_path | pancakes | platter, salad plate, 2 cocktails, 2 hands, long table |
| bite_selfie_eye, bite_friend_three_quarter | creator | fork + forkful, pasta, side table, window, pendant, plant |
| sip_selfie_eye, sip_high_lean, sip_friend_side | creator | cup (prop), saucer, side table, window, pendant, plant |
| verdict_eye_level, verdict_friend_eye | creator | cup + saucer, side table, window, pendant, plant |
| verdict_high_plate | creator | pasta plate on a raised table |

### Good templates for object swaps (same move, different object; judgement)

| Swap | Template guides | Why it is easy | Caveat |
|---|---|---|---|
| Different cup (mug, espresso cup, glass mug, takeaway) | steam_orbit_eye, steam_push_in_high, handoff_counter_cup, counter_edge_to_pass | One `p0_scenes.cup()` helper feeds every cup guide. The camera aims at the cup; hero-only orbit and push-in. | Changing `cup()` changes about 20 guides at once. Swap per guide, or add a parameter. Recalibrate the hero band and the foam/handle occlusion. |
| Different dish on the same plate | plate_low_push_in, plate_high_orbit, plate_tissue_slide, handoff_plate_lands, verdict_high_plate, pending plate_rise_overhead | `place_setting()` puts one dish on the plate. `imported_food()` already cleans and caches Tripo food (burger, brunch_toast, cake_slice, serving_bowl + contents). | The owner ruling keeps pasta for every kind until per-kind variants are approved. bite_pip_dish is a poor template because its fork and hanging strands are built for pasta. |
| Different drink in a glass | glass_slide_close, table_spread_orbit, pancake_clear_path | `cocktail()` is self-contained: shell, liquid surface, straw, ice. A beer glass is the same structure with foam instead of ice. | Grips were owner-corrected. A new glass shape needs the grip refitted, and the hand logic clamps fingers to radius 0.045 m. |
| Different pourer | pour_top_down_latte, pour_side_low, pour_upside_down | `reused_pourer()` aligns any vessel by its spout anchor. | It does not cover a tap pour: the glass moves and the tap stays still. That needs new scene logic. |
| Different side pastry | steam_push_in_high, steam_slide_pull_out | Support role only. | The approved-v2 croissant is the owner-approved shape, but P0 uses the procedural one. |
| Different prop in a person guide | sip_* (cup), bite_* (fork) | The prop is attached to the creator's hand. | Grips are sensitive: the owner rejected earlier grips, and a numeric contact check does not certify a grip. |
| Different main subject in a room or entrance | room_*, entrance_* | Built from room and venue helpers. | Mostly furniture; low value for swaps. |

## 4. Gaps: request list for the owner (no decision made)

The owner decides each item. "Exists" means a candidate file exists but is unverified in line art. Each item still needs a P0 render and the owner's review.

| # | Needed by | Object | Exists? |
|---|---|---|---|
| 1 | tap_pour_low (food-review-pour.build; bar-tasting, bar-night-out, bar-happy-hour pours) | beer tap / tap tower | Exists: `beer_tap` Tripo primary target, 0.46 m |
| 2 | same | pint glass, beer liquid and head (foam), tap stream | Missing. A procedural cocktail-glass variant is possible. |
| 3 | glass_raise_light (food-review-pour.glass) | filled beer or cocktail glass to be held up, bar lights, bar top | Partial: procedural cocktail glass, Tripo `bar_counter`, `pendant` |
| 4 | food-review-pour build ("shake, strain, garnish", `research/menu_item_kinds.md`) | shaker, strainer, jigger, garnish | Missing |
| 5 | bar-tasting.flight / taps | flight paddle with small glasses; tap board | Missing |
| 6 | case_slide_to_item, case_hold_shelf (food-review-sweet.case) | display case, readable through glass, in shelf-height variants | Partial: procedural `pastry_case` (no glass, 2.3 m), Tripo `display_case` (glass occlusion unsolved), `pastry_rack` |
| 7 | same | case contents: donuts, cookies, cake slices, mixed pastries on trays | Partial: croissant (procedural and approved-v2), cake_slice, rack tray |
| 8 | grill_low_hold (food-review-table.action) | tabletop grill (Korean BBQ), meat slices, tongs | Partial: legacy procedural grill block (`food_scenes.py`); Tripo `kitchen_tongs` (tong grip rejected) |
| 9 | same | hot pot pot and burner, broth, dipping | Missing |
| 10 | plate_moment_low_hold | yolk-break dish, sauce pour, broth dip | Partial: Tripo `brunch_toast`; no yolk or sauce action |
| 11 | table_talk_front (food-review-table.how) | creator bust at a table with the spread in the lower third | Exists: creator rig + table compositions. Needs a new scene, not a new model. |
| 12 | Per-kind dish variants (deferred by the 10 Nov ruling) | burger, taco/burrito/sandwich, pizza slice, soup bowl, curry, sushi + chopsticks, noodles, fries/starters, wings, donut, gelato, cake on plate | Partial: Tripo burger, pizza, brunch_toast, salad_portion, cake_slice, serving_bowl; procedural pancakes, pasta. Missing: taco, sandwich, soup with broth, sushi, chopsticks, fries, donut, gelato |
| 13 | Cutlery that was planned but not built | spoon (planned in steam_low_backlit), proper knife, chopsticks, steak knife | Missing (cutlery has a design sheet only) |
| 14 | Drinkware kinds (`menu_item_kinds.md` hot/cold drinks) | mug, small espresso cup, iced drink with condensation, boba cup, teapot, matcha bowl | Partial: takeaway_cup, drinking_glass, stemmed_glass, bottle (all unverified) |
| 15 | food-review-handheld.window, quick-truck-find | order window, food truck front | Partial: legacy procedural `facade(truck=True)` |
| 16 | counter_edge_to_pass (plan intent) | takeaway cup with lid at the pass | Exists: Tripo `takeaway_cup` (0.126 x 0.16 m) |
| 17 | Staff presence (customer-side, faint) | canonical barista in line art | Partial: barista rig exists, not converted. The faint bust is used today. |
| 18 | Talking, chewing, eating guides | facial rig (jaw, lips, eyelids) for the creator | Missing (deferred) |
| 19 | Napkin (plate_tissue_slide setup), receipt (quick-budget-run) | napkin square, receipt | Missing |

Non-food kinds (salon, gym, shops, services) have Tripo primary targets, but no P0 guide uses them. They are out of the P0 binding (`p0/discrepancy.md` row 1).

## 5. Where the style rules are written, and contradictions

| Source | What it states |
|---|---|
| `README.md` top, 10 Nov | Current style: native white contours, dark underlay, restrained yellow light edges, local steam glow |
| `catalog/p0/README.md` "Style and playback" | Shipping P0 spec: no shaded surfaces, walls, floor or baked viewfinder; 405 x 720 APNG at 15 fps; `alphaFactor` 1; runtime 65% before and 30% during capture |
| `.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/p0/animations.md` §2 | P0 clock, hero band, opacity hierarchy, visitor side, two hands at most |
| `guides/cinematic_composition.md` | Role hierarchy and the yellow-cue rule |
| `guides/blender_motion/p0_scenes.py` `ROLE_ALPHA`, `render_p0.py` | Executable truth: role alphas, yellow (1, .73, .17) lighting cues |
| `catalog/lineart-study/README.md`, `objects/README.md` | Study renderer spec: 3 px white over 5 px black underlay at 55%, 1080 x 1920 |
| `README.md` "Rules for every agent", "Filming-guide composition corrections" | Hands, faces, visitor access, place-setting rules |
| `guides/p0/guide_levels.json` | Example-dish ruling, easy/complex rule |
| `catalog/p0/hand-pose-references.md` | Grip references; approved verdict palms |
| `.ai/tasks/VIDEO_EDITOR_IMGLY_REPLACEMENT/shot_overlays_brief.md`; `.claude/skills/shot-overlay/`, `live-guide-authoring/`, `live-shot-guide/` | Older schematic or ghost guidance |

Contradictions:

1. **Watercolor rule still reads as current.** `README.md` "Rules for every agent" says: "use image generation for loose sketches with one translucent watercolor pigment ... apply alpha 0.5 in a final batch export ... Do not draw or trace the illustration from code." P0 is native Blender line art with `alphaFactor` 1, drawn from code. The section is not marked superseded.
2. **Opacity baked into the image.** `guides/blender_motion/README.md` says "Published overlays use 65% whole-image opacity, including their lines", and the README's 28 Oct section says "Publish ghost guides at 65% whole-overlay opacity". P0 uses `alphaFactor` 1 with runtime 65%/30% (`plan.json` decisions, `catalog/p0/README.md`).
3. **Fills.** `shot_overlays_brief.md` calls "schematic contours with selective WHITE fills at 25% opacity" the latest owner preference. P0 and the line-art study say no shaded or filled surfaces (`no_broad_filled_regions` check).
4. **Parametric props.** 28 Oct: "earlier parametric prop and character approximations are rejected" (`README.md`, `model_refferences/objects/README.md`). The approved P0 set is built from procedural lathe and tube primitives. The owner's later acceptance is implied by approval of P0 but not written down. Judgement: worth one explicit ruling, procedural line-art props allowed, so that no agent "upgrades" P0 cups to Tripo, or the reverse.
5. **Preferred assets.** `available-models.md` names the functional cup, approved-v2 croissant and Tripo plate as preferred. P0 uses procedural equivalents, and the example-dish ruling names "dinner plate", which means the procedural one.
6. **Two line-art specs.** The study uses white plus black underlay and no yellow at 1080 x 1920. P0 uses role-weighted alpha and yellow cues at 405 x 720. Both are called "line art". Neither document says the study spec is not the production spec.
7. **Status files are stale.**
   - Creator: `reconstructed-manifest.json` marks the creator "unapproved ... excluded from guide publication" (TripoSR study). The approved canonical creator is the Tripo-rigged mesh. The two are different files under the same name.
   - Pitcher and kettle: `milk_pitcher` and `kettle` status files still say pending or review, although both are in approved P0 guides.
   - Old inventory: `model_refferences/objects/inventory.md` lists kettle, espresso_machine and menu_board as rejected. That refers to the top-level parametric prototype, not the Tripo files.
8. **Hands.** 2 Nov: "Defer new character and hand-interaction work" (`README.md`). Three P0 table guides and bite_pip_dish later added cropped grips because the owner asked for them (`queued-table-compositions.md`). `revision-report.md` still says bite_pip_dish "does not demonstrate ... a fork grip", but the later `followup-report.md` added one. The newer report wins; the older text is stale.
9. **Plan vs build.** `plan.json` `sourceSetup` and `p0/animations.md` still list objects the builders dropped or replaced: takeaway cup, spoon, napkin, hands in the handoffs, a "generate" espresso machine. `animations.md` also points to `catalog/guide-objects.json`, which does not exist under ScriptsAndGuides. The real file is `/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/guide-objects.json`. `animations.md` counts 28 guides; there are now 37.
10. **Faces.** "Do not draw mouths, lips, teeth" (`README.md` rules). The canonical creator keeps its original head mesh, and eye marks become contour patches. Whether a mouth contour appears was not verified in this audit (judgement: check one people frame).
