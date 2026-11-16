"""Local, playable APNG guide catalog. No generated illustration is drawn here."""
import html
import json
import shutil
from pathlib import Path

from PIL import Image, ImageSequence

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
GUIDES=ROOT/'guides'
MOTION=GUIDES/'watercolor_motion'
UI='../guides/shot-proof/cup_eye_orbitr_cc/viewfinder.png'


def entries():
    manifest=json.loads((MOTION/'manifest.json').read_text())
    completed=HERE/'animations/index.json'
    ready=set(json.loads(completed.read_text())['guides']) if completed.exists() else set()
    records=[]
    for entry in manifest['guides']:
        gid=entry['id'];watercolor=gid in ready
        stable=watercolor and entry.get('rendering',{}).get('method') in ('single_source_crop','layered_animation')
        mode=entry.get('rendering',{}).get('mode','').replace('_',' ')
        folder=HERE/'animations'/gid
        if watercolor:
            assert entry['status'] in ('approved','keyframes_reviewed')
            animation=f'animations/{gid}/guide_with_guides.png'
            raw=f'animations/{gid}/guide.png'
            poster=f'animations/{gid}/poster_with_guides.png'
            strip=f'animations/{gid}/strip.png'
        else:
            animation=f'../guides/overlays/schematic/{gid}.png';raw=animation
            poster=f'animations/original-posters/{gid}.png'
            strip=f'strips/{gid}.png'
        still=(stable and entry['rendering']['mode']=='hold') or (not stable and all(w.get('camera_static') for w in entry['windows']) and not any(s['kind']=='still' for s in entry['source_live_steps']))
        records.append(dict(id=gid,description=entry['description'],watercolor=watercolor,
                            label=('Watercolor / local '+mode) if stable else ('Watercolor preview' if watercolor else 'Original schematic'),stable=stable,
                            animation=animation,raw=raw,poster=poster,strip=strip,still=still,limitation=entry.get('rendering',{}).get('limitation','')))
    return records


def prepare_posters(records):
    folder=HERE/'animations/original-posters';folder.mkdir(parents=True,exist_ok=True)
    for entry in records:
        destination=HERE/entry['poster']
        if destination.exists():continue
        clock=0
        with Image.open(HERE/entry['animation']) as source:
            for frame in ImageSequence.Iterator(source):
                poster=frame.convert('RGBA')
                clock+=frame.info.get('duration',1000/15)/1000
                if clock>=1:break
            poster.save(destination)


PLAYER_SCRIPT='''
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
function play(card){const img=card.querySelector('.motion-image');img.src=img.dataset.animation+'?play='+Date.now();card.dataset.playing='true';}
function pause(card){const img=card.querySelector('.motion-image');img.src=img.dataset.poster;card.dataset.playing='false';}
document.querySelectorAll('.motion-card').forEach(card=>{
 card.querySelector('[data-play]')?.addEventListener('click',()=>play(card));
 card.querySelector('[data-pause]')?.addEventListener('click',()=>pause(card));
});
const observer=new IntersectionObserver(items=>items.forEach(item=>{
 if(item.isIntersecting&&!reduced)play(item.target);else pause(item.target);
}),{threshold:.15});
document.querySelectorAll('.motion-card').forEach(card=>observer.observe(card));
'''


def player(entry,compact=False):
    e=html.escape;gid=e(entry['id'])
    overlay='' if entry['watercolor'] else f'<img class="fixed-sights" src="{UI}" alt="">'
    return f'''<div class="motion-card{' compact' if compact else ''}" data-guide="{gid}">
<div class="motion-stage"><img class="motion-image" loading="lazy" src="{e(entry['poster'])}" data-poster="{e(entry['poster'])}" data-animation="{e(entry['animation'])}" alt="Animated guide: {gid}">{overlay}</div>
<div class="motion-controls"><button type="button" data-play>Play / replay</button><button type="button" data-pause>Starting pose</button></div>
</div>'''


