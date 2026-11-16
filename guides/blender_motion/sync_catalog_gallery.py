"""Point the existing all-guide gallery at the reviewed Blender artifacts."""
from pathlib import Path
import json
import re
import sys
import html

BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(BASE/'api'))
import opacity_assets
page=BASE/'catalog/animations.html'
text=page.read_text()
index=json.loads((BASE/'catalog/blender-animations/index.json').read_text())
shots={row['id']:('blender-animations/'+row['id'],row.get('base_shot_only',True)) for row in index['shots'] if row['exported'] and row['reviewed']}
if 'bar_low_truckr_mm' not in shots:shots['bar_low_truckr_mm']=('blender-study/bar_low_truckr_mm',False)
context_path=BASE/'catalog/context-animations/index.json'
contexts=json.loads(context_path.read_text()).get('guides',{}) if context_path.exists() else {}
context_manifest=json.loads(context_path.read_text()) if context_path.exists() else {'steps':{}}
people_count=len(json.loads((BASE/'guides/blender_motion/people-policy.json').read_text())['deferred_guides'])
step_count=sum(bool(r.get('folder')) for r in context_manifest['steps'].values())
handover_count=sum(r.get('handover_status')=='included' for r in context_manifest['steps'].values())
for gid,row in contexts.items():
    if gid in shots:
        shots[gid]=(str(Path(row['folder']).relative_to('catalog')),row['scope']=='base_shot')
# Restore earlier artwork for a native guide explicitly deferred by the user.
for match in list(re.finditer(r'<article class="guide" id="([^"]+)".*?</article>',text,re.S)):
    gid=match.group(1);card=match.group()
    if 'data-blender="true"' not in card or gid in shots:continue
    previous=BASE/'catalog/animations'/gid
    if not (previous/'guide_with_guides.png').exists():continue
    folder='animations/'+gid
    card=card.replace('data-blender="true"','data-blender="false"')
    card=re.sub(r'<span class="badge[^>]*>.*?</span>','<span class="badge">Previous artwork; people generation deferred</span>',card,count=1)
    card=re.sub(r'<img class="motion-image"[^>]*>',f'<img class="motion-image" loading="lazy" src="{folder}/poster_with_guides.png" data-poster="{folder}/poster_with_guides.png" data-animation="{folder}/guide_with_guides.png" alt="Previous guide: {gid}">',card,count=1)
    card=re.sub(r'<img class="fixed-sights"[^>]*>','',card)
    card=re.sub(r'<img class="strip"[^>]*>',f'<img class="strip" loading="lazy" src="{folder}/strip.png" alt="Previous samples">',card,count=1)
    card=re.sub(r'<p class="blender-scope">.*?</p>','',card)
    card=re.sub(r'<footer>.*?</footer>',f'<footer><a href="{folder}/guide_with_guides.png" download>Previous animation</a><a href="{folder}/guide.png" download>Artwork APNG</a></footer>',card,count=1)
    text=text.replace(match.group(),card,1)

for gid,(folder,base_only) in shots.items():
    pattern=r'<article class="guide" id="'+re.escape(gid)+r'".*?</article>'
    match=re.search(pattern,text,re.S)
    if not match:
        # A guide added after the library page was built has no card there yet.
        print('No library card yet:',gid);continue
    card=match.group()
    if gid=='bar_low_truckr_mm' and context_path.exists() and contexts.get(gid,{}).get('transition_method')=='one_camera_shared_interior':
        card=re.sub(r'<p class="description">.*?</p>',
                    '<p class="description">Low rightward slide along the bar, then lift and turn through the same seating area. Settle above the best two-person table, lean toward its place setting and hold. One continuous demonstration; no cut.</p>',card,count=1,flags=re.S)
    if gid=='bag_handoff_low_hold' and contexts.get(gid,{}).get('transition_method')=='same_order_match_cut':
        card=re.sub(r'<p class="description">.*?</p>',
                    '<p class="description">A hand carries one closed burger box from the serving ledge, sets it on a table and releases it. Match cut straight above the same box; one hand opens its attached lid to reveal the same whole burger resting inside.</p>',card,count=1,flags=re.S)
    card=re.sub(r'data-new="[^"]*"','data-new="true"',card,count=1)
    card=re.sub(r'data-stable="[^"]*"','data-stable="true"',card,count=1)
    card=re.sub(r'data-blender="[^"]*"','data-blender="true"',card,count=1)
    if 'data-blender=' not in card:card=card.replace('data-new=', 'data-blender="true" data-new=',1)
    context=contexts.get(gid)
    label=' / final shot' if context and context['scope']=='complete_final_shot' else ' / object shot' if base_only else ' / shot and handover'
    card=re.sub(r'<span class="badge[^>]*>.*?</span>','<span class="badge new">Blender / 25% fill'+label+'</span>',card,count=1)
    card=re.sub(r'<img class="motion-image"[^>]*>',f'<img class="motion-image" loading="lazy" src="{folder}/poster.png" data-poster="{folder}/poster.png" data-animation="{folder}/guide.png" alt="Animated guide: {gid}">',card,count=1)
    if 'class="fixed-sights"' not in card:
        card=card.replace('</div>\n<div class="motion-controls">','<img class="fixed-sights" src="../guides/shot-proof/cup_eye_orbitr_cc/viewfinder.png" alt=""></div>\n<div class="motion-controls">',1)
    card=re.sub(r'<img class="strip"[^>]*>',f'<img class="strip" loading="lazy" src="{folder}/strip.jpg" alt="Six animation samples">',card,count=1)
    note='Contextual handover pending.' if base_only else 'Final shot; holds for the script ending.' if next((r for r in index['shots'] if r['id']==gid),{}).get('handovers')=='not_applicable' else 'Includes the actual next-shot handover.'
    if context:
        note='Next people shot deferred.' if context['handover_status']=='deferred_people' else 'Final shot; hold for the ending.' if context['handover_status']=='not_applicable' else 'Continues into the actual next object shot.'
        if context['handover_status']=='cut_to_next_step':note='This shot ends at the cut; the next step has its own animation.'
        if context.get('transition_method')=='brief_right_whip':note='Milk pour followed by a brief entrance landing; no full Arrive replay.'
        footer=f'<a href="{folder}/guide.png" download>Transparent APNG</a><a href="context-animations/index.html#{context["template_id"]}.{context["step_id"]}">Script preview</a>'
    else:
        footer=f'<a href="{folder}/guide_with_guides.png" download>Animation with guides</a><a href="{folder}/guide.png" download>Artwork APNG</a>'
    card=re.sub(r'<footer>.*?</footer>',f'<p class="blender-scope">{note}</p><footer>{footer}</footer>',card,count=1)
    # Make updates idempotent.
    card=re.sub(r'(<p class="blender-scope">.*?</p>)\s*(<p class="blender-scope">)',r'\2',card,flags=re.S)
    text=text[:match.start()]+card+text[match.end():]
