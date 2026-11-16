# Tripo credits estimate

Checked 2026-10-28. Planning estimate, not a guaranteed production quote. No segmentation or rigging has been purchased.

Current execution uses the smaller [shared-core and venue-pack plan](priority-plan.md) within the existing credit balance. The full-library envelope below is not a required purchase. The original table retains its 880-credit checkpoint; after the four-prop batch, 720 remained and the full-library baseline fell to 2,955. The next entrance/menu batch is 120, already contained in that baseline.

Audited all 178 published guides: 473 named components map to 75 planned generated prop families and 16 local/reuse groups. Reuse the three existing canonical characters. The first cafe/bar kit has 30 prop entries; after assembling the rack, cup-and-saucer and filled-croissant variants, it needs 27 distinct generation families.

## Unit prices

| Operation | Credits | USD equivalent |
|---|---|---|
| H3.1 generation with detailed textures, as used in our completed batch | 40 | $0.40 |
| Standard segmentation, per existing model | 40 | $0.40 |
| Smart Segmentation, existing GLB | 55 | $0.55 |
| Rig check | 0 | $0.00 |
| Auto rig, per character | 25 | $0.25 |
| Animation retarget, per preset | 10 | $0.10 |

Source: [Tripo API pricing](https://developers.tripo3d.ai/en/pricing). API credits are priced at $0.01 each. Studio allowances are separate. Our three completed jobs actually consumed 120 credits total. The supplied creator export is already available; its external Studio cost is unknown.

## Remaining work at the 880-credit balance checkpoint

| Scope | New prop jobs | Generation | Two character segmentations | Three character rigs | Total | Additional credits needed |
|---|---|---|---|---|---|---|
| First cafe/bar kit | 26 | 1040 | 80 | 75 | 1195 | 315 |
| All current guide families | 74 | 2960 | 80 | 75 | 3115 | 2235 |

The full remaining baseline is **3115 credits ($31.15)**. A 25% allowance gives 3894 credits; round to **3900 credits** for planning. This is not a spending authorization or a guarantee that all assets will succeed on the first attempt.

The newly authorized four-prop batch (cup, kettle, table, tongs) is estimated at 160 credits and is already included in these remaining counts. As it completes, reduce both the remaining generation cost and the balance by actual consumption. Do not add another 160 to the estimate.

## Character segmentation and talking

Barista and friend are single meshes: reserve 2 x 40 = 80 credits if we need standard segmentation. Creator already has 11 parts: inspect and reuse them before paying to split her again. Segmentation separates surfaces; it neither repairs topology nor supplies a skeleton or mouth controls. Do not segment arms or fingers merely to make them bend.

All three checked source GLBs have zero skins, zero animations and zero morph targets. Keep the existing head identity, review the lips/mouth cavity, clean or retopologize the face where necessary, then build closed-mouth, jaw-open, blink and speech mouth shape keys. A simple closure may only need a local shape key; convincing speech may need lips, inner mouth, teeth/tongue and a facial rig. Replace only the facial mesh if the source geometry cannot deform cleanly. Local Blender editing, shape keys and animation consume no Tripo credits; their labor is outside this credit estimate.

## Planned generation families

| Group | Models | Count |
|---|---|---|
| cafe_bar | rack_shelf_tray, latte_cup, saucer, croissant_oozing, croissant, display_case, bar_counter, dining_chair, dining_table, storefront, signboard, pastry_box, kitchen_tongs, kettle, espresso_machine, menu_board, bar_stool, drinking_glass, bottle, pendant, plant, serving_tray, cutlery, laptop, glazed_door, window, wall_shelf | 27 |
| food_and_drink | plate, coffee_grinder, milk_pitcher, portafilter, tap_fixture, tabletop_grill, oven_front, cash_register, food_truck, burger, pizza_dough, fried_egg, cooked_food, pasta, paper_bag | 15 |
| shopping | tshirt, hanger, clothing_rail | 3 |
| beauty | salon_chair, styling_station, treatment_bed, kit_trolley, treatment_lamp, clipper, hairdryer, hairspray, scissors, comb, round_brush, makeup_brush, crayon, tint_bowl | 14 |
| fitness_and_sauna | exercise_bench, dumbbell, training_frame, sauna_stove, flip_flops | 5 |
| music | acoustic_guitar, keyboard, kick_drum, snare_drum, floor_tom, cymbal, microphone, instrument_stand | 8 |
| activities_and_services | game_table, repair_tool, repair_workpiece | 3 |

## Reuse and local work

- cast: Reuse the three canonical full-body characters for all poses and hand close-ups; no paid generation per pose or hand.
- resource_cards: One locally authored thin card family, with reusable graphic layouts; no generation per menu, price, receipt or tag.
- food_details: Broad clay garnish, cream, crumbs and ingredients assembled or edited locally; not photorealistic simulations.
- cloth: Reuse one simple cloth mesh with folded/draped variants; local deformation setup.
- local_effects: Procedural liquid, steam, light, cracks and floor/wall detail; no paid 3D generation per frame.
- treatment_surface: Derive the close-up massage/skin/nail surfaces from the cast or local patches; no extra human model.
- sculpted_hair: Reuse and deform cast hair meshes; cut locks are local variants.
- drum_seat: Reuse a scaled bar stool with a different material.
- guitar_mount: Derive simple support brackets from the instrument stand.
- stage_structure: Local stage deck, truss and simple light housings; composition and lighting are local.
- attraction_arch: Assemble a wider door/frame variant; no separate generation.
- repair_bench: Reuse the dining table with a local bench-top variant.
- sauna_boards: Local repeated boards derived from the shelf/frame kit.
- coaster: Simple local flat cloth/card variant.
- flight_paddle: Simple local support paddle; repeated tasting glasses reuse the glass asset.
- rack_assembly: Assemble shelf/tray, croissant and support posts; do not generate a fused full rack.

## Assumptions and exclusions

One successful generation attempt per listed family, using the present H3.1 detailed-texture settings. Compound sets such as cutlery and separate moving parts still need local separation/cleanup. Unsupported geometry can require additional candidates or paid part operations. Missing references must be created before their jobs can run.

- Image-generation services and missing projection art.
- Retopology/UV/conversion services; prefer local Blender work when feasible.
- Prop segmentation, part completion, retries, retexturing and replacement candidates beyond the contingency.
- Tripo retarget presets: animate locally unless a preset is useful.
- Facial retopology, lip/jaw/blink shapes, rig cleanup, hand poses and local animation labor.
- Infrastructure, storage, distribution and local rendering hardware cost.

Keep an existing local model only after visual/contact review; each such reuse saves 40 credits. The inventory describes current scene components, not final approval of their composition or every requested correction.

See [credits-estimate.json](credits-estimate.json) for every model and the complete component-to-family mapping.

Latest completed-batch checkpoint: **600 credits remain**, with **400 total CLI generation credits consumed**. Seven further props are now generated. The remaining hypothetical full-library baseline is 2,835 credits, or 915 for the original cafe/bar kit, including the optional 155 for character processing. Current execution follows the much smaller shared-core plan.