def build():
    records=entries();prepare_posters(records)
    archive=HERE/'backups/pre-animated-previews/strips'
    for record in records:
        if not record['watercolor']:continue
        destination=HERE/'strips'/f'{record["id"]}.png'
        if destination.exists():
            archive.mkdir(parents=True,exist_ok=True)
            if not (archive/destination.name).exists():shutil.copy2(destination,archive/destination.name)
        shutil.copy2(HERE/record['strip'],destination)
    (HERE/'strips/index.json').write_text(json.dumps({e['id']:e['label'] for e in records},indent=2)+'\n')
    watercolor=sum(e['watercolor'] for e in records)
    stable_count=sum(e['stable'] for e in records)
    parts=['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Live guide animations</title><style>
*{box-sizing:border-box}body{margin:0;background:#f1efe8;color:#253943;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1440px;margin:auto;padding:28px}header{max-width:960px}h1{font-size:32px;font-weight:550;margin:10px 0}h2{font-size:15px;overflow-wrap:anywhere;margin:0}p{margin:9px 0}a{color:#326079}nav{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0;position:sticky;top:0;padding:12px;background:#f1efe8;z-index:2;border-bottom:1px solid #c5cece}input,select,button{font:inherit;padding:7px 10px;border:1px solid #a6b7bc;border-radius:5px;background:white;color:inherit}input{flex:1;min-width:220px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}.guide{background:#fbfaf6;border:1px solid #c9d1d1;border-radius:8px;overflow:hidden;padding:14px}.guide[hidden]{display:none}.guide{scroll-margin-top:90px}.cards.single{display:block;max-width:440px;margin:0 auto}.cards.single .motion-stage{height:640px}.description{font-size:12px;min-height:92px}.badge{font-size:12px;display:inline-block;margin:7px 0;color:#4b636c}.badge.new{color:#28684d;font-weight:600}.motion-stage{height:410px;background:#23343e;position:relative;overflow:hidden}.motion-image,.fixed-sights{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}.fixed-sights{pointer-events:none}.motion-controls{display:flex;gap:6px;margin:9px 0}.motion-controls button{font-size:12px;flex:1}.guide footer{font-size:12px;display:flex;gap:14px}.strip{width:100%;display:block;margin:9px 0}#count{align-self:center;font-size:13px}@media(max-width:600px){main{padding:15px}h1{font-size:26px}nav{position:static}.cards{grid-template-columns:1fr}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style></head><body><main><header><a href="catalog.html">Script catalog</a> / <a href="regeneration-report.md">Regeneration report</a><h1>Live guide animations</h1>''',
           f'<p><strong>{watercolor} watercolor previews</strong> at 50% alpha, with fixed viewfinder and horizon guides. The other {len(records)-watercolor} use their original schematic animations.</p>',
           f'<p>{stable_count} previews use fixed paintings and local camera or cutout animation: pans, zooms, tilts, layered reveals and parallax. Linework and pigment stay consistent between frames. <a href="local-motion-audit.md">Full motion audit and limits</a>. <a href="composition-audit.html">Composition and static-take audit</a>.</p>',
           '<p>Clips play when visible. Use Play / replay or Starting pose to inspect the camera move. Static guides hold the framing. These are browser animation previews; the PDF shows printable frame strips.</p></header>',
           '<nav><input id="search" type="search" placeholder="Find a guide or subject" aria-label="Find a guide"><select id="filter" aria-label="Animation style"><option value="stable">Local motion / layers</option><option value="new">Watercolor previews</option><option value="all">All guides</option><option value="original">Original schematic</option></select><button id="show-all" type="button">Show all</button><span id="count"></span></nav><div class="cards">']
    e=html.escape
    for record in records:
        gid=record['id'];parts.append(f'<article class="guide" id="{e(gid)}" data-new="{str(record["watercolor"]).lower()}" data-stable="{str(record["stable"]).lower()}" data-search="{e((gid+" "+record["description"]).lower())}"><h2>{e(gid)}</h2><span class="badge {"new" if record["watercolor"] else ""}">{e(record["label"])}{" / static hold" if record["still"] else ""}</span>')
        if record['limitation']:parts.append(f'<p class="description">{e(record["limitation"])}</p>')
        parts.append(player(record))
        parts.append(f'<p class="description">{e(record["description"])}</p><img class="strip" loading="lazy" src="{e(record["strip"])}" alt="Six animation samples"><footer><a href="{e(record["animation"])}" download>Animation with guides</a><a href="{e(record["raw"])}" download>Artwork APNG</a></footer></article>')
    parts+=['</div></main><script>',PLAYER_SCRIPT,'''const search=document.getElementById('search'),filter=document.getElementById('filter');
function applyFilter(){let count=0;document.querySelectorAll('.guide').forEach(card=>{const style=filter.value;const matches=style==='all'||(style==='stable'&&card.dataset.stable==='true')||(style==='new'&&card.dataset.new==='true')||(style==='original'&&card.dataset.new==='false');card.hidden=!matches||!card.dataset.search.includes(search.value.trim().toLowerCase());if(!card.hidden)count++;else pause(card.querySelector('.motion-card'));});document.querySelector('.cards').classList.toggle('single',count===1);document.getElementById('count').textContent=count+' guides';}
search.addEventListener('input',applyFilter);filter.addEventListener('change',applyFilter);
document.getElementById('show-all').onclick=()=>{search.value='';filter.value='all';history.replaceState(null,'',location.pathname);applyFilter();};
function fromHash(){const id=decodeURIComponent(location.hash.slice(1));if(id){const target=document.getElementById(id);if(target){filter.value='all';search.value=id;applyFilter();target.scrollIntoView();play(target.querySelector('.motion-card'));return;}}applyFilter();}
window.addEventListener('hashchange',fromHash);fromHash();
</script></body></html>''']
    (HERE/'animations.html').write_text('\n'.join(parts))
    print(f'animations.html: {watercolor} new playable previews; {len(records)-watercolor} original animations.')


if __name__=='__main__':build()
