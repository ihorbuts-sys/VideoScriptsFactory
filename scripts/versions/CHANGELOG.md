# Catalog changelog

## v3 (planned, design 2026-11-16)

Design: `research/p0_v3_design.md`. Script kinds (`dish-review`, `drink-review`, `menu-item-review`, `venue-review`)
with `kind` as identity; step roles (arrive, place, before, main, after, amenities, verdict) with optional steps; one
`variants` list with `when` keys replacing `lineVariants`, `noPrice` and `servingVariants`; choice sets (opinions and
amenities); dish and drink kinds plus tags; venue subjects by category; serving forms for guides. Not built yet:
waits for the owner's review of the design file. Snapshot of v2 taken first: `v2_2026-11-16/`.

## v2 (2026-11-13 to 2026-11-14)

Opinion slots and opinion sets, silent cards, line checker L1-L14, `noPrice`, `line: null` on complex steps, guide
metadata (showsFace, needsHelper, guideVisibleToCreator, US units), handheld serving variants, typed dish
(`food-review-typed`, `dishSource`), first visit takes a dish at the start. Snapshot: `v2_2026-11-16/`.

## v1 (to 2026-11-12)

Guided v0 scripts with `line`, `caption`, `prompter`, caption options and `titleFacts`; the 2026-11-12 publish of 26
guides. No snapshot folder (git history of this repo holds it).

## v3 (2026-11-16)

Built from `scripts/_parts/v3/` by `check_scripts.py --v3 --merge` into `scripts/catalog_v3.json`; the bundle writes it
as `catalog_v3.json` with `build_bundle.py --catalog-version 3`. v2 (`script_templates.json`, `catalog.json`) is built
and served as before, so rolling back is: stop serving `catalog_v3.json` (and `restore.py v2_2026-11-16` for the files).

- Four kinds with `kind` as identity: dish-review, drink-review, menu-item-review (steps from the derived kind),
  venue-review. No mapping from v2 ids.
- Step roles arrive, place, before, main, after, amenities, verdict; Ordering, First bite and Amenities optional; a
  venue subject's pattern decides which of before, main, after is required.
- `versions` pools (3-5 per step, tagged by daypart or menu section) replace `lineVariants`, `noPrice` and caption
  options; `variants` with `when` (kind, subject, dishKind, drinkKind, serviceKind, price) replace `servingVariants`.
- `choiceSets` (5 levels, own words, "Not for me" on verdicts; verdict never preselected) replace `opinionSets`;
  amenity set with 4 chips (non_smoking as an AI fact).
- Tables: dish kinds, drink kinds (beer and wine, cocktails P1), menu-section keywords (EN, UA stems), venue subjects
  by category (child care excluded), Visit consent and no-clients rule.
- Checker rules V1-V12 plus L1-L14 on every version of every variant (`test_v3.py`).
