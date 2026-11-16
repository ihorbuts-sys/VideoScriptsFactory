# Creator: Meshy comparison

Status: inputs prepared; no Meshy task has been submitted. API access is missing.

`inputs/` contains unchanged copies of the approved front, left, back and right
creator references. `input-views.jpg` is only a labeled contact sheet for review;
the four separate PNGs are the actual generation inputs. `inputs.json` records
their hashes and the existing local TripoSR comparison model.

The proposed test is one Meshy 7.1 Multi-Image to 3D task, Ultra 2K geometry,
4K textures, PBR, A-pose, no remeshing and no input image enhancement. Exact
parameters and the material prompt are in `settings.json`. Estimated cost is
35 API credits according to Meshy's published pricing checked on 28 October
2026. A paid Meshy API account with available credits is required.

The comparison will use Meshy's four-view input against the existing local
single-view reconstruction. This compares practical results; it is not a
controlled benchmark isolating only the model architecture. Original generated
geometry and textures will be retained before any Blender material cleanup.

## Configure access

Copy `.env.example` to `.env` in this directory, then replace the placeholder
with your Meshy API key locally. This directory is ignored by Git. Never paste
the key into chat. An inherited `MESHY_API_KEY` environment variable also works.

## Run one task

```sh
python3 run.py submit
python3 run.py status
python3 run.py download
```

Submission saves the task ID immediately and reuses it on later calls. If a
submission was attempted but no ID was saved, the tool stops for task-history
inspection rather than automatically creating a second paid task. Status calls
retrieve that same task. Download retains the original GLB and Meshy thumbnails
in `original/`, then records their hashes. None of these commands publishes the
model or changes existing guide assets.

After generation, render both actual meshes with the same framing, scale and
neutral studio light in Blender. Compare the face, sculpted ponytail, hand
anatomy, clothing silhouette, bag side, back and profile views. Provide a
separate uniform-material view for judging shape without texture detail.

Sources: [Multi-Image API](https://docs.meshy.ai/en/api/multi-image-to-3d),
[API pricing](https://docs.meshy.ai/en/api/pricing).
