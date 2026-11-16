# Local reconstruction trial

The owner rejected the first parametric prop and character prototypes because
they did not follow the generated reference images closely enough. Those models
are archived and must not be used for animation replacement.

The owner selected a local open-source reconstruction test before considering a
hosted service. This test uses the official MIT-licensed
[TripoSR source](https://github.com/VAST-AI-Research/TripoSR) and
[weights](https://huggingface.co/stabilityai/TripoSR).

The first test completed locally on the Apple M1 Pro GPU: 24,088 vertices,
48,172 faces, a watertight mesh, 20.3 seconds for model loading, preprocessing,
inference and mesh extraction after dependency and checkpoint setup. See the
[comparison gallery](reconstruction-trial/croissant-triposr/index.html) and
[actual run report](reconstruction-trial/croissant-triposr/report.json).
The original inferred vertex colors have ring artifacts. The separate clean
clay variant preserves the reconstructed shape, assigns a matte material and
lightly smooths the mesh. Unseen sides remain inferred and need assessment.

- Source commit: `107cefdc244c39106fa830359024f6a2f1c78871`.
- Local environment: `/private/tmp/loca-triposr/venv` (Python 3.11).
- Source checkout: `/private/tmp/loca-triposr/source`.
- Model weights: `/private/tmp/loca-triposr/weights`.
- Dependencies: [tools/local-reconstruction-requirements.txt](tools/local-reconstruction-requirements.txt).
- Runner: [tools/reconstruct_local.py](tools/reconstruct_local.py).
- Trial output: [reconstruction-trial/](reconstruction-trial/).

The source checkout is unchanged. A documented scikit-image marching-cubes
adapter avoids installing the upstream CUDA mesh extraction extension. The
reconstruction network, encoder and weights remain upstream.

This is a single-image model. The selected input view conditions inference;
the other five views are independent comparison targets. Supplying multiple
images to the upstream CLI would create multiple independent models, not a
joint multiview reconstruction. Do not describe it as a six-view reconstruction.

After inference, import the reconstructed mesh into Blender, retain its original
vertex colors, set metre scale and render actual front, back, left, right, top
and bottom views. Check silhouettes, thickness, separated parts and materials
against the references before accepting the mesh. No mass reconstruction,
character rollout or animation publication should follow from a successful file
export alone; the reference-fidelity problem must be resolved first.

Future accepted scenes must provide both a full-color animation and a
transparent ghost animation from the same scene and camera motion. Ghost output
retains the previously requested 65% overall opacity, quiet or absent walls,
fixed feasible lighting and separate app viewfinder/level UI. Every human guide
must use the approved creator, barista or friend with sculpted locs.

## First reusable pack and scene

The owner accepted this local workflow. [Six reconstructed props and two character studies](reconstructed.html) are now available with editable native assets and six actual Blender projections. The original combined cup/saucer reconstruction is superseded by independently reconstructed vessels. The cup liquid is leveled, the saucer thickness is calibrated, and support heights are sampled from the actual geometry. The broken croissant has two editable halves; five tiny detached reconstruction artifacts were removed.

The [coffee orbit proof](../../catalog/clay-scenes/index.html) contains 60 source frames at 15 fps, four seconds, with matching full-color MP4 and transparent ghost APNG exports. Identical APNG frames may be coalesced without changing playback duration. The whole-overlay multiplier is applied once at 65%; contours and fill retain their separate hierarchy. The creator-sip handover remains pending.

The local marching-cubes adapter was checked with a watertight sphere and corrected to export outward winding. Existing reconstructions are repaired during import without altering the retained originals. The six prop assets passed closure, orientation, support-origin and dimension checks. Character models remain studies pending rig, identity and hand/contact validation.

Apple GPU inference works. Blender Metal animation rendering stalled before the first frame on this machine, so the reviewed animation uses CPU Cycles rendering. No Blender UI was launched. Exact new reconstruction-reference prompts are stored beside the images in each asset `design/` directory; those images used the built-in image generation tool.

## Connected bar scene and modular rack

The library now contains **13 reusable prop assets** with six actual Blender projections each, plus **six unapproved character studies**. The additional props are the bar counter, stool, shelf, bottle, clay tumbler, reusable rack shelf/tray and assembled pastry rack. The three approved character identities remain the creator, barista and friend with sculpted locs; none of their current reconstructed meshes is approved for a human guide.

The [bar counter to best table animation](../../catalog/clay-scenes/bar_low_truckr_mm/index.html) is a complete 12-second shot and handover: 180 source frames at 15 fps, matching full-color MP4 and transparent ghost APNG, 65% overall opacity applied once. The opening four seconds match the existing mobile scenario timing: frame for 1.2 seconds, truck 60 cm right for 1.8 seconds, then hold for one second. The same camera lifts, turns through the public aisle and settles on the adjacent two-person table. It never enters the staff area. The saved scene passed 20 actual support-contact checks; its maximum camera speed is 0.523 m/s and turn rate is 38.95 degrees/s. No viewfinder is embedded.

The bar replacement is published in the development API. Both the canonical guide and `restaurant-room-tour.bar` context use the new content-versioned overlay. `GET /v1/guides/bar_low_truckr_mm` also exposes `colorVideoURL`. The full `restaurant-room-tour` sequence reuses the connected bar and best-table section once, for a total of 35.933 seconds; its other sections retain their existing art. The bundle builder reapplies [active scene revisions](../../catalog/clay-scenes/active-revisions.json) after the older native/context assets, preventing a future rebuild from restoring the previous guide or sequence section. The 304 step illustrations and all other guide records are preserved.

The four-level pastry rack is deliberately modular. A locally reconstructed shelf/tray is reused four times; the existing croissant is reused sixteen times. Sage structural uprights are authored support geometry, rather than a claimed neural reconstruction. Every pastry is independently editable, supported by its actual tray surface and at least 4.5 cm inside the tray boundary. An `empty-asset.blend` is also supplied. See [assembly provenance and contacts](pastry_rack/reconstructed/metadata.json).

Monolithic TripoSR and MIT TripoSG fixture trials failed the rack's open structure. TripoSG was tested at both 25 steps / 128 grid and 50 steps / 256 grid; the higher setting still fragmented shelves and posts. The storefront also failed to preserve separate usable openings. These failed trials remain archived and excluded from the usable gallery. A limited CPU/MPS VAE parity check matched signs at all 256 sampled positions, so there is no evidence from that check that local decoder precision explains the structural failure. See [trial review](reconstruction-trial/triposg-review.json).

Remaining work includes functional storefront/door/window assets, the other reusable prop families, canonical character face and body fidelity, rigging, natural hand contact and the remaining guide scenes. The coffee orbit remains an unpublished base-shot proof because its human handover is incomplete. Publishing one connected guide does not complete the 178-guide rollout.
