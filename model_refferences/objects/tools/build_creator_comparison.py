"""Browser review of actual Tripo and local Blender renders, with original references."""
import hashlib,html,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]/'creator';OUT=ROOT/'tripo-comparison'
VIEWS=['front','three-quarter','back','left','right','top','bottom','face','face-three-quarter','right-hand','left-hand']

def build():
    metadata=json.loads((OUT/'metadata.json').read_text());source=json.loads((OUT/'source-checks.json').read_text())
    files=[]
    for folder in ['tripo','local-triposr','tripo-shape','local-shape']:
        for view in VIEWS:
            p=OUT/folder/(view+'.png');assert p.exists(),p
            with Image.open(p) as image:image.verify()
            files.append(dict(path=str(p.relative_to(OUT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    def sheet(view,name):
        canvas=Image.new('RGB',(1600,950),'#f6f1e6');draw=ImageDraw.Draw(canvas)
        for i,(folder,label) in enumerate([('local-triposr','LOCAL TRIPOSR'),('tripo','IMPORTED TRIPO')]):
            im=Image.open(OUT/folder/(view+'.png')).convert('RGBA');im.thumbnail((800,880))
            bg=Image.new('RGBA',(800,880),'#f6f1e6');bg.alpha_composite(im,((800-im.width)//2,(880-im.height)//2))
            canvas.paste(bg.convert('RGB'),(800*i,50));draw.text((800*i+24,18),label,fill='#334a3e')
        canvas.save(OUT/name,quality=95)
    sheet('front','comparison-front.jpg');sheet('face','comparison-face.jpg')
    refs={v:'../'+v+'.png' for v in ['front','back','left','right','top','bottom']}
    refs.update({'three-quarter':'../front.png','face':'../reconstruction-inputs/head-front-crop.png',
                 'face-three-quarter':'../reconstruction-inputs/head-front-crop.png','right-hand':'../front.png','left-hand':'../front.png'})
    version=metadata['source_sha256'][:12]+'-'+str((OUT/'tripo/front.png').stat().st_mtime_ns)
    options=''.join(f'<option value="{v}">{html.escape(v.replace("-"," ").title())}</option>' for v in VIEWS)
    count=sum(p['triangles'] for p in metadata['mesh_parts'])
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Creator: Tripo comparison</title><style>
*{{box-sizing:border-box}}body{{font:16px/1.5 system-ui;margin:0;background:#eee9df;color:#263e32}}main{{max-width:1500px;padding:25px;margin:auto}}h1{{font-size:30px;margin-bottom:8px}}a{{color:#35664c}}p{{max-width:1050px}}nav{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;position:sticky;top:0;padding:12px 0;background:#eee9df;z-index:2}}select,button{{font:inherit;border:1px solid #8da28e;background:#fffaf0;color:inherit;border-radius:20px;padding:8px 15px}}button[aria-pressed=true]{{background:#385e49;color:white}}.comparison{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}article,details{{padding:20px;border-radius:20px;background:#fffaf1;margin:15px 0}}h2{{font-size:20px;margin:0 0 10px}}.stage{{height:min(76vh,850px);background:#f6f1e6;border-radius:12px;display:flex;align-items:center;justify-content:center;overflow:hidden}}.stage img{{width:100%;height:100%;object-fit:contain}}.reference{{max-height:500px;max-width:100%;object-fit:contain}}small{{display:block;color:#526b5a}}.findings{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}@media(max-width:700px){{main{{padding:15px}}.comparison,.findings{{grid-template-columns:1fr}}nav{{position:static}}.stage{{height:70vh}}}}
</style><main><p><a href="../../objects/reconstructed.html">Model library</a> · <a href="../contact-sheet.jpg">Approved six-view art</a></p><h1>Creator: Tripo comparison</h1><p>Actual Blender renders of the supplied Tripo GLB and the earlier local TripoSR reconstruction. Both are normalized to 1.72 m and use matching cameras and fixed studio lights. Select a view or inspect the shape with a uniform material.</p><p><a href="creator.blend">Editable Tripo Blender model</a> · <a href="asset.blend">Appendable asset</a> · <a href="../3d%20female%20character.glb">Original GLB</a> · <a href="review.md">Review notes</a></p><nav><label for="view">View</label><select id="view">{options}</select><button id="textured" aria-pressed="true">Original materials</button><button id="shape" aria-pressed="false">Shape only</button><button id="face">Face close-up</button><button id="full">Full figure</button></nav><div class="comparison"><article><h2>Earlier local TripoSR</h2><small>Single front-image reconstruction; existing baseline</small><div class="stage"><img id="local" src="local-triposr/front.png?v={version}" alt="Local creator reconstruction"></div></article><article><h2>Imported Tripo model</h2><small>{count:,} triangles · 11 mesh parts · no skeleton</small><div class="stage"><img id="tripo" src="tripo/front.png?v={version}" alt="Tripo creator model"></div></article></div><details><summary>Approved reference for this view</summary><p>The reference is generated 2D artwork. It is shown for identity and clothing comparison; its perspective and framing are not claimed to match the actual model renders.</p><img id="reference" class="reference" src="../front.png" alt="Approved creator reference"></details><section class="findings"><article><h2>Observed improvements</h2><p>The imported face, eyes, ponytail silhouette, clothing and bag read more clearly. The hair has broad sculpted clay locks. Independent mesh parts provide a useful starting point for further work.</p></article><article><h2>Still to resolve</h2><p>The eye textures have visible artifacts at close range. Hand grips and deformation have not been tested. The model has no rig and is dense for animation. Embedded maps are 256–1024 px per part; no 4K map is present in this export.</p></article></section><p><a href="comparison-front.jpg">Full figure contact sheet</a> · <a href="comparison-face.jpg">Face contact sheet</a> · <a href="metadata.json">Blender import details</a> · <a href="source-checks.json">Original-file checks</a></p><p>Original geometry, textures and material settings are retained. Only a root rotation, uniform scale and ground translation are applied in the Blender copy. The material override is for diagnostic renders. This candidate has not replaced any guide assets.</p></main><script>
const refs={json.dumps(refs)},version={json.dumps(version)},view=document.querySelector('#view');let shape=false;
function update(){{const v=view.value;document.querySelector('#local').src=(shape?'local-shape/':'local-triposr/')+v+'.png?v='+version;document.querySelector('#tripo').src=(shape?'tripo-shape/':'tripo/')+v+'.png?v='+version;document.querySelector('#reference').src=refs[v];document.querySelector('#textured').setAttribute('aria-pressed',String(!shape));document.querySelector('#shape').setAttribute('aria-pressed',String(shape));}}
view.onchange=update;document.querySelector('#textured').onclick=()=>{{shape=false;update()}};document.querySelector('#shape').onclick=()=>{{shape=true;update()}};document.querySelector('#face').onclick=()=>{{view.value='face';update()}};document.querySelector('#full').onclick=()=>{{view.value='front';update()}};
</script></html>'''
    (OUT/'index.html').write_text(page)
    (OUT/'render-checks.json').write_text(json.dumps(dict(status='passed',render_images=len(files),images=files,
        source_sha256=source['source_sha256'],source_file_unmodified=hashlib.sha256((ROOT/'3d female character.glb').read_bytes()).hexdigest()==source['source_sha256'],
        comparison_camera_and_lighting_shared=True,source_generation_settings_unknown=True),indent=2)+'\n')
    print('CREATOR_COMPARISON_GALLERY_BUILT',len(files))

if __name__=='__main__':build()