text=re.sub(r'<p><strong>\d+ (?:watercolor previews|Blender guides)</strong>.*?</p>',f'<p><strong>{len(shots)} Blender guides</strong> with 25% main fills are available in the local API. People generation is deferred; {people_count} guides retain their previous artwork. <a href="context-animations/index.html">{step_count} step guide animations and {handover_count} explicit transitions</a>.</p>',text,count=1,flags=re.S)
text=re.sub(r'<p>92 previews use.*?</p>','<p>Reusable native objects, fixed lighting and camera moves reviewed for a handheld phone. Viewfinder and horizon guides stay fixed. <a href="blender-regeneration-report.md">Current rollout report</a> · <a href="blender-animations/index.html">Native render gallery</a>.</p>',text,count=1,flags=re.S)
text=text.replace('href="regeneration-report.md"','href="blender-regeneration-report.md"')
if '<option value="blender">' not in text:
    text=text.replace('<option value="stable">','<option value="blender">Blender / 25% fill</option><option value="stable">',1)
text=text.replace('<option value="new">Watercolor previews</option>','<option value="new">Updated artwork</option>')
text=text.replace("const matches=style==='all'||", "const matches=style==='all'||(style==='blender'&&card.dataset.blender==='true')||") if "style==='blender'" not in text else text
if 'href="continuity-audit/report.md"' not in text:
    text=text.replace('</header>','<p><a href="continuity-audit/report.md">Continuity audit and repairs</a></p></header>',1)
revision=json.loads((BASE/'guides/blender_motion/cinematic-revision-status.json').read_text())
legacy=json.loads((BASE/'api/pre-blender-catalog.json').read_text())['guides']
for match in list(re.finditer(r'<article class="guide" id="([^"]+)".*?</article>',text,re.S)):
    gid=match.group(1);card=match.group()
    if gid in shots:master=BASE/'catalog'/shots[gid][0]/'guide.png'
    elif legacy[gid]['style']=='watercolor':master=BASE/'catalog/animations'/gid/'guide.png'
    else:master=BASE/'guides/overlays/schematic'/(gid+'.png')
    artifact=opacity_assets.assets(master);folder=str(Path(artifact['folder']).relative_to('catalog'))
    card=re.sub(r'<img class="motion-image"[^>]*>',f'<img class="motion-image" loading="lazy" src="{folder}/poster.png" data-poster="{folder}/poster.png" data-animation="{folder}/guide.png" alt="Animated guide: {gid}">',card,count=1)
    card=re.sub(r'<img class="strip"[^>]*>',f'<img class="strip" loading="lazy" src="{folder}/strip.jpg" alt="Animation frame samples">',card,count=1)
    card=re.sub(r'href="[^"]*/guide(?:_with_guides)?\.png"',f'href="{folder}/guide.png"',card)
    if gid not in shots:card=re.sub(r'<footer>.*?</footer>',f'<footer><a href="{folder}/guide.png" download>Transparent APNG</a></footer>',card,count=1,flags=re.S)
    if gid in revision['native_guides'] or gid in ['latte_top_in_cd_whipout','over_shoulder_counter_os_hold','cup_eye_hold_whipout','room_lights_eye_hold']:
        spec=json.loads((BASE/'catalog/blender-animations'/gid/'scene-spec.json').read_text())
        card=re.sub(r'<p class="description">.*?</p>','<p class="description">'+html.escape(spec['intent'])+'</p>',card,count=1,flags=re.S)
    text=text.replace(match.group(),card,1)
text=text.replace('25% main fills','65% whole-overlay opacity').replace('25% fill','65% overlay').replace('35%','65%').replace('50%','65%')
from gallery_ui import attach
text=attach(text,"guide-ui.js")
sys.path.insert(0,str(BASE/'catalog'))
from sync_clay_gallery import apply as clay_gallery
text=clay_gallery(text)
page.write_text(text)
print('Main gallery updated:',len(shots),'Blender guides')
