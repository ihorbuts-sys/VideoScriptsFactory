"""A progressively populated player for the P0 animation exports."""
import hashlib,json,shutil,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'guides/tools'))
import p0_catalog


def build():
    root=ROOT/'catalog/p0';plan=p0_catalog.registry();records=[];ready=0
    for record in plan['guides']:
        if record.get('availability') in ('deferred','archived'):continue
        row={k:record[k] for k in ['id','title','shotType','invariant','durationSec','setupBeatSeconds']}
        if record.get('allowedPeople'):row.update(camera=record['camera'],filmingMode=record['filmingMode'],previewMirrored=record['previewMirrored'])
        folder=root/'animations-light'/row['id'];check=folder/'export-checks.json'
        row['ready']=False
        if check.exists():
            checks=json.loads(check.read_text());source=ROOT/'guides/p0/renders'/(row['id']+'.png')
            object_only=checks.get('maximum_hands',99)<=record.get('allowedHands',0) and checks.get('silhouettes',99)<=record.get('allowedSilhouettes',0) and checks.get('detailed_people',99)<=record.get('allowedPeople',0)
            if object_only and checks['status']=='passed' and source.exists() and hashlib.sha256(source.read_bytes()).hexdigest()==checks['sha256']:
                for suffix in ['.png','_poster.png','_selector.png']:
                    src=source.parent/(row['id']+suffix);target=folder/('guide'+suffix)
                    if not target.exists() or src.stat().st_mtime_ns>target.stat().st_mtime_ns:shutil.copy2(src,target)
                row.update(ready=True,base='animations-light/'+row['id']+'/',sha256=checks['sha256'],seconds=checks['seconds'])
                ready+=1
        records.append(row)
    active={g['id'] for g in records}
    types=[{**kind,'guides':[gid for gid in kind['guides'] if gid in active]} for kind in plan['shotTypes']]
    manifest=dict(ready=ready,total=len(records),types=types,guides=records,deferredGuides=plan.get('deferredGuides',{}))
    temp=root/'players.tmp';temp.write_text(json.dumps(manifest,indent=2)+'\n');temp.replace(root/'players.json')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / P0 line-art guides</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece7;color:#263a2d;font:16px/1.5 system-ui}main{max-width:1180px;margin:auto;padding:24px}a{color:#326c52}button{font:inherit;padding:9px 15px;border:1px solid #9ba99d;border-radius:24px;background:#fffaf0;cursor:pointer}button[aria-pressed=true]{background:#355e47;color:white}.controls{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}article{padding:20px;background:#fffaf0;border-radius:18px;min-width:0}h1{line-height:1.1}h3{font-size:19px;min-height:3em}.stage{position:relative;width:min(100%,324px);aspect-ratio:9/16;margin:auto;background:#24352d;border-radius:12px;overflow:hidden}.stage img{width:100%;height:100%;opacity:var(--opacity,.65)}body[data-bg=light] .stage{background:#f8f4ed}section{margin:40px 0}.pending{padding:20px;border:1px dashed #9ba99d;border-radius:18px}p{overflow-wrap:anywhere}.finder{display:none;position:absolute;inset:0;pointer-events:none;background:linear-gradient(to right,transparent calc(33.333% - .5px),#ffffff38 33.333%,transparent calc(33.333% + .5px),transparent calc(66.666% - .5px),#ffffff38 66.666%,transparent calc(66.666% + .5px)),linear-gradient(to bottom,transparent calc(33.333% - .5px),#ffffff38 33.333%,transparent calc(33.333% + .5px),transparent calc(66.666% - .5px),#ffffff38 66.666%,transparent calc(66.666% + .5px))}body[data-finder=true] .finder{display:block}.finder:after{content:'';position:absolute;left:40%;right:40%;top:50%;height:1px;background:#ffd65399}@media(max-width:600px){main{padding:18px}}
