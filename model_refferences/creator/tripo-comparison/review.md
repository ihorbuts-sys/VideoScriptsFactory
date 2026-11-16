# Imported creator: Tripo comparison

The user supplied `../3d female character.glb`. Its embedded generator metadata
identifies Tripo. No new Meshy generation was submitted.

The [comparison page](index.html) provides front, back, anatomical left/right,
top/bottom, three-quarter, face and hand views. Textured and uniform-material
renders use the same studio lighting and camera positions for the imported
model and the earlier local TripoSR creator. Heights are normalized to 1.72 m
solely for comparison, not as a claim about the original character's dimensions.

## Files

- `creator.blend`: directly openable Blender model with studio lights, camera
  and all 33 imported image maps packed inside.
- `asset.blend`: appendable collection containing the model and placement root.
- `tripo/` and `local-triposr/`: original-material comparison renders.
- `tripo-shape/` and `local-shape/`: uniform-material geometry renders.
- `comparison-front.jpg` and `comparison-face.jpg`: two-model contact sheets.
- `metadata.json`: imported parts, texture sizes and calibration.
- `source-checks.json`: independent original GLB geometry/image checks.

The supplied GLB remains unchanged. The Blender copy preserves its original
geometry and material setup; it applies only a uniform root scale, orientation
and ground translation. The review floor's top is at the normalized shoe
support plane. No geometry repair, decimation, UV repacking or texture repaint
was applied.

## Visual assessment

This is a substantially better starting point than the local reconstruction.
The face and eyes are recognizable, the ponytail has broad sculpted locks,
and clothing, sneakers and the bag have clearer silhouettes. The pink bag
remains on the character's anatomical right side. Separate mesh parts are
useful for further editing.

The eye textures have artifacts visible in close-up. The relaxed hand views
are more readable, but they do not establish natural finger deformation or a
working cup/menu grip. Those require rigging and an actual action test.

## Measured properties and limits

- 11 mesh parts, 1,992,809 triangles.
- 33 embedded image maps: 256×256, 512×512 and 1024×1024. No 4096×4096 map is
  embedded in this file. The generation/export settings were not supplied,
  so the reason for per-part resolution allocation is unknown.
- No skeleton, skinning or animation in the supplied GLB.
- Raw GLB boundary-edge counts include duplicate UV/normal seam vertices.
  A diagnostic position weld reduces the count to 9,880 across all parts.
  Open clothing and segmented interfaces alone do not establish a faulty model;
  the diagnostic does not certify deformation quality or watertight printing.
- Source images/view count used in Tripo are unknown. The existing local model
  used one front image, so this is a practical visual comparison rather than a
  controlled same-input benchmark.
- The native file is a comparison candidate, not an animation-ready approval.
  It has not replaced guide models, rendered guide animations or API assets.

Next useful test: prepare a separate rig/retopology working copy and verify one
head turn and one close-up supported-cup grip, preserving this imported original.
