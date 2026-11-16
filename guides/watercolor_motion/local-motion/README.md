# Local painted animation resources

These are live camera-guide assets. Script preview JPEGs are unchanged.

Twelve source resources were generated with the built-in image tool. One additional edit removes the
wine sprite's yellow pigment. `originals/` keeps every untouched output and its metadata; `prompts/`
keeps the prompts. The selected clink source is `clink-hand-glass-blue.png`. Its older color variant is
retained for provenance and is not used. All selected resources use pale slate-blue sketch/waterbrush art.

`assets/` contains derived raster crops, normalized masters and mirrored cutouts. The source paintings
are never redrawn by code. `guide-ids.json` lists this pass's 57 rebuilt guides. `baseline/` preserves the
previous manifest and exact 62-source regeneration report. Previous animation exports are archived under
`catalog/backups/pre-local-motion/animations/`.

Mechanics:

- Camera windows sample a single master for zooms, pans and tilts.
- Multiplane layers use fixed affine transforms, timed by each guide's original motion windows.
- The same wall occluder is shared by seven chair/room guides; palm, cape and cup occluders cover the
  other three reveals. Foreground masks remove background paint before the final composition.
- Three tasting-glass cutouts move at different speeds to show parallax.
- A mirrored glass-and-hand sprite gives exactly two hands for a clink. The camera stays still.
- A single glass-and-hand cutout lowers while the bar background moves upward during a downward tilt.
- The same glass-and-hand cutout rises in front of a mouthless face for a close-up reveal.

Sources are reused where the angle and subject match: the salon chair is the last existing chair atlas
view, the face is the first front/back atlas view, the cape is a cloth-only crop of the existing hair-work
master, and the changing room is cropped from its existing wide painting. Dining/brunch backgrounds are
portrait crops of the new panoramas. The price board is masked out of its existing painting to exclude
all bystanders and their hands. Other audited legacy paintings are used directly as camera masters.

Global alpha is multiplied by 0.5 once after the finished frames are composed. RGB is preserved by that
alpha pass. Fixed horizon, thirds and viewfinder marks remain. Source originals retain their alpha.

A camera crop is an image-plane approximation. True orbits and actor turns require real perspective/pose
artwork. Camera-only guides do not synthesize independent fingers, working actions, pouring or steam.
The full 178-guide audit, exact sources and per-guide limits are in `catalog/local-motion-audit.md/.json`.
No device sensor or physical camera calibration has been performed.
