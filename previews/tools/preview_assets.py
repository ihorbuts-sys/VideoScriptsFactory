"""Prepare, normalize, and audit phase 02 assets. Generation uses the built-in image tool."""
import argparse
import fcntl
import hashlib
import html
import json
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT.parent / 'scripts'
OLD = ROOT.parents[5] / 'VideoEditorKit/Sources/VideoScripts/Resources/StepPreviews'
STYLE = "Flat editorial illustration, soft grain texture, limited palette of warm off-white, charcoal and one accent colour (terracotta), gentle soft shadows, simple geometric shapes, no text, no logos, no people's faces in detail, 9:16 portrait, the subject large and centred the way the step frames it."
VIEWPOINT_RULE = (
    'Visitor-accessible camera viewpoint only: place the camera in an ordinary customer area. '
    'Never place the camera behind a staff counter or till, inside a working kitchen, at a staff-only prep bench, '
    'or in another restricted area. Show staff activity from the customer side or through a public viewing window. '
    'Do not assume special access. Adapt any conflicting shot direction to a visitor-side view, '
    'using a served item or customer-facing hand-off if the work is not visible from a public area. '
    'Close and top-down framing must remain physically possible without crossing the customer boundary.'
)
HAND_RULE = (
    'At most two visible hands total in the entire image, counted across all people, including partial '
    'and background hands. Zero or one hand is fine. Keep hands anatomically plausible and attached to '
    'their owners. No extra, duplicated or detached hands. Frame all other hands out of the composition.'
)
MAKEUP_RULE = (
    'When makeup or cosmetic application is shown, draw it more schematically: simple face contours, minimal '
    'eye, lip and brow marks, flat accent areas for cosmetics, and a recognizable brush or applicator. '
    'Keep the application action clear at thumbnail size. Avoid realistic skin texture, individual lashes, '
    'detailed eyes and glossy beauty-ad shading. Do not reduce the subject to generic geometric symbols.'
)
GENERATION_CONSTRAINTS = ' '.join((VIEWPOINT_RULE, HAND_RULE, MAKEUP_RULE))
REUSE = set('''bakery-fresh-batch_outro
salon-transformation_before salon-transformation_space
salon-quick-tour_door salon-quick-tour_host salon-quick-tour_outro
cafe-first-visit_entrance cafe-first-visit_taste
cafe-morning-ritual_light cafe-morning-ritual_cup cafe-morning-ritual_pastry cafe-morning-ritual_corner
restaurant-date-night_entrance restaurant-date-night_dish restaurant-date-night_bite
bar-night-out_crowd bar-night-out_outro bar-tasting_first'''.split())


def save(data):
    temporary=ROOT/f'.manifest-{os.getpid()}.json'
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(ROOT/'manifest.json')


def normalize(source, stem):
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
        original_size = list(im.size)
        # Export normalization only; no scene drawing or creative image edits.
        im = ImageOps.fit(im, (1080, 1920), Image.Resampling.LANCZOS)
        im.save(ROOT / f'{stem}.png', optimize=True)
        im.save(ROOT / f'{stem}.jpg', quality=94, subsampling=0, optimize=True)
    return original_size


