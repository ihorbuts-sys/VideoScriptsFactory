"""Renders the dish variants of plate guides in parallel (drafts/dish_variants.py): per variant a draft folder with
record.json, render, export, contact sheet and the template's published poster; per guide a side-by-side sheet (pasta
plus each dish). Drafts only; an existing variant folder is archived first, never deleted.

    $PY guides/blender_motion/dish_batch.py [guide ...] [--dishes pastry pizza] [--jobs 4] [--date 2026-11-14]
    $PY guides/blender_motion/dish_batch.py [guide ...] --dishes generic

`generic` (owner 2026-11-17) is the yellow dish cycle of drafts/abstract_food_morph.py on the template's plate; it is
not in the default dish list.
    $PY guides/blender_motion/dish_batch.py [guide ...] --compare-templates <scratch dir>

--compare-templates re-renders each template from the current code into the scratch dir and compares its frames
with the published ones, and each owner-approved variant with its draft frames (swap-family rule). Approved variants
are never re-rendered in place."""
import argparse, hashlib, json, shutil, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'
sys.path.insert(0, str(HERE / 'drafts'))
TEMPLATES = ('plate_low_push_in_v2', 'plate_high_orbit_v2', 'plate_rise_overhead_v2', 'plate_top_orbit',
             'plate_tissue_slide', 'handoff_plate_lands', 'handoff_plate_lands_v2', 'room_tilt_up_from_plate',
             'verdict_high_plate_v2', 'plate_turntable')
DISHES = ('pastry', 'pancakes', 'pizza', 'salad')
VERSIONS = DISHES + ('generic',)
# US units (owner rule for record text).
DISH_TEXT = dict(
    pastry='the procedural two-half croissant (approved), about 6 3/4 in long, turned 18 deg',
    pancakes='the procedural pancake stack (approved) scaled 0.75, about 5 in across and 1 7/8 in high',
    pizza='the approved Tripo pizza flattened to about 1/2 in (crust rim a little higher), 10 in across, cut in 8 with '
          'solid cut faces, turned 30 deg, one slice pulled about 1 7/8 in toward the front right',
    salad='the approved Tripo salad portion scaled 0.9',
    generic='the approved dishes cycling in yellow lines (pasta, cut pizza with the pulled slice, cake slice, croissant, '
            'pancakes, salad, back to pasta; one every 0.8 s, each swap a 0.2 s shrink and a 0.2 s growth about the plate '
            'centre), as the abstract_food_morph pilot',
)
# Variants checked on a target probe and not rendered (guide-objects rule "re-render only visible").
SKIP = {
    ('plate_tissue_slide', 'pizza'): 'lens about 3 in above the table: the flat 10 in round is a sliver wider than the '
                                     'frame (runs off the left edge) and does not read as a pizza',
}
# Generic versions made elsewhere: plate_low_push_in_v2's is the abstract_food_morph pilot (not re-rendered).
REUSED = {'plate_low_push_in_v2__generic': 'guides/revisions/2026-11-16-v3/plate/abstract_food_morph'}
# Owner-approved variants (decisions/drafts-2026-11-14.json, every approve choice): never re-rendered or archived by the
# batch; --compare-templates re-renders them to the scratch dir and compares with their draft frames.
APPROVED_ON = {
    '2026-11-15': ('plate_rise_overhead_v2__salad', 'plate_tissue_slide__salad', 'plate_top_orbit__salad', 'plate_turntable__salad'),
    '2026-11-16': tuple(f'{t}__{d}' for t, ds in (
        ('handoff_plate_lands', DISHES), ('handoff_plate_lands_v2', ('pancakes', 'pastry', 'salad')),
        ('plate_high_orbit_v2', DISHES), ('plate_low_push_in_v2', DISHES),
        ('plate_rise_overhead_v2', ('pancakes', 'pastry', 'pizza')), ('plate_tissue_slide', ('pancakes', 'pastry')),
        ('plate_top_orbit', ('pancakes', 'pastry', 'pizza')), ('plate_turntable', ('pancakes', 'pastry', 'pizza')),
        ('room_tilt_up_from_plate', DISHES), ('verdict_high_plate_v2', ('pastry', 'pizza', 'salad'))) for d in ds),
}
APPROVED = tuple(g for ids in APPROVED_ON.values() for g in ids)
APPROVED_DATE = {g: day for day, ids in APPROVED_ON.items() for g in ids}
# Place setting per dish (plate_dishes.PLACE_SETTING, owner rule 2026-11-15), US units.
SETTING_TEXT = dict(
    pastry='on an about 8 in dessert plate (the dinner plate scaled 0.673), no fork, knife or side plate',
    pancakes='on an about 8 in dessert plate (the dinner plate scaled 0.673), fork and knife 3/4 in (2 cm) clear of the '
             'plate edge (knife added mirroring the fork where the template has none)',
    pizza='on the template dinner plate, no fork or knife',
    generic='on the template dinner plate for the whole cycle, no fork, knife or side plate',
    salad='on the template dinner plate, fork and knife 3/4 in (2 cm) clear of the plate edge (knife added mirroring '
          'the fork where the template has none)',
)
PUBLISHED = ROOT / 'catalog/p0/animations-light'
BG = (28, 28, 32)
# Parallel jobs share ARCHIVE.json: one archive move and log write at a time.
ARCHIVE_LOCK = threading.Lock()


