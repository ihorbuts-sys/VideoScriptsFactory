"""Publish the supported-object Line Art batch, with light browser previews."""
import argparse
import html
import json
from pathlib import Path

from PIL import Image
from pack_full_frame_apng import pack

CLIPS=[
    ('cup-steady','Cup on saucer / steady 45°','A gentle 90° arc at a constant downward angle.'),
    ('cup-cinematic','Cup on saucer / changing angles','The same arc, with continuous 45° → 37° → 53° → 45° changes.'),
    ('coffee-pastry','Coffee and pastry / rising diagonal','One tray throughout: arc right while rising from 35° to 60°.'),
    ('dessert','Cake on plate / descending arc','Arc left while lowering from 55° to 35°, exposing the layers.'),
]


def package(folder):
    meta=json.loads((folder/'meta.json').read_text())
    assert json.loads((folder/'scene-checks.json').read_text())['status']=='passed'
    count=meta['frame_count'];small=folder/'browser';small.mkdir(exist_ok=True)
    for number in range(1,count+1):
        name=f'frame_{number:04d}.png'
        with Image.open(folder/name) as source:
            source.resize((540,960),Image.Resampling.LANCZOS).save(small/name)
    pack(folder,folder/'animation.png',count,30,plays=1)
    pack(small,small/'animation.png',count,30,plays=1)
    for directory in [folder,small]:
        with Image.open(directory/'animation.png') as apng:
            assert apng.n_frames==count and apng.info['loop']==1
            for frame in range(count):
                apng.seek(frame)
                with Image.open(directory/f'frame_{frame+1:04d}.png') as original:
                    assert apng.convert('RGBA').tobytes()==original.convert('RGBA').tobytes()
    report=dict(status='passed',frames=count,plays=1,full_resolution=[1080,1920],browser_resolution=[540,960],
        all_decoded_apng_frames_match_corresponding_png=True,opacity_not_baked=True)
    (folder/'packaging-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    return meta,report


def run(root):
    clips={};cards=[];reports={}
    for key,title,description in CLIPS:
        meta,reports[key]=package(root/key)
        clips[key]=dict(count=meta['frame_count'],fps=30,frames=[dict(pitch=f['pitch_degrees'],yaw=f['azimuth_degrees']) for f in meta['frames']])
        direction=('Sit beside the cup. Keep the cup on its saucer and the phone at a 45° downward angle. Trace a short arc at the same height without changing the lens.'
                   if key=='cup-steady' else meta['assembly']['direction'])
        cards.append(f'''<article id="{key}" data-key="{key}"><h2>{html.escape(title)}</h2><p class="description">{html.escape(description)}</p>
<div class="stage"><img id="{key}-image" src="{key}/browser/frame_0001.png" alt="{html.escape(title)}"></div>
<p id="{key}-pose" class="pose"></p><div class="controls"><button data-play="{key}">Play / replay</button><button data-start="{key}">Starting pose</button></div>
<p>{html.escape(direction)}</p><p><a href="{key}/animation.png">Full-size animation</a> · <a href="{key}/scene.blend">Blender scene</a> · <a href="{key}/scene-checks.json">Checks</a></p></article>''')
        print('PACKAGED',key,flush=True)
    inventory=json.loads((root/'available-models.json').read_text());groups={}
    for obj in inventory['objects']:groups.setdefault(obj['category'],[]).append(obj['id'].replace('_',' '))
    models='<table><thead><tr><th>Category</th><th>Existing models</th></tr></thead><tbody>'+''.join('<tr><td>'+html.escape(k)+'</td><td>'+html.escape(', '.join(v))+'</td></tr>' for k,v in groups.items())+'</tbody></table>'
    document='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / supported object guides</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece7;color:#25332a;font:16px/1.5 system-ui}main{max-width:1120px;margin:auto;padding:24px}a{color:#326c52}h1{line-height:1.15}h2{font-size:22px}.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:16px 0}button{font:inherit;color:inherit;border:1px solid #a0ac9f;border-radius:24px;padding:9px 16px;background:#fffaf0;cursor:pointer}button[aria-pressed=true]{background:#355e47;color:white}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{min-width:0;background:#fffaf0;padding:22px;border-radius:20px}.description{min-height:3em}.stage{aspect-ratio:9/16;max-width:315px;margin:auto;background:#273530;border-radius:14px;overflow:hidden}.stage img{width:100%;height:100%;object-fit:contain;opacity:var(--image-opacity,1)}body[data-background=light] .stage{background:#f7f4ec}body[data-background=checker] .stage{background:conic-gradient(#758277 25%,#3d4c42 0 50%,#758277 0 75%,#3d4c42 0) 0 0 / 24px 24px}.pose{font-variant-numeric:tabular-nums}.scrub{width:min(100%,500px)}label{display:flex;gap:10px;align-items:center;flex-wrap:wrap}input{accent-color:#355e47}p{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border-bottom:1px solid #bdc6bb;text-align:left;vertical-align:top;padding:12px}th:first-child{width:25%}section{margin:40px 0}@media(max-width:680px){.grid{grid-template-columns:1fr}main{padding:18px}}
</style><body data-background="dark"><main><p><a href="../../animations.html">Guide catalog</a> · <a href="../orbit/index.html">Earlier cup-only comparison</a> · <a href="README.md">Rendering notes</a></p>
<h1>Supported objects / line-art guides</h1><p>The cup now rests on its saucer. Four eight-second clips use the existing models, fixed 24 mm lens and continuous phone moves. Camera height and direction change smoothly while the props stay still.</p>
<div class="controls"><button id="play-all">Play all</button><button id="start-all">Starting poses</button><button data-bg="dark" aria-pressed="true">Dark</button><button data-bg="light" aria-pressed="false">Light</button><button data-bg="checker" aria-pressed="false">Checkerboard</button><label>Opacity <input id="opacity" type="range" min="0" max="100" value="100"><output id="opacity-value">100%</output></label></div>
<label>Compare moment <input id="scrub" class="scrub" type="range" min="1" max="240" value="1"><output id="time">0.00 s</output></label><p id="status" role="status">Press Play or scrub the exact camera frames.</p><div class="grid">CARDS</div>
<p>The players use 540×960 previews; full-size links retain the native 1080×1920 frames. Playback runs once and holds the final pose. White contours and their dark underlay are transparent elsewhere; viewfinder and app opacity remain separate.</p>
<section id="models"><h2>What we have now</h2><p>44 newer Tripo object families, plus a local saucer, rack shelf/tray and plant. Functional and scene-ready corrections are preferred where present. The creator, barista and friend with locs also have 65-bone rigs; natural gripping and facial performance need separate work.</p>MODELS<p><a href="available-models.md">Detailed inventory and Blender paths</a> · <a href="available-models.json">Machine-readable inventory</a></p></section>
<section><h2>Useful next scenes</h2><p>Customer-side pastry-display sweep; coffee station from counter to ordered cup; a menu-to-order tilt; a window-side place-setting reveal; burger or brunch detail. Existing assets cover these. Larger scenes need their own contour and occlusion review before rollout.</p><p><a href="completion.json">Batch checks</a>. These are review studies; current app/API guide artwork is unchanged. Physical phone capture is not tested.</p></section></main><script>
const clips=CLIPDATA,states={},status=document.querySelector('#status');let serial=0;
function pose(key,frame){const r=clips[key].frames[frame-1];document.querySelector('#'+key+'-pose').textContent=r.pitch.toFixed(1)+'° down · '+r.yaw.toFixed(1)+'° orbit';}
function still(key,frame=1){delete states[key];const img=document.querySelector('#'+key+'-image');img.onload=null;img.src=key+'/browser/frame_'+String(frame).padStart(4,'0')+'.png';pose(key,frame);}
function play(key){const img=document.querySelector('#'+key+'-image'),run=++serial;states[key]={run,started:null};status.textContent='Loading animation…';img.onload=()=>{if(states[key]?.run!==run)return;states[key].started=performance.now();status.textContent='Playing. The last pose will hold.';};img.onerror=()=>{delete states[key];status.textContent='Could not load the animation. Use its full-size link to inspect the file.';};img.src=key+'/browser/animation.png?replay='+run;}
document.querySelector('#play-all').onclick=()=>Object.keys(clips).forEach(play);
document.querySelector('#start-all').onclick=()=>{Object.keys(clips).forEach(k=>still(k));document.querySelector('#scrub').value=1;document.querySelector('#time').value='0.00 s';status.textContent='Starting poses.';};
document.querySelectorAll('[data-play]').forEach(b=>b.onclick=()=>play(b.dataset.play));document.querySelectorAll('[data-start]').forEach(b=>b.onclick=()=>still(b.dataset.start));
document.querySelector('#scrub').oninput=function(){const frame=Number(this.value);Object.keys(clips).forEach(k=>still(k,frame));document.querySelector('#time').value=((frame-1)/30).toFixed(2)+' s';status.textContent='Comparing frame '+frame+' of 240.';};
document.querySelectorAll('[data-bg]').forEach(b=>b.onclick=()=>{document.body.dataset.background=b.dataset.bg;document.querySelectorAll('[data-bg]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
document.querySelector('#opacity').oninput=function(){document.documentElement.style.setProperty('--image-opacity',Number(this.value)/100);document.querySelector('#opacity-value').value=this.value+'%';};
function tick(){const now=performance.now();for(const [key,state] of Object.entries(states)){if(state.started===null)continue;const frame=Math.min(clips[key].count,1+Math.floor((now-state.started)/1000*clips[key].fps));pose(key,frame);if(frame===clips[key].count){delete states[key];if(!Object.keys(states).length)status.textContent='Finished; holding the final poses. Press Replay to repeat.';}}requestAnimationFrame(tick);}Object.keys(clips).forEach(k=>pose(k,1));tick();
</script></body></html>'''.replace('CARDS',''.join(cards)).replace('MODELS',models).replace('CLIPDATA',json.dumps(clips))
    (root/'index.html').write_text(document)
    (root/'preview-checks.json').write_text(json.dumps(dict(status='passed',clips=reports),indent=2)+'\n')
    print('OBJECT_PREVIEW_READY',root/'index.html',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True,type=Path)
    run(p.parse_args().root.resolve())