def prepare():
    if (ROOT / 'manifest.json').exists():
        raise SystemExit('Manifest already exists; resume it instead of overwriting.')
    catalog = json.loads((SCRIPTS / 'script_templates.json').read_text())
    plans = json.loads((SCRIPTS / 'shot_plan.json').read_text())
    old_prompts = (ROOT.parent.parent / 'script-image-prompts.md').read_text()
    old_by_stem = dict(re.findall(r'\*\*([^*]+)\.png\*\*[^\n]*\n\n(.*?)\n\nSize:', old_prompts, re.S))
    kinds = {k['id']: k['title'] for k in catalog['venueKinds']}
    entries = []
    for template in catalog['templates']:
        reasoning = next(p for p in SCRIPTS.glob(f'*/{template["id"]}.md'))
        reasoning_text = reasoning.read_text()
        for step in template['steps']:
            stem = Path(step['imageURL']).stem
            plan = plans[template['id']][step['id']]
            selfie = step['shot'] == 'selfie'
            pov = step['shot'] == 'pov'
            frame = {'wide': 'wide establishing shot with the whole room or facade visible',
                     'medium': 'medium shot showing the main subject and its surroundings',
                     'close': 'close shot with the main subject filling most of the frame',
                     'detail': 'detail shot of a clearly recognizable part of the main subject'}[plan['start']]
            viewpoint = ('Front-camera selfie view from the creator\'s outstretched arm; schematic creator looking into the lens, with venue behind. The phone itself is outside the picture.' if selfie else
                         'First-person view through the creator\'s eyes, with their hands at the lower edge when relevant; do not show a phone.' if pov else
                         'View through the camera lens; do not show the creator filming or a camera device.')
            prompt = (f'{STYLE}\n{GENERATION_CONSTRAINTS}\nUse case: illustration-story. Asset type: venue script step-card illustration. '
                      f'Venue: {kinds[template["venueKinds"][0]]}. Script: {template["title"]}. '
                      f'Script context: {template["summary"]}\n'
                      f'Subject: {step["title"]}. Position: {step["position"]}. '
                      f'Composition: {frame}; camera angle {plan["angle"]}. {viewpoint}\n'
                      f'Shot action to illustrate: {step["direction"]}\n'
                      'Show one readable still from this shot using its starting framing, with the named subject clearly visible. '
                      'Any camera motion describes filming instructions, not extra pictured cameras, arrows, or motion diagrams. '
                      'Single continuous full-bleed image, no panels or collage. One clear subject readable at 72 pixels high. '
                      'Match the established flat editorial illustrations: simplified matte shapes, restrained fine grain, soft shadows, no outlines; '
                      'warm ivory, charcoal, terracotta, natural muted skin tones. Only creator, consenting staff or friends when needed; no detailed bystander faces. '
                      'No text, lettering, numerals, prices, menus with writing, logos, watermark, interface, phone frame, captions, arrows or guidelines. '
                      'Where signs, receipts or labels are mentioned, show blank unmarked shapes. '
                      'Portrait canvas 1080 x 1920 pixels, exactly 9:16. '
                      'Input image is a STYLE REFERENCE ONLY: match its simplified editorial drawing, palette, restrained texture and schematic people; create the new scene described above, do not copy its oven, baker or layout.')
            entry = dict(stem=stem, template=template['id'], title=step['title'], shot=step['shot'],
                         plan=plan, imageURL=step['imageURL'], prompt=prompt,
                         reasoning=str(reasoning.relative_to(ROOT.parent)),
                         reasoning_sha256=hashlib.sha256(reasoning_text.encode()).hexdigest(),
                         status='pending', review='Not generated yet.')
            if stem in REUSE:
                entry.update(status='reused', source=str(OLD / step['imageURL']),
                             source_size=normalize(OLD / step['imageURL'], stem),
                             prompt=old_by_stem[stem],
                             review='Existing illustration reviewed for subject, framing and palette; retained and upscaled from 720 x 1280.')
            elif (OLD / step['imageURL']).exists():
                entry['replaces_existing'] = True
                entry['review'] = 'Existing preview needs replacement: updated angle/framing or single-view subject differs.'
            entries.append(entry)
    save(dict(version=1, generator='built-in image_gen', target_size=[1080, 1920],
              catalog_sha256=hashlib.sha256((SCRIPTS/'script_templates.json').read_bytes()).hexdigest(),
              entries=entries))
    report()