def template_record(gid):
    plan = json.loads((ROOT / 'guides/p0/plan.json').read_text())
    return next(g for g in plan['guides'] if g['id'] == gid)


def variant_record(template, dish):
    rec = dict(template_record(template))
    verdict = template == 'verdict_high_plate_v2'
    where = (' The plate rests on the table in front of her (no held plate, no waiter grip); her free hand rests on '
             'the table and she keeps the verdict nod.') if verdict else ''
    rec.update(id=f'{template}__{dish}', title=f"{rec['title']} ({'any dish' if dish == 'generic' else dish})", sourceScene=template, dish=dish,
               availability='draft', newObjects=f'none; {DISH_TEXT[dish]}, {SETTING_TEXT[dish]}',
               sourceSetup=f"As {template} (same camera path, light, hands and timing); the pasta on the plate is "
                           f"replaced by {DISH_TEXT[dish]}, {SETTING_TEXT[dish]}; it moves with the plate.{where}")
    if verdict:
        rec['invariant'] = ("Sit at your table with your plate in front of you and hold the front camera at arm's length, a "
                            "little above your eyes; keep the plate at the bottom of the frame and give your verdict.")
    rec.setdefault('phoneOrientation', 'portrait')
    return rec


def archive(folder, date, reason):
    """Moves an existing draft folder to archive/guides/<date>/dish_variants_batch/ and logs it in ARCHIVE.json."""
    with ARCHIVE_LOCK:
        archive_locked(folder, date, reason)


def archive_locked(folder, date, reason):
    stamp = datetime.now().strftime('%H%M%S')
    name = f'{folder.stem}_{stamp}{folder.suffix}' if folder.is_file() else f'{folder.name}_{stamp}'
    target = ROOT / 'archive/guides' / date / 'dish_variants_batch' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(folder), str(target))
    log = ROOT / 'archive/guides' / date / 'ARCHIVE.json'
    data = json.loads(log.read_text()) if log.exists() else {}
    data.setdefault('rounds', []).append(dict(reason=reason, moves=[dict(id=folder.name, **{
        'from': str(folder.relative_to(ROOT)), 'to': str(target.relative_to(ROOT))})]))
    log.write_text(json.dumps(data, indent=1) + '\n')


def frames_of(render):
    meta = json.loads((render / 'meta.json').read_text())
    lead = 8 + meta['setup_frames']; last = lead + meta['move_frames']
    return meta, [lead + 1 + round(k * (last - lead - 1) / 4) for k in range(5)]


