# Slim T-shirt, version 2

The new reference and Tripo reconstruction replace the inflated torso-shaped design with a flatter empty garment. The original version and raw Tripo download remain unchanged.

- [Reference image](reference.png) and [built-in imagegen edit prompt](reference-prompt.txt).
- [Prepared upright GLB](tshirt-slim.glb), [Blender asset](tshirt-slim.blend), [preview](preview.png) and [side inspection](side.png).
- [Flat-laid shelf GLB](tshirt-shelf-flat.glb): the same garment laid horizontally, unfolded, with the front upward and its lowest surface at Z=0.
- [Raw Tripo model](tripo/tripo-out/tshirt-slim-v2-2d3fe51d/model.glb), [request](generation-request.json) and [verification](generation-result.json).

One H3.1 task cost 30 API credits; 415 credits remained afterward, with 0 frozen. No paid retries, segmentation or additional model generations were submitted.

Tripo still introduced body depth and returned a white surface. Local preparation aligns the garment, calibrates it to 0.50 m wide by 0.65 m tall by 0.025 m maximum depth, and restores the plain matte yellow material. This flattening is an explicit geometry adjustment, not a claim that Tripo produced that thickness directly. The prepared dimensions were measured and checked in Blender 5.2.3 LTS.

The upright origin is at the bottom centre; up is +Z and front is -Y. It is an empty reusable garment with no embedded hanger or human. Fit against a specific hanger and cloth deformation have not been tested. The shelf version is flat-laid, not folded.

`prepare_model.py` reproduces the local preparation, exports and inspection renders without calling Tripo.
