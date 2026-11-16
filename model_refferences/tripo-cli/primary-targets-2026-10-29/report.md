# Primary filming targets / static-overlay components

Sixteen standalone objects were generated successfully from built-in imagegen reference art and reconstructed with Tripo v3.1. Actual charge: **640 credits**. The checked wallet now contains **5 credits, 0 frozen**. Each paid job was submitted once; no paid retries or processing add-ons were used.

[Open the gallery](http://127.0.0.1:8766/primary-targets/index.html). The models are ready for reuse in Blender scenes and for prototyping static overlays. They are not measured scans, and device LiDAR registration has not been implemented or tested by this batch.

## Chosen targets

|Object|Why it was prioritized|Candidate guide IDs|
|---|---|---|
|`dinner_plate`|Serves as a reusable dish, support surface and large stable alignment target across food reviews and dining.|14|
|`burger`|Primary hero and handheld/cut target in fast-food and menu-item reviews; halves will be derived locally.|7|
|`beer_tap`|Unlocks tap-pour and bar approach guides; separated from the counter and drink.|6|
|`salon_chair`|Large primary salon target with seat, back, base and access-side anchors.|26|
|`serving_bowl`|Reusable bowl and support target for soups, pasta, salads and shared-table guides.|24|
|`acoustic_guitar`|Requested replacement for the poor guitar and primary target for music demonstrations and lessons.|4|
|`dumbbell`|Repeated gym equipment, exercise grip and stable rigid alignment target; racks can reuse instances.|6|
|`tshirt`|Standalone clothing target for picking, labels, try-on and garment rails; hanger can be added separately.|12|
|`bakery_oven`|Primary bakery oven/tray action target; avoids buying a complete room or baked-in food setup.|16|
|`cake_slice`|Adds a distinct dessert subject and cross-section while reusing empty tableware.|8|
|`stemmed_glass`|Separate reusable drink target for wine, cocktails, cheers and dining setups.|14|
|`brunch_toast`|Primary yolk-break/brunch target. Plate and knife remain independent.|10|
|`hair_clipper`|Actual salon filming tool and precise grip/action endpoint target.|8|
|`treatment_bed`|Large primary wellness/appointment scene target with treatment surface and head-end anchors.|8|
|`pizza`|Whole pizza plus locally derived portions supports handheld cross-section and shared-table shots.|13|
|`salad_portion`|Primary food subject for bowl/plate reviews; align using support plane and extent rather than individual leaves.|24|

Candidate counts are keyword-based opportunities, not completed guide replacements. Food, empty tableware and equipment remain independently placeable. Existing cups, tables, chairs, doors, windows, counters, shelves and the canonical cast are reused. No rooms or secondary decorative objects were bought.

## Files and prompts

For each object `<id>`, the files are saved inside:

- `model_refferences/objects/<id>/design-lidar-v1/`: `prompt.txt`, `sheet.png`, front/left/back/right/top/bottom reference crops and two three-quarter crops. References were generated with the built-in imagegen tool, not an API-key fallback.
- `model_refferences/objects/<id>/tripo-generated/tripo-out/`: original GLB and provider task record, preserved unchanged.
- `model_refferences/objects/<id>/tripo-generated/review/`: `model.blend`, appendable `asset.blend`, `model.glb`, `model.usdz`, `geometry-proxy.glb`, `geometry-proxy.usdz`, `component.json`, `ghost-preview.png`, and six native projections in `rendered/` and `shape/`.
- `catalog/primary-targets/`: portable review pages and links to the prepared components.

Use `asset.blend` when appending an independent object. `model.blend` is a review project and also contains its studio camera, lights and review floor. The GLB/USDZ packages and appendable asset contain only the object and its anchors.

The eight-view AI sheets are design references. The six native projections show the actual reconstructed geometry and are the reliable orthographic views of each delivered model. The guitar reference received one built-in image edit (saved as `design-lidar-v1/edit-prompt.txt`); its strings, six bridge pins, tuner connections and fret spacing were then corrected as local geometry. The tap and salon chair were reoriented, and the treatment-bed height was calibrated to 0.76 m. These repairs used no additional Tripo credits.

## Component contract

Blender projects use metres, Z up and front -Y. Normalized GLB and USDZ use metres and Y up; the coordinate mapping is `[x,z,-y]` from Blender. `component.json` contains actual model bounds, dimensions and alignment anchors in both coordinate frames, including exact GLB anchor-node names. The origin lies at the model's bounding-box center in X/Y projected to its measured lowest support plane. That origin is a placement frame rather than a claim that its center touches a physical foot. Named surface anchors are measured against the mesh; opening/grip estimates are labelled accordingly.

Full geometry and the lightweight proxy share this frame. The proxy is intended for registration/render experiments; it is not a certified collision hull. The full model retains its colored materials. Runtime code can apply a ghost material to either geometry variant. The static ghost PNG has transparent empty space and full-strength hero surfaces; the review page applies one 65% image-view opacity multiplier. No animation, floor, room, camera, lighting object or viewfinder is embedded in the component exports.

## API

- `GET /v1/guide-objects?pageSize=100`: the 16-object index.
- `GET /v1/guide-objects?category=food`: category filtering.
- `GET /v1/guide-objects/burger`: normalized GLB/USDZ, proxy, preview, metadata and Blender links, plus dimensions and anchors.

These routes use the existing API authentication. Asset URLs are immutable content-hash paths. The new object index is additive: no script preview, guide animation or full-script sequence was replaced. The existing 178-guide catalog is unchanged; 14 guides are in the approved glass animation treatment from previous batches.

## Verification

- All 16 generations succeeded, one task per model, for exactly 640 credits.
- All 64 full/proxy GLB/USDZ files were re-imported and checked for correct axes, scale, bounds and support origin.
- Both GLB variants for every object contain no animation or character skin. Their anchor transforms match the exported metadata.
- All 16 static ghost previews retain transparent background and full-strength subject alpha.
- The live API test downloaded and hash-checked 240 assets, including all six projections per object, and checked MIME types, pagination, filtering and unknown IDs.
- All 16 review pages loaded color/ghost previews, all six projections and the reference sheet at mobile width, with no horizontal overflow.
- Device registration, human grips, moving mechanisms and scene-specific contacts still require their own setup work.

Evidence: [export round-trip](export-roundtrip.json), [anchor/static checks](anchor-static-checks.json), [live API checks](live-api-check.json), [visual review](visual-review.json), [final balance](final-balance.json) and the resumable wave state files.
