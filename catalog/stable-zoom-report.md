# Stable zoom and close-up rebuild

Date: 2026-10-25 (Europe/Kiev).

**35 clips rebuilt from existing images: 26 zoom guides and 9 held close-ups.** No new AI poses were generated for these clips.

Each clip now samples one saved master illustration throughout its duration. The camera crop changes continuously on zooms; the same pose remains fixed on static close-ups. Object geometry, hands, linework and pigment no longer morph between generated views. The original camera angle, motion timing and fixed viewfinder/horizon are retained. Alpha is applied once at 50% after frames are composed.

View the [updated animation catalog](animations.html); its default filter shows these 35 clips.

| Guide ID | Mode | Master cell | Preview |
|---|---|---|---|
| `burger_cut_high_in_cd_through` | dolly_in | 0 | [Play](animations.html#burger_cut_high_in_cd_through) |
| `burger_cut_high_in_cd_whipout` | dolly_in | 0 | [Play](animations.html#burger_cut_high_in_cd_whipout) |
| `burger_cut_low_in_cd` | dolly_in | 3 | [Play](animations.html#burger_cut_low_in_cd) |
| `burger_low_in_mc` | dolly_in | 0 | [Play](animations.html#burger_low_in_mc) |
| `card_menu_high_in_cd_whipout` | dolly_in | 0 | [Play](animations.html#card_menu_high_in_cd_whipout) |
| `card_menu_top_hold` | hold | 3 | [Play](animations.html#card_menu_top_hold) |
| `card_pricelist_top_hold` | hold | 3 | [Play](animations.html#card_pricelist_top_hold) |
| `card_receipt_top_hold` | hold | 5 | [Play](animations.html#card_receipt_top_hold) |
| `card_tag_high_hold` | hold | 5 | [Play](animations.html#card_tag_high_hold) |
| `card_tag_top_in_cd` | dolly_in | 0 | [Play](animations.html#card_tag_top_in_cd) |
| `card_tag_top_in_cd_through` | dolly_in | 0 | [Play](animations.html#card_tag_top_in_cd_through) |
| `card_ticket_eye_in_cd` | dolly_in | 0 | [Play](animations.html#card_ticket_eye_in_cd) |
| `case_eye_in_mc_through` | dolly_in | 0 | [Play](animations.html#case_eye_in_mc_through) |
| `case_eye_out_cm` | dolly_out | 5 | [Play](animations.html#case_eye_out_cm) |
| `counter_barista_side` | dolly_in | 0 | [Play](animations.html#counter_barista_side) |
| `cup_high_out_dm` | dolly_out | 5 | [Play](animations.html#cup_high_out_dm) |
| `door_curtain_eye_in_md_through` | dolly_in | 0 | [Play](animations.html#door_curtain_eye_in_md_through) |
| `door_eye_in_wd_through` | dolly_in | 0 | [Play](animations.html#door_eye_in_wd_through) |
| `door_pov_in_wc_through` | dolly_in | 0 | [Play](animations.html#door_pov_in_wc_through) |
| `door_pov_in_wd_through` | dolly_in | 0 | [Play](animations.html#door_pov_in_wd_through) |
| `facade_eye_in_wm` | dolly_in | 0 | [Play](animations.html#facade_eye_in_wm) |
| `facade_truck_eye_in_wm` | dolly_in | 0 | [Play](animations.html#facade_truck_eye_in_wm) |
| `glass_drink_high_hold` | hold | 0 | [Play](animations.html#glass_drink_high_hold) |
| `glass_outro_high_out_dm` | dolly_out | 5 | [Play](animations.html#glass_outro_high_out_dm) |
| `glass_pour_eye_in_cd_through` | dolly_in | 0 | [Play](animations.html#glass_pour_eye_in_cd_through) |
| `glass_pour_low_in_cd` | dolly_in | 0 | [Play](animations.html#glass_pour_low_in_cd) |
| `hair_work_high_in_cd_through` | dolly_in | 0 | [Play](animations.html#hair_work_high_in_cd_through) |
| `hand_pov_garment_pov_in_mc` | dolly_in | 0 | [Play](animations.html#hand_pov_garment_pov_in_mc) |
| `hand_pov_item_pov_in_mc` | dolly_in | 0 | [Play](animations.html#hand_pov_item_pov_in_mc) |
| `hands_guitar_high_hold` | hold | 0 | [Play](animations.html#hands_guitar_high_hold) |
| `hands_high_hold` | hold | 0 | [Play](animations.html#hands_high_hold) |
| `hands_stance_top_hold` | hold | 0 | [Play](animations.html#hands_stance_top_hold) |
| `hands_tool_top_hold` | hold | 0 | [Play](animations.html#hands_tool_top_hold) |
| `over_shoulder_hands_os_in_mc` | dolly_in | 0 | [Play](animations.html#over_shoulder_hands_os_in_mc) |
| `topdown_box_top_out_cm` | dolly_out | 5 | [Play](animations.html#topdown_box_top_out_cm) |

## Framing and scope

- Master images are extracted from existing generated artwork; script-preview pictures and original atlases remain unchanged.
- The burger-cut low-angle shot starts from its already-open halves, rather than changing a whole burger into two halves during the zoom.
- Close-up pointing shots use a frame where the finger is already on the menu/price line; their camera view remains steady.
- Push-through end crops magnify the same food, fabric, foam or cape surface. Five end-crop extents are explicitly recorded in the JSON alongside the legacy live-sensor amount.
- These are image-plane zoom previews at a fixed viewing angle. Independent subject actions such as pouring, separating halves or moving a tool are held in the source pose; they are not newly synthesized.
- Very tight crops inherit the source image resolution. Native sensor scenarios were not changed or device-calibrated.
- Previous clip exports are preserved in `backups/pre-stable-zoom/animations/`.

Machine-readable master provenance, hashes, crop rectangles and zoom factors are in [stable-zoom-report.json](stable-zoom-report.json).
