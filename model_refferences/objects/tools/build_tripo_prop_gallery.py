"""Build a review gallery for completed prop batches, without publishing guides."""
import hashlib
import html
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tripo_batch_gallery import page, relative

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT.parent / 'tripo-cli'


def build():
    cards = []
    records = []
    verified = []
    for aid in ['latte_cup', 'kettle', 'dining_table', 'kitchen_tongs', 'glazed_door', 'window', 'menu_board',
                'croissant_oozing', 'display_case', 'bar_counter', 'bar_stool', 'bottle', 'drinking_glass',
                'croissant', 'espresso_machine', 'milk_pitcher', 'coffee_grinder', 'portafilter',
                'takeaway_cup', 'serving_tray', 'pastry_box', 'pastry_rack',
                'wall_shelf', 'pendant', 'coffee_tamper', 'knock_box', 'laptop']:
        review = ROOT / aid / 'tripo-generated/review'
        if not (review / 'metadata.json').exists():
            continue
        data = json.loads((review / 'metadata.json').read_text())
        source = Path(data['source'])
        assert hashlib.sha256(source.read_bytes()).hexdigest() == data['source_sha256']
        views = ['preview', 'front', 'back', 'left', 'right', 'top', 'bottom']
        for mode in ['rendered', 'shape']:
            for view in views:
                path = review / mode / (view + '.png')
                with Image.open(path) as im:
                    im.verify()
                verified.append(str(path.relative_to(ROOT.parent)))
        title = aid.replace('_', ' ').title()
        design = ROOT / aid / 'design'
        ref = design / ('three-quarter.png' if aid == 'latte_cup' else 'front.png')
        if aid in ['espresso_machine', 'milk_pitcher', 'coffee_grinder', 'portafilter', 'takeaway_cup', 'pastry_box', 'coffee_tamper', 'knock_box']:
            design = ROOT / aid / 'design-ordering'
            ref = design / 'three-quarter.png'
        elif aid == 'croissant':
            design = ROOT / aid / 'design-review-v2'
            ref = design / 'whole-isolated.png'
        elif aid in ['pastry_rack', 'wall_shelf']:
            ref = design / 'reconstruction-v2.png'
        assert ref.exists(), ref
        reference_views = {v: relative(design / (v + '.png'), review)
                           if (design / (v + '.png')).exists() else relative(ref, review) for v in views}
        options = ''.join(f'<option value="{v}">{v.title()}</option>' for v in views)
        revision = str((review / 'rendered/preview.png').stat().st_mtime_ns)
        sheet = Image.new('RGB', (1200, 850), '#f6f1e6')
        draw = ImageDraw.Draw(sheet)
        for i, view in enumerate(views[1:]):
            im = Image.open(review / 'rendered' / (view + '.png')).convert('RGBA')
            im.thumbnail((390, 390))
            cell = Image.new('RGBA', (400, 390), '#f6f1e6')
            cell.alpha_composite(im, ((400 - im.width) // 2, (390 - im.height) // 2))
            sheet.paste(cell.convert('RGB'), (i % 3 * 400, i // 3 * 425 + 25))
            draw.text((i % 3 * 400 + 10, i // 3 * 425 + 5), view.upper(), fill='#354b3c')
        sheet.save(review / 'projections.jpg', quality=94)
        body = f'''<p><a href="{relative(INDEX / 'props.html', review)}">All prop models</a></p>
<h1>{title}</h1><p>Original Tripo geometry and textures, with a local placement transform.
The downloaded GLB remains unchanged. This is a review candidate; it has not replaced a live guide.</p>
<p><a href="model.blend">Packed Blender model</a> · <a href="asset.blend">Appendable asset</a> ·
<a href="{relative(source, review)}">Original GLB</a> · <a href="metadata.json">Measurements</a></p>
<nav><label for="view">View</label><select id="view">{options}</select><button id="material">Show shape only</button></nav>
<div class="pair"><article><h2>Design reference</h2><div class="stage"><img id="reference" src="{relative(ref, review)}" alt="Design reference"></div></article>
<article><h2>Actual Blender render</h2><div class="stage"><img id="model" src="rendered/preview.png?v={revision}" alt="{title}"></div></article></div>
<section><p>{data['triangles']:,} triangles · {data['mesh_parts']} mesh parts · {data['credits_consumed']:g} API credits.</p>
<p>Actual-vertex ground placement: {data['lowest_vertex_z']:.7f} m. Placement and articulation still need scene testing.</p>
<p>{html.escape(' '.join(data['limitations']))}</p></section>
<section><h2>Six model projections</h2><img src="projections.jpg?v={revision}" alt="Six actual Blender projections"></section>'''
        script = f'''<script>const refs={json.dumps(reference_views)},v=document.querySelector('#view');let shape=false;
function update(){{document.querySelector('#reference').src=refs[v.value];document.querySelector('#model').src=(shape?'shape/':'rendered/')+v.value+'.png?v={revision}';document.querySelector('#material').textContent=shape?'Show original materials':'Show shape only'}}
v.onchange=update;document.querySelector('#material').onclick=()=>{{shape=!shape;update()}};</script>'''
        (review / 'index.html').write_text(page(title, body, script))
        link = relative(review, INDEX)
        cards.append(f'<article><h2><a href="{link}/index.html">{title}</a></h2><div class="pair"><a href="{link}/index.html"><img src="{link}/rendered/preview.png?v={revision}" alt="{title}"></a><div><p>{data["triangles"]:,} triangles · {data["credits_consumed"]:g} credits.</p><p><a href="{link}/index.html">Compare reference and six projections</a></p><p><a href="{link}/model.blend">Blender file</a> · <a href="{relative(source, INDEX)}">Original GLB</a></p><p>Review candidate; no live guide replacement.</p></div></div></article>')
        records.append(dict(id=aid, task_id=data['task_id'], credits_consumed=data['credits_consumed'],
                            review=relative(review, INDEX), source_sha256=data['source_sha256'],
                            triangles=data['triangles'], status='review_candidate'))
        derived = review.parent / 'scene-ready'
        if (derived / 'metadata.json').exists():
            corrected = json.loads((derived / 'metadata.json').read_text())
            images = [p for name in ['preview.png', 'closed.png', 'open.png', 'glazing.png']
                      if (p := derived / name).exists()]
            figures = ''.join(f'<article><img src="{p.name}?v={p.stat().st_mtime_ns}" alt="Locally corrected {title}"></article>' for p in images)
            notes = ' '.join(corrected.get('changes', []))
            rejected = (review.parent / 'owner-review.json').exists()
            status = 'Excluded: reference correction pending' if rejected else 'Local scene-ready correction'
            derived_body = f'<p><a href="{relative(INDEX / "props.html", derived)}">Model library</a></p><h1>{title} / {status}</h1><p>{html.escape(notes)}</p><p>Original GLB preserved. Local processing used no additional API credits.</p><p><a href="model.blend">Blender review</a> · <a href="asset.blend">Appendable asset</a> · <a href="metadata.json">Correction details</a> · <a href="../review/index.html">Original model and reference views</a></p>{figures}'
            (derived / 'index.html').write_text(page(title + ' / local correction', derived_body))
            navigation = f'<section><h2><a href="../scene-ready/index.html">{status}</a></h2><p>{html.escape(notes)}</p></section>'
            file = review / 'index.html'
            file.write_text(file.read_text().replace('<main>', '<main>' + navigation, 1))
            cards[-1] = cards[-1].replace('</h2>', f'</h2><p><a href="{relative(derived, INDEX)}/index.html">{status}</a></p>', 1)
            if images and not rejected:
                primary = relative(images[0], INDEX)
                cards[-1] = cards[-1].replace(f'{link}/rendered/preview.png?v={revision}', primary + '?v=' + str(images[0].stat().st_mtime_ns))
            if rejected:
                cards[-1] = '<article><h2>Broken croissant / approved shape derivative</h2><p>The earlier model is excluded. The replacement consists of two halves derived locally from the approved whole croissant.</p><a href="../objects/croissant_oozing/approved-v2/preview.png"><img src="../objects/croissant_oozing/approved-v2/preview.png" alt="Two halves from the approved croissant"></a><p><a href="../objects/croissant_oozing/approved-v2/model.blend">Replacement Blender model</a> · <a href="../objects/croissant/design-review-v2/index.html">Approved reference</a></p></article>'
                records[-1]['status'] = 'excluded_replaced_by_local_approved_derivative'
        for variant, label in [('functional', 'Functional coffee asset'), ('full-height', 'Full-height window'),
                               ('approved-v2', 'Approved clay shape')]:
            folder = ROOT / aid / variant
            if not (folder / 'metadata.json').exists():
                continue
            picture = folder / 'preview.png'
            with Image.open(picture) as im:
                im.verify()
            href = relative(folder, INDEX)
            cards[-1] = cards[-1].replace('</article>', f'<p><a href="{href}/model.blend">{label} / Blender</a> · <a href="{href}/preview.png">Preview</a> · <a href="{href}/metadata.json">Measurements</a></p></article>')
    credits = sum(r['credits_consumed'] for r in records)
    cast = ''.join(f'<article><h2>{aid.replace("_", " ").title()} / rigged</h2><a href="../{aid}/tripo-rigged/review/model.blend"><img src="../{aid}/tripo-rigged/review/elbow-proof.png" alt="Rigged {aid}"></a><p><a href="../{aid}/tripo-rigged/review/model.blend">Blender deformation proof</a> · <a href="../{aid}/tripo-rigged/review/metadata.json">65-bone rig details</a></p><p>Body rig ready. Scene-specific finger contact and facial controls still require preparation.</p></article>' for aid in ['creator', 'barista', 'friend_locs'])
    body = f'<h1>Reusable Tripo props</h1><p>{len(records)} generated props · {credits:g} actual generation credits. Existing artwork and downloaded GLBs are preserved.</p><p><a href="index.html">Characters and chair</a> · <a href="README.md">Current balance and progress</a> · <a href="priority-plan.md">Venue packs and visit flow</a></p>' + ''.join(cards) + cast
    (INDEX / 'props.html').write_text(page('Loca reusable Tripo props', body))
    (INDEX / 'props-generation-report.json').write_text(json.dumps(dict(models=records, actual_credits=credits,
        verified_render_images=len(verified), source_files_unmodified=True, api_guides_replaced=False), indent=2) + '\n')
    index = INDEX / 'index.html'
    existing = index.read_text()
    if 'id="props-link"' not in existing:
        existing = existing.replace('<main>', '<main><section id="props-link"><h2><a href="props.html">New reusable prop models</a></h2><p><a href="priority-plan.md">Shared layout and venue packs</a> · <a href="credits-estimate.md">Credits estimate</a></p></section>', 1)
        index.write_text(existing)
    print(json.dumps(dict(models=len(records), credits=credits, render_images=len(verified))))


if __name__ == '__main__':
    build()
