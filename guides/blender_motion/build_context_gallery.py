"""Review actual per-script object handovers without generating or showing new people."""
from pathlib import Path
import html
import json
import sys
import os
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'catalog/context-animations'
sys.path.insert(0,str(BASE/'api'))
import opacity_assets
manifest=json.loads((OUT/'index.json').read_text());templates=json.loads((BASE/'guides/script_templates.json').read_text())['templates']
sections=[];count=0;handovers=0
for template in templates:
    cards=[];deferred=[]
    for original_step in template['steps']:
        step=dict(original_step)
        if step['overlays'][0]=='cup_eye_hold_whipout':step['direction']='Start on the steaming cup, then rise diagonally to reveal the plated croissant beside it on the same table.'
        if template['id']=='cafe-morning-ritual' and step['id']=='pastry':step['direction']='Continue toward the opened croissant and its filling from the same shared table view. Keep the pastry supported; do not mime a tear.'
        if step['overlays'][0]=='over_shoulder_counter_os_hold':step['direction']='Hold the phone on the customer side with the menu above and cup below. Film the espresso flowing into the supported cup.'
        key=template['id']+'.'+step['id'];row=manifest['steps'][key]
        if not row.get('folder'):deferred.append(step['title']);continue
        count+=1;handovers+=row['handover_status']=='included'
        opacity=opacity_assets.assets(BASE/row['folder']/'guide.png')
        relative=os.path.relpath(BASE/opacity['folder'],OUT);primary=row['source']['frames']/15
        note='Next people shot deferred.' if row['handover_status']=='deferred_people' else 'Final shot; hold for the ending.' if row['handover_status']=='not_applicable' else 'Continues into the actual next object shot: '+row['next_guide']+'.'
        if row['handover_status']=='cut_to_next_step':note='This step ends at the cut. Play the next step separately; its whole shot is not repeated here.'
        if row.get('transition_method')=='brief_right_whip':note='Brief right-whip landing only. The complete entrance shot belongs to the next step.'
        if row.get('transition_method')=='one_camera_shared_interior':
            note='One continuous room: along the bar, lift and turn through the seating area, then settle above the same best table. The following step continues the table shot.'
        if row.get('transition_method')=='same_order_match_cut':
            note='The same burger box is carried down, set on the table and released. Match cut overhead to open its attached lid. The next step reuses these exact box and burger frames.'
        if row.get('transition_method')=='one_camera_shared_scene':note='One continuous camera move connects the resources in the same physical scene. The next step reuses its landing frames.'
        cards.append(f'''<article id="{html.escape(key)}" data-guide-id="{row['guide_id']}" data-search="{html.escape((template['title']+' '+step['title']+' '+row['guide_id']).lower())}"><h3>{html.escape(step['title'])}</h3><p class="meta">{html.escape(row['guide_id'])} · {primary:g} s primary shot · {row['duration']:g} s demonstration</p><div class="stage"><img class="motion" loading="lazy" src="{relative}/poster.png" data-poster="{relative}/poster.png" data-animation="{relative}/guide.png" alt="{html.escape(step['direction'])}"><img class="sights" src="../blender-animations/cup_eye_orbitr_cc/viewfinder.png" alt=""></div><button data-play>Play / replay</button><button data-pause>Starting pose</button><p>{html.escape(step['direction'])}</p><p class="meta">{html.escape(note)}</p><a href="{relative}/guide.png" download>Transparent APNG</a> · <a href="{relative}/strip.jpg">Frame samples</a></article>''')
    note='<p class="deferred">People steps deferred: '+html.escape(', '.join(deferred))+'. Full-script playback awaits those scenes.</p>' if deferred else ''
    sequence=manifest['scripts'][template['id']]
    if sequence.get('folder'):
        opacity=opacity_assets.assets(BASE/sequence['folder']/'guide.png',video=True)
        folder=os.path.relpath(BASE/opacity['folder'],OUT)
        note+=f'<p>Complete object-only sequence · {sequence["duration"]:g} seconds · <a href="{folder}/guide.png">Transparent animated sequence</a> · <a href="{folder}/preview.mp4">Play MP4</a></p><video controls playsinline preload="none" poster="{folder}/poster.png" style="display:block;width:min(100%,270px);background:#23343e"><source src="{folder}/preview.mp4" type="video/mp4"></video>'
    sections.append('<section><h2>'+html.escape(template['title'])+'</h2>'+note+'<div class="grid">'+''.join(cards)+'</div></section>')
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Script object handovers</title><style>*{box-sizing:border-box}body{margin:0;background:#eeece6;color:#293d49;font:14px/1.6 system-ui,sans-serif}main{max-width:1400px;margin:auto;padding:24px}h1{font-size:30px}h2{font-size:23px;margin-top:40px}h3{margin:0;font-size:17px}a{color:#326881}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:18px}article{background:#faf9f4;padding:15px;border:1px solid #cad3d5;border-radius:8px}.stage{aspect-ratio:9/16;position:relative;background:#f7f5ef;margin:12px 0}.stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.sights{pointer-events:none}.dark .stage{background:#23343e}.meta,.deferred{font-size:12px;color:#607783}button,input{font:inherit;padding:7px 10px;border:1px solid #a8b8c0;background:white;border-radius:5px;margin:3px;cursor:pointer}input{min-width:260px;cursor:text}nav{position:sticky;top:0;background:#eeece6;padding:10px;z-index:2;border-bottom:1px solid #cad3d5}[hidden]{display:none!important}</style><main><a href="../animations.html">All guide animations</a><h1>Actual script handovers</h1>'''
page+=f'<p>{count} object/hand step guide animations, including {handovers} transitions into the next object shot. Whole-overlay opacity is 65%; backgrounds remain fainter. Viewfinder and level references are separate UI; live sensor readings appear in the camera app. No new faces, heads or full-body figures appear here.</p><p>The demonstration shows the primary shot and the next object action. It can be longer than the recommended capture time for one step.</p><nav><input id="search" placeholder="Find a script, step or guide" aria-label="Search"><button id="background">Light / dark background</button></nav>'
page+=''.join(sections)+'''</main><script>function play(card){const image=card.querySelector('.motion');image.src=image.dataset.animation+'?play='+Date.now()}function pause(card){const image=card.querySelector('.motion');image.src=image.dataset.poster}const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;const observer=new IntersectionObserver(items=>items.forEach(item=>{if(item.isIntersecting&&!reduced)play(item.target);else pause(item.target)}),{threshold:.15});document.querySelectorAll('article').forEach(card=>{observer.observe(card);card.querySelector('[data-play]').onclick=()=>play(card);card.querySelector('[data-pause]').onclick=()=>pause(card)});document.getElementById('background').onclick=()=>document.body.classList.toggle('dark');document.getElementById('search').oninput=event=>{const query=event.target.value.toLowerCase();document.querySelectorAll('article').forEach(card=>card.hidden=!card.dataset.search.includes(query));document.querySelectorAll('section').forEach(section=>section.hidden=!section.querySelector('article:not([hidden])'))};if(location.hash){const card=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(card){card.scrollIntoView();play(card)}};</script></html>'''
from gallery_ui import attach
page=attach(page,"../guide-ui.js")
sys.path.insert(0,str(BASE/'catalog'))
from sync_clay_gallery import apply_context
page=apply_context(page)
(OUT/'index.html').write_text(page);print('Context gallery:',count,'steps,',handovers,'object handovers')