def write_reuse_map(manifest):
    entries = {e['stem']: e for e in manifest['entries']}
    mapping = {}
    groups = {}
    for stem, entry in entries.items():
        canonical = entry.get('reuse', {}).get('canonical_stem', stem)
        root = entries[canonical]
        mapping[stem] = dict(stepImageURL=entry['imageURL'], canonicalStem=canonical,
                             canonicalImageURL=root['imageURL'],
                             sourceKind='project' if Path(root['source']).parent.resolve()==OLD.resolve() else 'generated')
        groups.setdefault(canonical, []).append(stem)
    summary = dict(steps=len(entries), unique_illustrations=len(groups),
                   shared_step_aliases=sum(v['canonicalStem']!=k for k,v in mapping.items()),
                   unique_project_illustrations=sum(mapping[k]['sourceKind']=='project' for k in groups),
                   steps_using_project_art=sum(v['sourceKind']=='project' for v in mapping.values()))
    (ROOT/'reuse-map.json').write_text(json.dumps(dict(summary=summary, steps=mapping,
        shared_groups={k:v for k,v in groups.items() if len(v)>1}), indent=2)+'\n')
    catalog=json.loads((SCRIPTS/'script_templates.json').read_text())
    for template in catalog['templates']:
        for step in template['steps']:
            step['imageURL']=mapping[Path(step['imageURL']).stem]['canonicalImageURL']
    (ROOT/'shared_catalog.json').write_text(json.dumps(catalog, indent=2)+'\n')
    return summary


