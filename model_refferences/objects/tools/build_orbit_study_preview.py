"""Publish two lossless, play-once orbit studies with synchronized frame scrubbing."""
import argparse,json
from pathlib import Path
from PIL import Image
from pack_full_frame_apng import pack

def run(root):
    data={};checks={};cards=[]
    for key,title,description in [
        ('steady','Steady 45° orbit','A steady 45° downward view. Soft acceleration, one smooth 90° arc, then a settled finish.'),
        ('cinematic','Orbit with gentle angle changes','45° → 37° → 53° → 45°. The phone lowers slightly, rises to reveal the heart, then settles while continuing around the cup.')]:
        folder=root/key;meta=json.loads((folder/'meta.json').read_text());review=json.loads((folder/'orbit-checks.json').read_text());assert review['status']=='passed'
        pack(folder,folder/'animation.png',meta['frame_count'],meta['fps'],plays=1)
        with Image.open(folder/'animation.png') as animation:
            assert animation.n_frames==meta['frame_count'] and animation.info['loop']==1
            for number in range(meta['frame_count']):
                animation.seek(number)
                with Image.open(folder/f'frame_{number+1:04d}.png') as source:assert animation.convert('RGBA').tobytes()==source.convert('RGBA').tobytes()
        data[key]=dict(fps=meta['fps'],count=meta['frame_count'],frames=[dict(pitch=r['pitch_degrees'],yaw=r['azimuth_degrees']) for r in meta['frames']])
        checks[key]=dict(status='passed',decoded_pixels_match_source=True,plays=1,frames=meta['frame_count'])
        cards.append(f'''<article data-key="{key}"><h2>{title}</h2><p>{description}</p><div class="stage"><img id="{key}-image" src="{key}/frame_0001.png" alt="Filled cup with a heart, {title}"></div><p class="pose" id="{key}-pose">45° pitch · -45° orbit</p><div class="row"><button data-play="{key}">Play / replay</button><button data-start="{key}">Starting pose</button></div><p><a href="{key}/animation.png">Full-size animation</a> · <a href="{key}/scene.blend">Blender scene</a> · <a href="{key}/meta.json">Camera metadata</a> · <a href="{key}/orbit-checks.json">Checks</a></p></article>''')
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / smooth filled-cup orbit</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece7;color:#25332a;font:16px/1.5 system-ui}main{max-width:1120px;margin:auto;padding:24px}h1{line-height:1.15}h2{font-size:22px}a{color:#326c52}.row,.controls{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:16px 0}button{font:inherit;color:inherit;border:1px solid #a0ac9f;border-radius:24px;padding:9px 16px;background:#fffaf0;cursor:pointer}button[aria-pressed=true]{background:#355e47;color:white}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px}article{min-width:0;background:#fffaf0;padding:22px;border-radius:20px}.stage{position:relative;aspect-ratio:9/16;max-height:680px;background:#273530;border-radius:14px;overflow:hidden}.stage img{width:100%;height:100%;object-fit:contain;opacity:var(--image-opacity,1)}body[data-background=light] .stage{background:#f7f4ec}body[data-background=checker] .stage{background:conic-gradient(#758277 25%,#3d4c42 0 50%,#758277 0 75%,#3d4c42 0) 0 0 / 24px 24px}.pose{font-variant-numeric:tabular-nums}.scrub{width:min(100%,500px)}label{display:flex;gap:10px;align-items:center;flex-wrap:wrap}input{accent-color:#355e47}p{overflow-wrap:anywhere}@media(max-width:680px){.grid{grid-template-columns:1fr}main{padding:18px}}
</style><body data-background="dark"><main><p><a href="../index.html">Earlier line-art tests</a> · <a href="README.md">Orbit notes</a></p><h1>Filled cup / smooth orbit comparison</h1><p>The same cup, coffee surface and foam heart in both clips. The heart and coffee hide the handle geometry inside the opening. Each clip is eight seconds at 30 fps, with the same fixed lens and distance. Only the camera moves.</p><div class="controls"><button id="play-both">Play both</button><button id="start-both">Starting poses</button><button data-bg="dark" aria-pressed="true">Dark</button><button data-bg="light" aria-pressed="false">Light</button><button data-bg="checker" aria-pressed="false">Checkerboard</button><label>Opacity <input id="opacity" type="range" min="0" max="100" value="100"><output id="opacity-value">100%</output></label></div><label>Compare the same moment <input id="scrub" class="scrub" type="range" min="1" max="240" value="1"><output id="time">0.00 s</output></label><p id="status" role="status">Press Play both, or scrub to compare the two camera paths.</p><div class="grid">'''+''.join(cards)+'''</div><p>Playback holds the last pose. Use Replay to start again; there is no abrupt automatic reset. Both clips retain transparent interiors, white contour lines and a dark underlay. The coffee is opaque only during contour/occlusion extraction; shaded surfaces are not rendered.</p><p><a href="completion.json">Rendering and camera checks</a></p></main><script>
const clips=CLIPDATA,states={},status=document.querySelector('#status');let serial=0;
function pose(key,frame){const r=clips[key].frames[frame-1];document.querySelector('#'+key+'-pose').textContent=r.pitch.toFixed(1)+'° pitch · '+r.yaw.toFixed(1)+'° orbit';}
function still(key,frame=1){delete states[key];const img=document.querySelector('#'+key+'-image');img.onload=null;img.src=key+'/frame_'+String(frame).padStart(4,'0')+'.png';pose(key,frame);}
function play(key){const img=document.querySelector('#'+key+'-image'),run=++serial;states[key]={run,started:null};status.textContent='Loading orbit…';img.onload=()=>{if(states[key]?.run!==run)return;states[key].started=performance.now();status.textContent='Playing. The last pose will hold.';};img.src=key+'/animation.png?replay='+run;}
document.querySelector('#play-both').onclick=()=>Object.keys(clips).forEach(play);
document.querySelector('#start-both').onclick=()=>{Object.keys(clips).forEach(k=>still(k));document.querySelector('#scrub').value=1;document.querySelector('#time').value='0.00 s';status.textContent='Starting poses.';};
document.querySelectorAll('[data-play]').forEach(b=>b.onclick=()=>play(b.dataset.play));document.querySelectorAll('[data-start]').forEach(b=>b.onclick=()=>still(b.dataset.start));
document.querySelector('#scrub').oninput=function(){const frame=Number(this.value);Object.keys(clips).forEach(k=>still(k,frame));document.querySelector('#time').value=((frame-1)/30).toFixed(2)+' s';status.textContent='Comparing frame '+frame+' of 240.';};
document.querySelectorAll('[data-bg]').forEach(b=>b.onclick=()=>{document.body.dataset.background=b.dataset.bg;document.querySelectorAll('[data-bg]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));});
document.querySelector('#opacity').oninput=function(){document.documentElement.style.setProperty('--image-opacity',Number(this.value)/100);document.querySelector('#opacity-value').value=this.value+'%';};
function tick(){const now=performance.now();for(const [key,state] of Object.entries(states)){if(state.started===null)continue;const frame=Math.min(clips[key].count,1+Math.floor((now-state.started)/1000*clips[key].fps));pose(key,frame);if(frame===clips[key].count){delete states[key];status.textContent='Finished; holding the last pose. Press Replay to repeat.';}}requestAnimationFrame(tick);}tick();
</script></body></html>'''.replace('CLIPDATA',json.dumps(data))
    text=text.replace('.stage{position:relative;aspect-ratio:', '.stage{max-width:382.5px;margin:auto;position:relative;aspect-ratio:')
    (root/'index.html').write_text(text)
    (root/'preview-checks.json').write_text(json.dumps(dict(status='passed',clips=checks,global_opacity_not_baked=True),indent=2)+'\n')
    print(json.dumps(dict(status='ready',preview=str(root/'index.html'))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();run(a.root.resolve())
