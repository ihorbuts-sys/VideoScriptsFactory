# Blender guides: leftovers audit (2026-10-27)

Audit of the Blender guide rollout after the last Codex session (26 October, work until 22:59), plus a trial of
the CC0 hand models across the remaining hand scenes.

## Where the rollout stands

- 178 library guides. 137 are published to the dev API as Blender guides (last publish 26 Oct 20:41,
  `api/blender-publication.json`); 41 people guides are deferred at the owner's request and keep their
  watercolor or schematic art.
- `work-plan.json` still says `object_and_hand_rollout_complete_people_deferred`; it does not record the work
  done after 20:39 (CC0 hands, the 22:5x re-export).

## Leftovers

| # | Leftover | Count | State |
|---|---|---|---|
| 1 | Published guides whose render changed after review (re-exported 22:54-22:59) | 78 | Need a visual review, then publish |
| 2 | Reviewed renders never published (live API serves the older render) | 29 | Ready to publish |
| 3 | Published guides that are current (live = local = reviewed) | 30 | Nothing to do |
| 4 | Published guides still drawn with the old schematic hands (blob palm plus tube fingers) | 28 | See "Hands" below |
| 5 | People guides deferred by the owner | 41 | 39 rendered but not exported, 1 (`talking_head_eye_level`) render pending; blocked by `people-policy.json` |
| 6 | Codex's level indicator patch (`api/app-level-patch`): `GuideLevelReading`, `GuideLevelIndicator`, edits to `LiveGuideModel` and `StepCameraView` | 5 files | Reworked in VideoEditorKit (uncommitted): the separate X/Y widget (`GuideLevelIndicator`) is removed; the camera's sight now draws the level itself on every guide page and style (horizon line upright, bubble overhead). `GuideLevelReading` and its tests are kept. `api/app-level-patch` is superseded; do not reapply it |
| 7 | `tools/scriptwriter/server.py` step guide overrides and script sequences | 1 file | Uncommitted in VideoEditorKit; the running dev server uses it |
| 8 | `catalog/blender-animations/index.json` and the review gallery | - | Rebuilt; 137 exported, 59 reviewed (matches 2 + 3) |

Item 1 includes scenes with no visible change (`room_eye_panl_ww` frame matches the live one) and real
redesigns (`hands_garment_high_hold`: folded garment with a price tag), so each needs a look, not a bulk accept.

## Hands

Free models in use, both CC0 and vendored with their source notes:

- `guides/blender_motion/vendor/para-fps-arms`: para / MakeHuman forearms with relaxed, point and pinch poses
  (left and right), contact landmarks for fingertips and grip.
- `guides/blender_motion/vendor/innerscene-guitar`: Innerscene acoustic guitar.

7 published scenes already use the anatomical hands (placed one by one in `cinematic_*` and `order_handoff`).
28 published scenes still use the old builders `assets.hand()` and `food_assets.pointing_hand()`.

Trial (this session): both builders now place the anatomical mesh in the same local frame (grip at the old
grip point, fingertip at the pointer's tip), and `build_scenes.run` removes the old separate wrist and forearm
tubes. Probes of all 28 scenes:

- Better as is (14): `burger_cut_high_in_cd_through`, `burger_cut_high_in_cd_whipout`, `burger_cut_low_in_cd`,
  `hands_tool_top_hold`, `hands_tool_top_hold_whipout`, `hands_high_hold`, `hands_top_hold`,
  `tools_tray_top_hold`, `nails_tech_pov_hold`, `plate_sizzle_low_in_cd`, `hands_dough_top_hold`,
  `topdown_first_top_hold_whipout`, `cup_eye_hold_whipout`, `plate_bite_top_hold`.
- Need per-scene placement (14):
  - life-size hand far too large for the camera: `plate_yolk_high_in_cd`, `room_cupreveal_eye_reveal_dw`
  - forearm through props: `glasses_clink_center`, `plate_kids_top_hold`, `plate_spread_top_hold`
  - hand hidden or gone (it relied on the removed forearm tube): `glass_build_eye_hold`, `tap_pour_glass`,
    `tap_taps_low_tiltd_mm`, `hands_wrap_top_hold`, `hand_pov_item_pov_in_mc`, `hand_pov_garment_pov_in_mc`
  - nails were attached to the old fingers and now float: `nails_turns_eye_hold`, `nails_accent_top_hold`
  - hand and bag read as a person: `topdown_bag_top_hold`

Nothing from the trial is published or exported: the 28 scene folders were restored from
`guides/blender_motion/backups-before-anatomical-hands-scenes` (only probe frames and `proof.jpg` previews
were regenerated). The builder change stays in `assets.py`, `food_assets.py` and `build_scenes.py`; the
originals are in `guides/blender_motion/backups-before-anatomical-hands-<timestamp>`. Any rebuild of these
scenes now gets anatomical hands.

## Next steps

1. Place the hands in the 14 scenes that need it (one scene module edit each), probe, render.
2. Render the 14 good ones in full, then visually review all 28 plus the 78 from item 1, binding each review
   with `accept_review.py`.
3. Publish the reviewed set (items 1, 2 and the hand scenes) with `tools/build_bundle.py` and
   `api/publish_reviewed_assets.py`, then rerun the API checks.
4. Decide on items 6 and 7 in VideoEditorKit (keep and commit, or drop).
5. Update `work-plan.json`, `README.md` and `blender-regeneration-report.md` to the new counts.
