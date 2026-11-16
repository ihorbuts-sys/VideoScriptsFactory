"""Package checked native PNGs losslessly and make a light/dark transparency preview."""
import argparse,html,json
from pathlib import Path
from PIL import Image
from pack_full_frame_apng import pack

def run(study):
    report=json.loads((study/'test-report.json').read_text());assert report['status']=='passed'
    output=study.parent;cards=[]
    cases=[('cup-top-push','Your cup / top detail push-in'),('cup-top-wide','Your cup / complete top view'),
        ('cup-eye-hidden','Your cup / eye level and hidden edges'),('synthetic-top-push','Cylinder and torus / required test')]
    for name,title in cases:
        folder=study/name;meta=json.loads((folder/'meta.json').read_text());validation=json.loads((folder/'validation.json').read_text())
        assert validation['status']=='passed';count=meta['frame_count']
        if count>1:
            pack(folder,folder/'animation.png',count,meta['fps'])
            with Image.open(folder/'animation.png') as animation:
                assert animation.n_frames==count
                for number in range(count):
                    animation.seek(number)
                    with Image.open(folder/f'frame_{number+1:04d}.png') as source:assert animation.convert('RGBA').tobytes()==source.convert('RGBA').tobytes()
        prefix=html.escape(str(folder.relative_to(output)))+'/'
        motion='animation.png' if count>1 else 'frame_0001.png'
        status=f'{meta["actual_final_height_fraction"]:.0%} actual frame height; '+('full bounding box fits.' if meta['fits_frame'] else 'bounding box crosses the frame edge.')
        if meta['minimum_focus_limited']:status+=' The 0.15 m focus limit takes priority over the requested detail size.'
        cards.append(f'''<article><h2>{title}</h2><div class="stage"><img src="{prefix}frame_0001.png" data-poster="{prefix}frame_0001.png" data-animation="{prefix}{motion}" alt="{title}"></div><p><button class="play" type="button">Play / replay</button> <button class="stop" type="button">Starting pose</button></p><p>{count} frame{'s' if count!=1 else ''} at 30 fps. {html.escape(status)}</p><p><a href="{prefix}meta.json">Camera and safe-zone metadata</a> · <a href="{prefix}validation.json">Alpha checks</a> · <a href="{prefix}scene.blend">Blender scene</a></p></article>''')
    text='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca / native line-art cup study</title><style>
*{box-sizing:border-box}body{margin:0;background:#eeece7;color:#25332a;font:16px/1.5 system-ui}main{max-width:1160px;margin:auto;padding:24px}h1{line-height:1.15}h2{font-size:20px}a{color:#326c52}.controls{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:20px 0}button{border:1px solid #98a599;border-radius:24px;padding:9px 15px;background:#fffaf0;color:inherit;font:inherit;cursor:pointer}button[aria-pressed=true]{background:#355e47;color:white}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:22px}article{min-width:0;border-radius:20px;padding:20px;background:#fffaf0}.stage{position:relative;aspect-ratio:9/16;max-height:640px;background:#273530;border-radius:14px;overflow:hidden}.stage img{width:100%;height:100%;object-fit:contain;opacity:var(--image-opacity,1)}body[data-background=light] .stage{background:#f7f4ec}body[data-background=checker] .stage{background:conic-gradient(#758277 25%,#3d4c42 0 50%,#758277 0 75%,#3d4c42 0) 0 0 / 24px 24px}p{overflow-wrap:anywhere}label{display:flex;gap:8px;align-items:center}input{accent-color:#355e47}
</style><body data-background="dark"><main><p><a href="../animations.html">Guide catalog</a> · <a href="README.md">Renderer and test notes</a></p><h1>Cup / native line-art study</h1><p>White contours with a dark underlay on transparent pixels. There are no shaded cup surfaces. The first three examples use the existing cup model. Choose a light background to inspect the dark underlay, or the checkerboard to see transparency.</p><div class="controls"><button data-bg="dark" aria-pressed="true">Dark</button><button data-bg="light" aria-pressed="false">Light</button><button data-bg="checker" aria-pressed="false">Checkerboard</button><label>Image opacity <input id="opacity" type="range" min="0" max="100" value="100"><output id="opacity-value">100%</output></label></div><div class="grid">'''+''.join(cards)+'''</div><p>Each animation has a half-second still finish. Framing follows the requested height; metadata reports any horizontal cropping and focus-distance limit. Viewfinder graphics are separate from these images.</p><p><a href="'''+html.escape(study.name)+'''/test-report.json">Import, animation and failure checks</a></p></main><script>
let replay=0;
document.querySelectorAll('article').forEach(card=>{const img=card.querySelector('img');card.querySelector('.play').onclick=()=>{img.src=img.dataset.animation+'?replay='+(++replay)};card.querySelector('.stop').onclick=()=>{img.src=img.dataset.poster}});
document.querySelectorAll('[data-bg]').forEach(button=>button.onclick=()=>{document.body.dataset.background=button.dataset.bg;document.querySelectorAll('[data-bg]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)))});
document.querySelector('#opacity').oninput=function(){document.documentElement.style.setProperty('--image-opacity',Number(this.value)/100);document.querySelector('#opacity-value').value=this.value+'%'};
</script></body></html>'''
    (output/'index.html').write_text(text)
    (output/'preview-checks.json').write_text(json.dumps(dict(status='passed',apng_pixels_match_native_frames=True,global_opacity_not_baked=True,source_test_report=str(study/'test-report.json')),indent=2)+'\n')
    print(json.dumps(dict(status='ready',preview=str(output/'index.html'))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--study',type=Path,required=True);a=p.parse_args();run(a.study.resolve())