def cycle_strip(render, out, title):
    """Every 2nd demonstration frame of a generic version, 10 per row."""
    meta, _ = frames_of(render)
    lead = 8 + meta['setup_frames']
    picks = list(range(lead + 1, lead + meta['move_frames'] + 1, 2))
    w, h, per = 135, 240, 10
    rows = (len(picks) + per - 1) // per
    sheet = Image.new('RGB', (per * (w + 4) + 4, rows * (h + 18) + 24), BG)
    for k, f in enumerate(picks):
        im = Image.open(render / 'export_frames' / f'frame_{f:04d}.png').convert('RGBA').resize((w, h), Image.Resampling.LANCZOS)
        x, y = 4 + (k % per) * (w + 4), 24 + (k // per) * (h + 18) + 14
        sheet.paste(im, (x, y), im)
        ImageDraw.Draw(sheet).text((x + 2, y - 12), str(f), fill=(200, 200, 200))
    label(sheet, title + ': every 2nd move frame')
    sheet.save(out)


def label(image, text):
    ImageDraw.Draw(image).text((6, 4), text, fill=(235, 200, 80))


def contact_sheet(render, out, title):
    meta, picks = frames_of(render)
    sheet = Image.new('RGB', (405 * 5 + 24, 720 + 40), BG)
    for k, (f, name) in enumerate(zip(picks, ('start', '25%', 'middle', '75%', 'end'))):
        im = Image.open(render / 'export_frames' / f'frame_{f:04d}.png').convert('RGBA')
        sheet.paste(im, (4 + k * 409, 36), im)
        ImageDraw.Draw(sheet).text((8 + k * 409, 20), f'{name} (frame {f})', fill=(200, 200, 200))
    label(sheet, title)
    sheet.save(out)


def guide_sheet(template, folder, date):
    """Pasta (published) and every version made so far: the target frame (poster) on top, the start of the move below
    (the generic column shows its middle frame below). The previous sheet is archived."""
    def render_of(d):
        gid = f'{template}__{d}'
        return (ROOT / REUSED[gid] if gid in REUSED else folder / gid) / 'render'
    columns = [('pasta (published)', PUBLISHED / template)] + [(d, render_of(d)) for d in VERSIONS]
    columns = [(n, r) for n, r in columns if (r / 'export_frames').exists()]
    w, h = 270, 480
    sheet = Image.new('RGB', (w * len(columns) + 8 * (len(columns) + 1), 2 * h + 70), BG)
    for k, (name, render) in enumerate(columns):
        _, picks = frames_of(render)
        for row, f in enumerate((1, picks[2] if name == 'generic' else picks[0])):
            im = Image.open(render / 'export_frames' / f'frame_{f:04d}.png').convert('RGBA').resize((w, h), Image.Resampling.LANCZOS)
            sheet.paste(im, (8 + k * (w + 8), 36 + row * (h + 14)), im)
        ImageDraw.Draw(sheet).text((10 + k * (w + 8), 20), name, fill=(200, 200, 200))
    label(sheet, f'{template}: target (top), start of the move (bottom; generic: middle)')
    out = folder / f'{template}__dishes.png'
    if out.exists():
        archive(out, date, f'dish_variants_batch guide sheet of {template} rebuilt with every version. Restore by moving "to" back to "from".')
    sheet.save(out)


def run(command, log):
    with log.open('a') as stream:
        stream.write('$ ' + ' '.join(command) + '\n'); stream.flush()
        return subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT).returncode


def variant(template, dish, folder, date):
    gid = f'{template}__{dish}'; out = folder / gid
    if gid in APPROVED:
        result = dict(id=gid, status='approved', reason=f'owner approved {APPROVED_DATE[gid]}; kept as rendered')
        print(json.dumps(result), flush=True)
        return result
    if gid in REUSED:
        result = dict(id=gid, status='reused', folder=REUSED[gid], reason='the abstract_food_morph pilot is this guide\'s '
                      'generic version; not re-rendered')
        print(json.dumps(result), flush=True)
        return result
    if (template, dish) in SKIP:
        result = dict(id=gid, status='skipped', reason=SKIP[template, dish])
        print(json.dumps(result), flush=True)
        return result
    if out.exists():
        archive(out, date, f'dish_variants_batch re-run of {gid}: the previous draft is replaced. Draft only, never '
                           'published. Restore by moving "to" back to "from".')
    out.mkdir(parents=True)
    (out / 'record.json').write_text(json.dumps(variant_record(template, dish), indent=2) + '\n')
    shutil.copyfile(ROOT / 'guides/p0/renders' / f'{template}_poster.png', out / 'published_poster.png')
    log = out / 'batch.log'; started = time.time()
    code = run([BLENDER, '-b', '--python-exit-code', '1', '-P', str(HERE / 'render_p0.py'), '--', '--id', gid,
                '--record', str(out / 'record.json'), '--out', str(out / 'render')], log)
    rendered = time.time() - started
    result = dict(id=gid, render_seconds=round(rendered), status='render_failed')
    if code == 0:
        code = run([sys.executable, '-I', str(HERE / 'export_p0.py'), str(out / 'render'), '--out', str(out / 'export')], log)
        result['status'] = 'export_failed'
        if code == 0:
            contact_sheet(out / 'render', out / 'sheet.png', gid)
            if dish == 'generic':
                cycle_strip(out / 'render', out / 'cycle_strip.png', gid)
            meta = json.loads((out / 'render/meta.json').read_text())
            result.update(status='passed', adaptations=meta['pre_render_review']['adaptations'],
                          target_bounds={k: round(v, 3) for k, v in meta['target_bounds'].items()},
                          target_camera=[round(v, 4) for v in meta['camera_samples'][0]['camera_position']])
    result['seconds'] = round(time.time() - started)
    print(json.dumps(result), flush=True)
    return result


