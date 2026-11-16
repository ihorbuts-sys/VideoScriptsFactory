# Scene and grip corrections

[Play the updated collection](http://127.0.0.1:8766/p0/index.html). Ten existing guide IDs were replaced in place; the other nineteen animations are byte-identical. There are still 29 active guides and 87 API files. Five person/selfie guides remain deferred.

| Guides | Correction |
|---|---|
| `entrance_sign_tilt` | Close 1.4 m visitor-side position; lower the phone 45 cm while tilting from the centered sign to the door. No pull-back. |
| `room_reveal_plant` | Film from a clear aisle through a floor plant, then slide right. No foreground table under the plant or phone; the room tables are physically separate. |
| `steam_low_backlit`, `steam_push_in_high`, `steam_orbit_eye`, `steam_slide_pull_out` | A floor plant sits in the background beside the window. Fixed light, cup/saucer support and existing camera paths are retained. |
| `handoff_counter_cup` | Cup and saucer sit near a counter corner, with a thick overhanging top, full-height cabinet and sparse front joints visible beneath. The cup stays supported and stationary. |
| `glass_slide_close` | Quarter-turn the grip upright around the glass side; palm behind the glass rather than underneath it. |
| `pancake_clear_path` | Exactly two cropped hands, one on each side. Right hand pulls each drink right; left hand curls over the left salad-plate rim and pulls left. Neither reaches across to push from the opposite side. |
| `table_spread_orbit` | Move salad and bread inward. Every plate rim has at least 6 cm clearance from the table edge; all plates remain away from the table center. |

All 29 export checks, saved-scene checks, staged API checks and live API checks passed. Browser playback checks cover all ten corrected animations, their current content hashes, actual moving pixels, final target holds and 65% image-view opacity. Native checks inspect actual table/plant footprints, phone clearance from leaves, counter support and visible corner, reachable sign-to-door travel, side-grip orientation, rear palm position, outward prop trajectories and plate-rim clearance. Numeric checks do not certify the appearance of a grip.

The local API serves the corrected files using content-hashed URLs. Food Review / Dish and Restaurant / First Visit / Plate still share the three table-sequence assets. Source scenes and frames remain in `animations-light/<guide-id>/`; API masters remain in `../../guides/p0/renders/`. See `owner-corrections-checks.json` for the exact replaced/retained lists and check reports.

White/yellow transparent line art, separate viewfinder/level, fixed feasible lighting and runtime opacity are unchanged. No new guide variants or paid model generations were added; Blender stayed headless. Physical phone capture, mobile UI and Blender 4.x remain untested.
