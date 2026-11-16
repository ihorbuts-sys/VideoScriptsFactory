"""Write a reviewable batch index and an inventory of the remaining guides."""
import html
import json
import re
from pathlib import Path

BASE=Path(__file__).resolve().parents[3]
ROOT=BASE/'catalog/glass-rollout/coffee'
CATALOG=Path('/Users/ihor.buts/Documents/Development/Scriptwriter/catalog/catalog.json')


def run():
    catalog=json.loads(CATALOG.read_text())
    cards=[];scenes=[];planned={'cup_shot_eye_in_cd_through'};credits=0
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or not (folder/'scene-spec.json').exists():continue
        spec=json.loads((folder/'scene-spec.json').read_text());planned.add(spec['guide'])
        review=folder/'review-status.json'
        if review.exists() and json.loads(review.read_text()).get('status')=='rejected':continue
        credits+=spec.get('generation_credits_used',0)
        planned.update(b['guide'] for b in spec.get('guide_bindings',[]))
        if folder.name=='morning-pair':planned.add('pastry_tear_open')
        published=(folder/'publication.json').exists()
        checked=(folder/'composite-browser-check.json').exists()
        status='Published' if published else 'Playback checked' if checked else 'Exporting' if (folder/'render-ready.json').exists() else 'Rendering'
        template=next(t for t in catalog['templates'] if t['id']==spec['template'])
        step=next(s for s in template['steps'] if s['id']==spec['step'])
        label=html.escape(spec['title']);slug=folder.name
        image='color-strip.jpg' if (folder/'color-strip.jpg').exists() else 'probes-color/frame_0001.png'
        link=f'<a href="{slug}/index.html">Play color and glass guide</a>' if checked else 'Preview becomes playable after verification.'
        cards.append(f'<article><h2>{label}</h2><p class="status">{status}</p><p>{html.escape(template["title"])} → {html.escape(step["title"])}</p><img src="{slug}/{image}" alt="{label}" loading="lazy"><p>{link}</p><p>{html.escape(spec["direction"])}</p></article>')
        scenes.append(dict(id=slug,status=status,template=spec['template'],step=spec['step'],guide=spec['guide'],seconds=spec['duration_s']))
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / coffee glass guides</title><style>body{font:16px/1.5 system-ui;background:#f2ede3;color:#293b32;max-width:1100px;margin:auto;padding:24px}a{color:#326c52}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}article{padding:20px;background:#fffaf0;border-radius:20px}h1{line-height:1.2}h2{font-size:20px}.status{font-weight:600;color:#326c52}img{width:100%;max-height:320px;object-fit:contain;border-radius:12px}</style><p><a href="../../animations.html">All guides</a> · <a href="../../coffee-hologram-study/index.html">Approved glass study</a></p><h1>Coffee / glass guide rollout</h1><p>Object-only guides from the approved café scene. Fixed light, public phone positions, full-strength subjects at 100% view opacity, and separate viewfinder UI. Use Animation style in the iOS camera.</p><p><a href="index.json">Batch status</a> · <a href="../rollout.json">Full guide inventory</a></p><div class="grid">'''+''.join(cards)+'</div></html>'
    (ROOT/'index.html').write_text(text)
    (ROOT/'index.json').write_text(json.dumps(dict(scenes=scenes),indent=2)+'\n')
    done={gid for gid,g in catalog['guides'].items() if g.get('imageViewOpacity')==.65 and g.get('alphaFactor')==1}
    contextual={gid for rows in catalog.get('stepGuideOverrides',{}).values() for gid,g in rows.items() if g.get('imageViewOpacity')==.65 and g.get('alphaFactor')==1}
    inventory=[]
    for gid,guide in sorted(catalog['guides'].items()):
        contexts=[dict(template=t['id'],step=s['id']) for t in catalog['templates'] for s in t['steps'] if gid in s.get('overlays',[])]
        status='published' if gid in done|contextual else 'first-coffee-batch' if gid in planned else 'queued'
        inventory.append(dict(guide=gid,status=status,contexts=contexts))
    report=dict(approved_style='glass-full-surfaces-v3',total_guides=len(inventory),
        glass_guides_published=len(done|contextual),planned_coffee_guides=len(planned),
        image_view_opacity=.65,baked_global_opacity=1,scene_bloom=False,architecture_in_ghost=False,
        no_new_generation_credits_used=credits==0,generation_credits_used=credits,guides=inventory)
    (ROOT.parent/'rollout.json').write_text(json.dumps(report,indent=2)+'\n')
    # Refresh the existing gallery too, so its cards cannot keep playing older
    # assets after a template/API binding has been updated.
    gallery=BASE/'catalog/animations.html'
    text=gallery.read_text()
    current=f'<p><strong>{len(done|contextual)} of {len(inventory)} guides</strong> use the approved object-only glass treatment with 65% image-view opacity. The other guides retain their previous native artwork. Creator performances are available; remaining character actions are listed in the report. <a href="glass-rollout/report.md">Current report and verification</a>.</p>'
    text=re.sub(r'<p><strong>(?:178 Blender guides|\d+ of \d+ guides)</strong>.*?</p>',lambda match:current,text,count=1,flags=re.S)
    text=re.sub(r'<p id="cinematic-progress">.*?</p>',
        '<p id="cinematic-progress">The new glass images use full-strength surfaces and one 65% image-view multiplier. Older images retain their baked opacity. <a href="glass-rollout/coffee/index.html">Play the current coffee guides</a>.</p>',text,count=1,flags=re.S)
    manifest=json.loads((BASE/'catalog/clay-scenes/active-revisions.json').read_text())
    for folder in ROOT.iterdir():
        review=folder/'review-status.json'
        if not review.exists() or json.loads(review.read_text()).get('status')!='rejected':continue
        spec=json.loads((folder/'scene-spec.json').read_text())
        for binding in spec.get('guide_bindings',[]):
            gid=binding['guide']
            if manifest['guides'].get(gid,{}).get('opacity_mode')=='image_view':continue
            article=f'<article class="guide" id="{html.escape(gid)}" data-search="{html.escape(gid)}"><h2>{html.escape(gid)}</h2><p>The new hand-interaction study was withdrawn after owner review. Its grip looked unnatural. The earlier API guide is retained while a replacement is pending.</p></article>'
            text=re.sub(r'<article class="guide" id="'+re.escape(gid)+r'".*?</article>',lambda match:article,text,count=1,flags=re.S)
    if not (ROOT.parent/'sequences/bakery-box/publication.json').exists():
        text=re.sub(r'<p id="bakery-glass-sequence">.*?</p>','',text,flags=re.S)
    for gid,row in manifest['guides'].items():
        if row.get('opacity_mode')!='image_view':continue
        folder=BASE/row['folder']
        spec=json.loads((folder/'scene-spec.json').read_text())
        relative=str(folder.relative_to(BASE/'catalog'))
        preview=spec['source_scene'].removeprefix('catalog/')+'/index.html'
        description=html.escape(row['direction'])
        guide=html.escape(gid)
        variant_links=[]
        for variant in manifest.get('guide_variants',{}).values():
            if variant['guide_id']!=gid:continue
            variant_spec=json.loads((BASE/variant['folder']/'scene-spec.json').read_text())
            target=variant_spec['source_scene'].removeprefix('catalog/')+'/index.html'
            for context in variant['contexts']:
                template=next(t for t in catalog['templates'] if t['id']==context['template'])
                step=next(s for s in template['steps'] if s['id']==context['step'])
                variant_links.append(f'<a href="{html.escape(target)}">{html.escape(template["title"])} / {html.escape(step["title"])}</a>')
        variants='<p class="context-variants">Step-specific versions: '+' · '.join(variant_links)+'</p>' if variant_links else ''
        article=f'''<article class="guide" id="{guide}" data-blender="true" data-new="true" data-stable="true" data-search="{guide} {description}"><h2>{guide}</h2><span class="badge new">Glass / image-view opacity / native 3D</span>
<div class="motion-card" data-guide="{guide}"><div class="motion-stage"><img class="motion-image" style="opacity:.65" loading="lazy" src="{relative}/view-overlay-poster.png" data-poster="{relative}/view-overlay-poster.png" data-animation="{relative}/view-overlay.png" alt="Animated guide: {guide}"></div><div class="motion-controls"><button type="button" data-play>Play / replay</button><button type="button" data-pause>Starting pose</button></div></div>
<p class="description">{description}</p><img class="strip" loading="lazy" src="{relative}/view-overlay-strip.jpg" alt="Animation frame samples"><p class="blender-scope">{spec['duration_s']:.2f} seconds. Object-only glass with 65% image-view opacity. Viewfinder and level remain separate.</p>{variants}<footer><a href="{relative}/view-overlay.png" download>Transparent APNG</a><a href="{preview}">Color and glass preview</a></footer></article>'''
        pattern=r'<article class="guide" id="'+re.escape(gid)+r'".*?</article>'
        text=re.sub(pattern,lambda match:article,text,count=1,flags=re.S)
    marker='<p id="coffee-hologram-study">'
    if 'id="coffee-glass-rollout"' not in text:
        text=text.replace(marker,'<p id="coffee-glass-rollout"><strong>Coffee rollout:</strong> <a href="glass-rollout/coffee/index.html">Play the new guide batch and check publication status</a>.</p>'+marker,1)
    sequence=ROOT.parent/'sequences/cafe-morning-ritual'
    if (sequence/'composite-browser-check.json').exists():
        link='<p id="morning-glass-sequence"><strong>Morning ritual:</strong> <a href="glass-rollout/sequences/cafe-morning-ritual/index.html">Play all four shots in the new glass style</a>.</p>'
        if 'id="morning-glass-sequence"' not in text:text=text.replace('<p id="coffee-glass-rollout">',link+'<p id="coffee-glass-rollout">',1)
        index=(ROOT/'index.html').read_text().replace('<div class="grid">','<p><a href="../sequences/cafe-morning-ritual/index.html">Play the complete Morning ritual sequence</a></p><div class="grid">',1)
        (ROOT/'index.html').write_text(index)
    if (ROOT.parent/'sequences/bakery-box/publication.json').exists():
        link='<p id="bakery-glass-sequence"><strong>Build a box:</strong> <a href="glass-rollout/sequences/bakery-box/index.html">Play all five shots, including the continuous packing reveal</a>.</p>'
        if 'id="bakery-glass-sequence"' not in text:text=text.replace('<p id="coffee-glass-rollout">',link+'<p id="coffee-glass-rollout">',1)
        index=(ROOT/'index.html').read_text().replace('<div class="grid">','<p><a href="../sequences/bakery-box/index.html">Play the complete Build a box sequence</a></p><div class="grid">',1)
        (ROOT/'index.html').write_text(index)
    gallery.write_text(text)


if __name__=='__main__':run()
