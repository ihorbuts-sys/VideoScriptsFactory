# Salon station mirror

Plain portrait mirror with a cream frame, faint blue-gray glass, two diagonal glints and an empty sage tool shelf. No reflection, tools, wall, floor or people are included.

- [Reference image](reference.png) and [built-in imagegen prompt](reference-prompt.txt).
- [Prepared GLB](salon-mirror.glb) and [packed Blender asset](salon-mirror.blend).
- [Original Tripo GLB](tripo/tripo-out/salon-mirror-7388f97b/model.glb) and [Tripo preview](tripo/tripo-out/salon-mirror-7388f97b/preview.png).
- [Design dimensions](specification.json), [request](generation-request.json) and [verification](generation-result.json).

One H3.1 image-to-model task cost 30 API credits. Balance after generation: 445 available, 0 frozen. No paid retries or segmentation were submitted.

The prepared copies have a calibrated overall width of 0.6 m, depth of 0.1016 m and height of 0.938 m, including the shelf and gap. Individual frame thickness and mirror height remain approximate reconstructions. The original download is unchanged. Blender import and export passed in headless Blender 5.2.3 LTS.

The prepared origin is the mirror bottom centre at the wall plane. Front faces -Y; up is +Z. Place the root at Z = 1.016 m to mount the mirror bottom 40 inches above the floor. The shelf extends 0.038 m below that origin. Both copies are reusable assets, not a furnished salon scene.

The glints are present in the model's appearance. Separate line-art glint strokes and a faint glass overlay still need to be prepared for the guide-rendering pipeline; no line-art render is included here. Keep the shelf empty until the hair-clipper line art is approved.

`prepare_model.py` reproduces the local axis alignment and assembly-envelope calibration. It does not call Tripo.