def report():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    entries = manifest['entries']
    reuse_summary = write_reuse_map(manifest)
    counts = {s: sum(e['status'] == s for e in entries) for s in sorted({e['status'] for e in entries})}
    prompts = ['# Step preview prompts', '', 'Generation: built-in image_gen. PNG masters and matching JPEG exports are 1080 x 1920.',
               'Retained and shared assets list their source image prompt; regenerated assets list the actual new prompt.', '',
               '## Mandatory constraints for future generation and reuse', '', VIEWPOINT_RULE, '', HAND_RULE, '', MAKEUP_RULE, '',
               'Historical prompts below document existing artwork; they are not exemptions from these constraints. '
               'Append all constraints and adapt any conflicting direction before regenerating. '
               'See viewpoint-audit.md for existing images flagged by the targeted review.', '']
    review = ['# Step preview review', '', f'Catalog: {len(entries)} steps. Status: {json.dumps(counts)}.', '',
              'Visitor-access constraint: '+VIEWPOINT_RULE,
              'Hand-count constraint: '+HAND_RULE,
              'Makeup style constraint: '+MAKEUP_RULE,
              'Earlier approval statuses predate this rule. See viewpoint-audit.md for flagged viewpoints; '
              'export validation does not certify visitor access.', '',
              'PNG masters follow the phase 02 brief. Matching .jpg exports preserve imageURL filenames without changing the catalog.',
              'Existing images are upscaled from 720 x 1280; generated originals are preserved at the source paths recorded in manifest.json.',
              'Export normalization uses Lanczos resizing and a centered fit to 9:16; scene generation uses the built-in image tool.', '',
              f'Reuse audit: {reuse_summary["unique_illustrations"]} unique illustrations for {len(entries)} steps; '
              f'{reuse_summary["shared_step_aliases"]} additional steps share a canonical image. '
              f'{reuse_summary["unique_project_illustrations"]} original project illustrations serve '
              f'{reuse_summary["steps_using_project_art"]} steps.',
              'reuse-map.json records canonical resources. shared_catalog.json applies those imageURL aliases for integration; '
              'the research catalog and all compatibility step filenames remain available.', '',
              '## Images requiring replacement', '']
    for e in entries:
        prompts += [f'## {e["stem"]}.png - {e["title"]}', '', f'Status: {e["status"]}. JPEG: `{e["imageURL"]}`.', '', e['prompt'], '']
        if e.get('reuse'):
            prompts += [f'Image source: `{e["reuse"]["canonical_stem"]}`. {e["reuse"]["reason"]}', '']
        if e.get('replaces_existing'):
            review.append(f'- `{e["stem"]}`: {e["status"]}. {e["review"]}')
    review += ['', '## Reused illustrations', '']
    for e in entries:
        if e.get('reuse'):
            review.append(f'- `{e["stem"]}` -> `{e["reuse"]["canonical_stem"]}`: {e["reuse"]["reason"]}')
    review += ['', 'Superseded exports and metadata are preserved under reuse-audit/superseded/.', '',
               '## Generated images redone after review', '']
    redone=[e for e in entries if e.get('attempts')]
    for e in redone:
        for attempt in e['attempts']:
            review.append(f'- `{e["stem"]}`: {attempt["review"]} Current status: {e["status"]}.')
    if not redone:review.append('None so far.')
    review += ['', '## Steps without a reviewed image', '']
    missing = [e for e in entries if e['status'] not in ('reused', 'approved')]
    review += [f'- `{e["stem"]}`: {e["status"]}. {e["review"]}' for e in missing] or ['None.']
    review += ['', '## Script strip review', '', 'Open index.html. Each row also has a saved contact strip under review-strips/.', '']
    groups = {}
    for e in entries:
        groups.setdefault(e['template'], []).append(e)
    (ROOT/'review-strips').mkdir(exist_ok=True)
    body = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Step previews review</title><style>body{margin:32px;background:#ece5d9;color:#292929;font:15px system-ui}section{margin:28px 0;border-top:1px solid #c8b9a7}h2{font-size:20px}.row{display:flex;gap:16px;overflow:auto;padding-bottom:16px}figure{margin:0;flex:0 0 135px}img,.missing{width:135px;height:240px;object-fit:cover;background:#d9cdbe;border-radius:8px}figcaption{font-size:11px;overflow-wrap:anywhere;margin-top:8px}.mini{height:72px;width:40.5px;border-radius:2px;margin-top:8px}.missing{display:grid;place-items:center}.status{font-weight:600}</style><h1>Step previews</h1>', f'<p>{len(entries)} steps. {html.escape(json.dumps(counts))}. Full card and 72 px strip sizes.</p>']
    body += [f'<p>{reuse_summary["unique_illustrations"]} unique illustrations; {reuse_summary["shared_step_aliases"]} shared step aliases. '
             '<a href="reuse-map.json">Reuse map</a> · <a href="shared_catalog.json">Catalog using shared resources</a></p>']
    body += ['<p><strong>Visitor-access review:</strong> Camera viewpoints must be accessible to ordinary visitors. '
             'Earlier approvals predate this requirement. '
             '<a href="viewpoint-audit.md">Existing viewpoints flagged for correction</a>.</p>']
    body += ['<p><strong>Hand-count rule:</strong> At most two visible hands total per image, '
             'including partial hands and hands across all people. Earlier approvals predate this requirement.</p>']
    for name, group in groups.items():
        strip = Image.new('RGB', (len(group)*160, 314), '#ece5d9')
        draw = ImageDraw.Draw(strip)
        body += [f'<section><h2>{html.escape(name)}</h2><div class="row">']
        for i,e in enumerate(group):
            path=ROOT/f'{e["stem"]}.png'
            if path.exists():
                with Image.open(path) as im:
                    strip.paste(ImageOps.fit(im.convert('RGB'), (135,240)), (i*160,0))
                    strip.paste(ImageOps.fit(im.convert('RGB'), (40,72)), (i*160+95,242))
                pic=f'<a href="{e["stem"]}.png"><img loading="lazy" src="{e["stem"]}.jpg" alt="{html.escape(e["title"])}"></a><img class="mini" loading="lazy" src="{e["stem"]}.jpg" alt="Strip size">'
            else:
                pic='<div class="missing">Pending</div>'
            draw.text((i*160,244),e['stem'].split('_',1)[1][:15],fill='#292929')
            shared = f'<br>Source: {html.escape(e["reuse"]["canonical_stem"])}' if e.get('reuse') else ''
            body += [f'<figure>{pic}<figcaption>{html.escape(e["title"])}<br><span class="status">{e["status"]}</span><br>{e["plan"]["angle"]}, {e["plan"]["start"]}{shared}</figcaption></figure>']
        strip.save(ROOT/'review-strips'/f'{name}.jpg',quality=90)
        body += ['</div></section>']
        ready=sum(e['status'] in ('approved','reused') for e in group)
        review.append(f'- `{name}`: {ready}/{len(group)} approved or retained.')
    (ROOT/'index.html').write_text('\n'.join(body)+'</html>\n')
    (ROOT/'prompts.md').write_text('\n'.join(prompts))
    (ROOT/'review.md').write_text('\n'.join(review)+'\n')
    print(json.dumps(counts))


def accept(stem, source, prompt=None):
    with (ROOT/'.manifest.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        _accept(stem,source,prompt)


def _accept(stem, source, prompt=None):
    manifest = json.loads((ROOT/'manifest.json').read_text())
    entry = next(e for e in manifest['entries'] if e['stem']==stem)
    if entry['status'] in ('reused', 'approved'):
        raise SystemExit('Refusing to overwrite an approved asset without an explicit redo.')
    entry.update(status='generated', source=source, source_size=normalize(source,stem),
                 review='Generated with built-in image_gen; awaiting script strip review.')
    if prompt:
        entry['prompt']=prompt
    save(manifest)


def approve(template):
    with (ROOT/'.manifest.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        _approve(template)


def _approve(template):
    manifest=json.loads((ROOT/'manifest.json').read_text())
    for entry in manifest['entries']:
        if entry['template']==template and entry['status']=='generated':
            entry.update(status='approved', review='Script strip visually inspected: subject and angle readable, consistent editorial palette, single camera view and no baked text.')
    save(manifest)


def validate():
    manifest=json.loads((ROOT/'manifest.json').read_text())
    catalog=json.loads((SCRIPTS/'script_templates.json').read_text())
    expected={Path(s['imageURL']).stem for t in catalog['templates'] for s in t['steps']}
    recorded={e['stem'] for e in manifest['entries']}
    errors=[]
    if expected!=recorded:errors.append('Manifest/catalog stems differ.')
    if len(recorded)!=len(manifest['entries']):errors.append('Duplicate manifest stems.')
    if hashlib.sha256((SCRIPTS/'script_templates.json').read_bytes()).hexdigest()!=manifest['catalog_sha256']:
        errors.append('Catalog changed after preview preparation.')
    prompts=(ROOT/'prompts.md').read_text()
    for entry in manifest['entries']:
        if entry['status'] not in ('approved','reused'):
            errors.append(f'Unreviewed image {entry["stem"]}: {entry["status"]}')
        if f'## {entry["stem"]}.png - ' not in prompts:
            errors.append(f'Missing documented prompt {entry["stem"]}')
        for suffix,fmt in [('png','PNG'),('jpg','JPEG')]:
            path=ROOT/f'{entry["stem"]}.{suffix}'
            if not path.exists():
                errors.append(f'Missing {path.name}')
                continue
            with Image.open(path) as im:
                if im.size!=(1080,1920) or im.format!=fmt:
                    errors.append(f'Invalid export {path.name}: {im.size}, {im.format}')
                im.verify()
            canonical=entry.get('reuse', {}).get('canonical_stem',entry['stem'])
            if canonical!=entry['stem']:
                canonical_path=ROOT/f'{canonical}.{suffix}'
                if hashlib.sha256(path.read_bytes()).digest()!=hashlib.sha256(canonical_path.read_bytes()).digest():
                    errors.append(f'Shared export differs from canonical: {path.name}')
    reuse=json.loads((ROOT/'reuse-map.json').read_text())
    shared=json.loads((ROOT/'shared_catalog.json').read_text())
    shared_steps=[s for t in shared['templates'] for s in t['steps']]
    if len(shared_steps)!=len(manifest['entries']):errors.append('Shared catalog step count differs.')
    for step in shared_steps:
        if not (ROOT/step['imageURL']).exists():errors.append(f'Missing shared resource: {step["imageURL"]}')
    (ROOT/'validation.json').write_text(json.dumps(dict(expected_steps=len(expected),
        scripts=len(catalog['templates']),
        reviewed_steps=sum(e['status'] in ('approved','reused') for e in manifest['entries']),
        reuse=reuse['summary'],
        png_count=len(list(ROOT.glob('*.png'))),jpg_count=len(list(ROOT.glob('*.jpg'))),
        errors=errors),indent=2)+'\n')
    print(f'{len(expected)} expected steps; {len(errors)} validation errors.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare','report','accept','approve','validate'])
    parser.add_argument('--stem');parser.add_argument('--source');parser.add_argument('--prompt-file')
    parser.add_argument('--template')
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='report':report()
    elif args.action=='approve':approve(args.template)
    elif args.action=='validate':validate()
    else:accept(args.stem,args.source,Path(args.prompt_file).read_text() if args.prompt_file else None)
