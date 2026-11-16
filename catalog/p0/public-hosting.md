# Public gallery hosting

The public URL and exact Site/version/deployment IDs are in `publication.json`. Access is public; no local API or sign-in is needed. Only the 29 active P0 guides are included, as 87 animation/poster/selector files. Blender scenes, source frames, internal reports, step pictures and credentials are excluded.

Canonical publishing checkout: `catalog/public-gallery-upload/`. Its `.openai/hosting.json` retains the existing project ID. Use this checkout for Site updates. `catalog/public-gallery-site/` preserves the initial complete local packaging attempt; its history was never published and should not be pushed.

Rebuild with `python3 guides/tools/build_public_gallery.py` from ScriptsAndGuides. Stage large updates in a separate output directory first, then copy changed assets into the canonical publishing checkout in batches below 44 MiB. The host limits each Git push to 64 MiB, so a single full-collection initial push is too large. Preserve the existing remote history and use the Sites source helper for each incremental commit/push. Save and deploy only the complete final archive. Keep credentials in session memory and pass them via hidden stdin, never files or command arguments.

The static root is `dist/`. Local asset checks and a Chromium playback check passed; the responsive layout was checked at 390 px. Native Sites deployment returned success with the public URL. Later local renders require a new publication of the same Site to update this snapshot.

The eight canonical creator guides added on 10 November 2026 are local/API-only by explicit owner instruction. `build_public_gallery.py` excludes them by default. Do not use `--include-character-guides` without a later explicit request to expand publication. The public Site remains at 29 guides.