def compare(template, scratch):
    """A template against its published frames, or an approved variant against its draft frames."""
    variant = '__' in template
    out = scratch / template; log = scratch / f'{template}.log'
    if out.exists():
        shutil.rmtree(out)
    started = time.time()
    command = [BLENDER, '-b', '--python-exit-code', '1', '-P', str(HERE / 'render_p0.py'), '--', '--id', template, '--out', str(out)]
    if variant:
        draft = ROOT / 'guides/revisions/2026-11-14/plate/dish_variants_batch' / template
        command += ['--record', str(draft / 'record.json')]
    code = run(command, log)
    result = dict(id=template, status='render_failed', seconds=round(time.time() - started))
    if code == 0:
        reference = (draft / 'render') if variant else (PUBLISHED / template)
        worst = 0.; equal = 0; frames = sorted((reference / 'frames').glob('frame_*.png'))
        for path in frames:
            a = np.asarray(Image.open(path).convert('RGBA')).astype(int)
            b = np.asarray(Image.open(out / 'frames' / path.name).convert('RGBA')).astype(int)
            share = float((np.abs(a - b).max(axis=2) > 8).mean()); worst = max(worst, share); equal += int((a == b).all())
        result.update(status='compared', frames=len(frames), bit_identical=equal, worst_share_over_8_levels=round(worst, 5))
    print(json.dumps(result), flush=True)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument('guides', nargs='*')
    p.add_argument('--dishes', nargs='+', default=list(DISHES), help='any of ' + ' '.join(VERSIONS))
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('--date', default='2026-11-14')
    p.add_argument('--compare-templates', type=Path)
    a = p.parse_args()
    if a.compare_templates and not a.guides:
        a.guides = list(TEMPLATES) + list(APPROVED)
    elif not a.guides:
        a.guides = list(TEMPLATES)
    assert all(g in TEMPLATES or (a.compare_templates and g in APPROVED) for g in a.guides) and all(d in VERSIONS for d in a.dishes), (a.guides, a.dishes)
    with ThreadPoolExecutor(max_workers=a.jobs) as pool:
        if a.compare_templates:
            a.compare_templates.mkdir(parents=True, exist_ok=True)
            results = list(pool.map(lambda g: compare(g, a.compare_templates), a.guides))
            (a.compare_templates / 'compare.json').write_text(json.dumps(results, indent=1) + '\n')
            return
        folder = ROOT / 'guides/revisions' / a.date / 'plate/dish_variants_batch'
        jobs = [(g, d) for g in a.guides for d in a.dishes]
        results = list(pool.map(lambda job: variant(*job, folder, a.date), jobs))
    for g in a.guides:
        guide_sheet(g, folder, a.date)
    report = folder / 'batch.json'
    previous = {r['id']: r for r in json.loads(report.read_text())} if report.exists() else {}
    for r in results:
        previous[r['id']] = dict(previous.get(r['id'], {}), owner='approved ' + APPROVED_DATE[r['id']]) if r['status'] == 'approved' else r
    report.write_text(json.dumps(sorted(previous.values(), key=lambda r: r['id']), indent=1) + '\n')
    if any(r['status'] not in ('passed', 'skipped', 'approved', 'reused') for r in results):
        sys.exit(1)


if __name__ == '__main__':
    main()
