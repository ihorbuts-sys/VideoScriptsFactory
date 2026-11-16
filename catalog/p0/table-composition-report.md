# Reference-based table sequences

[Play all 29 guides](http://127.0.0.1:8766/p0/index.html). The three new sequences below are available under **Plate reveal**. All three are shared by **Food review / Dish** and **Restaurant / First visit / Plate**; both API steps return the same asset URLs rather than duplicate exports. The previous 26 published animations are unchanged by this batch.

| Guide ID | Gallery title | Demonstration | Motion |
|---|---|---|---|
| `table_spread_orbit` | Rise over the shared table spread | 8 s | A curved rise into an overhead spread of pizza, bread, salad and two cocktails, with gentle ice rotation. Plates sit away from the shared table center. |
| `glass_slide_close` | Slide a cocktail into the close-up | 6 s | A supported glass slides diagonally into a close-up, with a cropped grip and a small sideways camera adjustment. |
| `pancake_clear_path` | Clear the foreground to reveal pancakes | 8 s | A companion clears a near drink right, salad left and a far drink right, while the creator moves beside the table at pancake height. At most two cropped grips; every prop stays supported. |

The raw exports use native white contours with dark underlay, restrained yellow surface reflections, transparent empty space and no baked viewfinder. The app/player applies 65% view opacity once. Clear glasses reveal their meniscus, straws and slowly rotating ice. Existing clay-world pizza/salad meshes are cleaned once and reused; the glass, ice, bread, pancake and plate components are reusable native geometry. No paid generation was needed. Full person/selfie guides remain deferred.

All 29 exports (87 API files, 2640 native frames), saved Blender scenes, browser playback, staged API and live API checks passed. The new native checks inspect ice vertices throughout the take: cubes remain separated and inside the glass; glass and plate bases remain on the tabletop. Browser checks confirm actual animation pixels move, the final pose holds and matches the poster, and runtime opacity is 65%. Both script endpoints return the same three new guide assets. Content-hashed URLs avoid stale cached versions.

Results: `animations-light/<guide-id>/` holds the native scene, frames and playback files. `../../guides/p0/renders/` holds API masters. Use `GET /v1/steps/food-review.dish/guides` or `GET /v1/steps/first-visit.plate/guides` with the existing Bearer token, then follow the returned signed URLs. Evidence is in `table-composition-checks.json` and its linked check files.

Rendered headlessly in Blender 5.2.3 LTS. Numeric contact checks do not certify the anatomy or appearance of a grip. Physical phone capture, the mobile app UI and Blender 4.x were not tested.