</style><body data-bg="dark"><main><p><a href="../animations.html">Guide catalog</a> · <a href="progress.json">Batch progress</a></p><h1>P0 / line-art animations</h1><p>Transparent white contours, restrained yellow light-facing accents and a soft local glow on steam. The target frame opens each guide, followed by the shot demonstration and the same target at the end.</p><p id="count" role="status">Loading available animations…</p><div class="controls"><button data-opacity=".65" aria-pressed="true">Before capture · 65%</button><button data-opacity=".30">During capture · 30%</button><button data-bg="dark">Dark</button><button data-bg="light">Light</button><button id="finder">Viewfinder</button></div><div id="groups"></div><p>Step-card pictures are separate from these animated overlays. Source frames, Blender scenes and per-guide checks are stored beside each animation. Canonical creator guides include mirrored front-camera and friend-filmed rear-camera options. The existing rig demonstrates framing and gestures; chewing and talking are not simulated. Choose First visit under Cafe or Restaurant. See the <a href="README.md">results and verification notes</a>.</p></main><script>
const groups=document.querySelector('#groups'),cards=new Map();let serial=0,jumpedToHash=false;
function show(record,container){let card=cards.get(record.id);if(card&&card.dataset.sha===record.sha256)return;if(card&&card.dataset.playing==='true')return;
if(!card){card=document.createElement('article');card.id=record.id;container.append(card);cards.set(record.id,card)}card.dataset.sha=record.sha256;card.replaceChildren();
const title=document.createElement('h3');title.textContent=record.title;card.append(title);const stage=document.createElement('div');stage.className='stage';const img=new Image();img.alt=record.title;img.src=record.base+'guide_poster.png?v='+record.sha256.slice(0,12);stage.append(img);const finder=document.createElement('div');finder.className='finder';stage.append(finder);card.append(stage);
const controls=document.createElement('div');controls.className='controls';const play=document.createElement('button');play.textContent='Play / replay';const stop=document.createElement('button');stop.textContent='Target pose';controls.append(play,stop);card.append(controls);
if(record.filmingMode){const mode=document.createElement('p');mode.textContent=record.filmingMode==='selfie'?'Front camera · mirrored preview':'Filmed by a friend · rear camera';card.append(mode)}const caption=document.createElement('p');caption.textContent=record.invariant;card.append(caption);const status=document.createElement('p');status.textContent=record.seconds+' s · '+record.id;card.append(status);
let generation=0;play.onclick=()=>{const current=++generation;card.dataset.playing='true';status.textContent='Loading animation…';img.onload=()=>{if(current!==generation)return;status.textContent='Playing the target-first guide.';setTimeout(()=>{if(current===generation){status.textContent='Finished; holding the target.';card.dataset.playing='false'}},record.seconds*1000)};img.src=record.base+'guide.png?v='+record.sha256.slice(0,12)+'&replay='+(++serial)};
stop.onclick=()=>{generation++;card.dataset.playing='false';img.onload=null;img.src=record.base+'guide_poster.png?v='+record.sha256.slice(0,12);status.textContent='Target pose.'};
const links=document.createElement('p');for(const [label,file] of [['Animation','guide.png'],['Selector','guide_selector.png'],['Blender scene','scene.blend'],['Checks','export-checks.json']]){const a=document.createElement('a');a.textContent=label;a.href=record.base+file;if(links.childNodes.length)links.append(' · ');links.append(a)}card.append(links)}
async function refresh(){try{const response=await fetch('players.json?refresh='+Date.now(),{cache:'no-store'});const data=await response.json();const available=new Set(data.guides.filter(g=>g.ready).map(g=>g.id));for(const [id,card] of cards){if(!available.has(id)){card.remove();cards.delete(id)}}document.querySelector('#count').textContent=data.ready+' of '+data.total+(data.ready===data.total?' animations ready. Collection complete.':' animations ready. New results appear here as exports finish.');for(const type of data.types){if(!type.guides.length){document.getElementById('type-'+type.id)?.remove();continue}let section=document.getElementById('type-'+type.id);if(!section){section=document.createElement('section');section.id='type-'+type.id;const heading=document.createElement('h2');heading.textContent=type.title;section.append(heading);const grid=document.createElement('div');grid.className='grid';section.append(grid);groups.append(section)}const grid=section.querySelector('.grid');for(const record of data.guides.filter(g=>g.shotType===type.id&&g.ready))show(record,grid)}if(!jumpedToHash&&location.hash){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(target){target.scrollIntoView({block:'start'});jumpedToHash=true}}}catch{document.querySelector('#count').textContent='Could not refresh the batch. Existing players remain available.'}}
document.querySelectorAll('[data-opacity]').forEach(b=>b.onclick=()=>{document.documentElement.style.setProperty('--opacity',b.dataset.opacity);document.querySelectorAll('[data-opacity]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)))});document.querySelectorAll('[data-bg]').forEach(b=>b.onclick=()=>document.body.dataset.bg=b.dataset.bg);document.querySelector('#finder').onclick=()=>document.body.dataset.finder=String(document.body.dataset.finder!=='true');refresh();setInterval(refresh,5000);
</script></body></html>'''
    (root/'index.html').write_text(html)
    print(json.dumps(dict(ready=ready,total=len(records),url='http://127.0.0.1:8766/p0/index.html')),flush=True)
    return ready


if __name__=='__main__':build()
