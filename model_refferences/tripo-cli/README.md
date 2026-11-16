# Tripo models and coffee ordering kit

Balance checked with `tripo balance --json` on 2026-10-29: **5 API credits available, 0 frozen**. The new purchase has funded 1,000 credits of additional props. Recorded lifetime spending is 1,995 credits from 2,000 funded credits. See [the balance ledger](current-balance.json).

The approved 320-credit phase is complete: 160 for four coffee tools, 80 for two character segmentations, and 75 for three body rigs. It spent 315 credits and retained 5. No paid retargets or automatic paid retries were submitted.

[Open the model gallery](props.html) for 27 generated props, the original references, six model projections, packed Blender files and the rigged cast. [Initial character and chair review](index.html) preserves the source comparisons.

## Coffee ordering first

- Espresso machine, grinder, milk pitcher and detachable portafilter are downloaded and prepared as native Blender assets.
- Takeaway cup, serving tray, empty hinged pastry box and pastry rack have also been generated and prepared with six projections each (160 credits).
- The cup has a real hollow interior. Coffee tools have measured functional anchors; animated contacts still require scene review.
- The existing counter, cup, kettle, table, chairs, menu and door are reused.
- The existing window has a locally adapted 2.8-m full-height variant. It cost no generation credits.
- The approved whole croissant has replaced the rejected shape. Two matching halves are derived locally from that same mesh.
- Creator, barista and friend have 65-bone body rigs. Creator retains 11 mesh parts; barista and friend retain 14 each. The Blender deformation proofs include local elbow and head motion. Finger grips and facial controls are not certified by body rigging.

Source downloads remain unchanged. Models and rig proofs are preparation assets; they do not mean every live guide has been re-rendered or published. Blender runs in the background; no UI is launched without a request.

## Installed CLI

Node 25.6.1 and Tripo CLI 0.8.0 are installed. International login (`ov`) is complete. All seven initial doctor checks passed after funding. Credentials remain CLI-managed outside the project and are never copied into reports.

Completed task IDs and resumable batch state files are retained here. Recover an interrupted task by inspecting or downloading its existing task ID. Do not submit a duplicate generation or use a fresh batch run as a retry.

## API credits

The developer API and Studio balances are separate. This ledger records the API wallet used by the CLI.

- [API billing](https://developers.tripo3d.ai/billing)
- [Studio subscriber API-credit claim](https://studio.tripo3d.ai/cli)
- [Full inventory estimate](credits-estimate.md), a planning estimate rather than a spending commitment

Spending after the 2026-10-29 balance (newest first):

| Date | Item | Task | Credits | Wallet | Balance before -> after | Who |
|---|---|---|---|---|---|---|
| 2026-11-16 | Food truck with side service window (image_to_model v3.1, standard texture, from `objects/food_truck/reference-aligned.png`) | 51baebf5-a44b-4b95-b775-cd1a09e12372 | 30 | API wallet (CLI): the upload key prefix `tcli_` in `task.json` marks a Tripo CLI task, and the CLI spends the API wallet | 505 -> 475 | owner |
| 2026-11-16 | Salon station mirror with empty tool shelf (image_to_model v3.1, from `objects/salon_mirror/reference.png`) | 7388f97b-1d07-4818-a574-c5c1d339fa71 | 30 | API wallet (CLI) | 475 -> 445 (balance after from `objects/salon_mirror/README.md`) | owner |
| 2026-11-16 | T-shirt slim v2, empty flat garment (image_to_model v3.1, from `objects/tshirt/slim-v2/reference.png`) | 2d3fe51d-0f90-465b-a5e3-2b9730d8f679 | 30 | API wallet (CLI) | 445 -> 415 (balance after from `objects/tshirt/slim-v2/README.md`) | owner |

The 505 balance before this task means about 500 credits were added after the 2026-10-29 check (5 left then); that top-up is not in `current-balance.json`.

## Tripo project context

The CLI automatically stores `last_task_id` in `.tripo/context.json`. At the owner's request this file was moved from Loca to `/Users/ihor.buts/Documents/Development/VideoEditorKit/.tripo/context.json` with its contents unchanged. Future Tripo commands run from VideoEditorKit. Existing asset files and manifests retain their current absolute paths.

## Parallel fixture and accessory batches

Wall shelf and pendant were generated concurrently from existing approved reference art (80 credits). Tamper and knock box were generated concurrently from new built-in imagegen references (80 credits). All four jobs succeeded with no retries. Scene editing and reference generation continued alongside those jobs. The current balance is 5 credits.

## Primary targets for static overlays

The owner authorized the remaining 645 credits and prioritized separately usable
filming targets over secondary decoration. Sixteen new models cost 640 credits;
5 remain. No paid retries, segmentation, UV operations or new decorative models
were purchased. [Priority and delivery report](primary-targets-2026-10-29/report.md).

[Open the new component gallery](../../catalog/primary-targets/index.html). Each
target has full-color and static ghost previews, six native projections, packed
Blender files, normalized GLB/USDZ, lightweight proxies and measured anchors.
The API provides `/v1/guide-objects` and `/v1/guide-objects/<id>`. Device LiDAR
registration and scene-specific human/tool contacts have not been validated.
The existing 27-prop gallery remains a separate earlier collection.
