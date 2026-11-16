"""Review Tripo CLI model trials, preserving downloads and reporting actual generation cost."""
import hashlib,html,json,os
from pathlib import Path
from PIL import Image,ImageDraw
REFS=Path(__file__).resolve().parents[2];BASE=REFS.parent
INDEX=REFS/'tripo-cli'
STYLE='''*{box-sizing:border-box}body{font:16px/1.5 system-ui;background:#eee9df;color:#293f34;margin:0}main{max-width:1450px;margin:auto;padding:25px}article,section{padding:22px;border-radius:20px;background:#fffaf0;margin:22px 0}h1{font-size:30px}h2{font-size:22px}a{color:#35674f}img{width:100%;height:auto;object-fit:contain}.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px}.stage{height:min(74vh,800px);background:#f6f1e6;border-radius:12px}.stage img{height:100%}select,button{font:inherit;padding:8px 15px;border:1px solid #91a38e;border-radius:22px;background:#fffaf0;color:inherit}nav{display:flex;flex-wrap:wrap;gap:12px;align-items:center}small{color:#526b5a}table{border-collapse:collapse;width:100%}th,td{text-align:left;border-bottom:1px solid #d6d9cc;padding:9px}@media(max-width:700px){main{padding:15px}.pair{grid-template-columns:1fr}}'''

def page(title,body,script=''):
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{html.escape(title)}</title><style>{STYLE}</style><main>{body}</main>{script}</html>'

def relative(path,root):return Path(os.path.relpath(path,root)).as_posix()

def build():
    manifest=json.loads((INDEX/'next-models.json').read_text());state=json.loads((INDEX/'next-models.batch.yaml.state.json').read_text());records=[];cards=[];verified=[]
    for job in manifest['jobs']:
        aid=job['id'];review=BASE/job['output']/'review';data=json.loads((review/'metadata.json').read_text())
        state_key='loca-'+aid+'-v1';task_id=state['jobs'][state_key]['task_id'];raw=Path(state['jobs'][state_key]['output_dir']);task=json.loads((raw/'task.json').read_text())
        assert task['status']=='success';assert task['task_id']==task_id
        source=Path(data['source']);assert hashlib.sha256(source.read_bytes()).hexdigest()==data['source_sha256']
        views=['preview','front','left','back','right','top','bottom']+(['face','right-hand','left-hand'] if aid!='dining_chair' else [])
        for folder in ['rendered','shape']:
            for v in views:
                p=review/folder/(v+'.png');assert p.exists(),p
                with Image.open(p) as image:image.verify()
                verified.append(str(p.relative_to(BASE)))
        title={'barista':'Barista','friend_locs':'Friend with sculpted locs','dining_chair':'Dining chair'}[aid]
        ref_root=REFS/aid if aid!='dining_chair' else REFS/'objects/dining_chair/design'
        inputs={v:relative(ref_root/(v+'.png'),review) for v in ['front','left','back','right','top','bottom']}
        inputs['preview']=inputs['front']
        for v in ['face','right-hand','left-hand']:inputs[v]=inputs['front']
        count=sum(m['triangles'] for m in data['meshes']);sizes=sorted(set(tuple(i['resolution']) for i in data['textures']))
        support=data['support'];max_lift=support['max_foot_height_difference_m']*1000
        gallery=Image.new('RGB',(1200,850),'#f6f1e6');draw=ImageDraw.Draw(gallery)
        for i,v in enumerate(['front','back','left','right','top','bottom']):
            im=Image.open(review/'rendered'/(v+'.png')).convert('RGBA');im.thumbnail((400,390));bg=Image.new('RGBA',(400,390),'#f6f1e6');bg.alpha_composite(im,((400-im.width)//2,(390-im.height)//2));gallery.paste(bg.convert('RGB'),(i%3*400,i//3*425+25));draw.text((i%3*400+10,i//3*425+6),v.upper(),fill='#354b3c')
        gallery.save(review/'projections.jpg',quality=94)
        options=''.join(f'<option value="{v}">{v.replace("-"," ").title()}</option>' for v in views)
        version=data['source_sha256'][:12]+'-'+str((review/'rendered/preview.png').stat().st_mtime_ns)
        body=f'''<p><a href="{relative(INDEX/'index.html',review)}">All Tripo trials</a></p><h1>{title}</h1><p>Original Tripo CLI result, calibrated by a uniform root transform. The reference art remains unchanged. Both material modes show the same geometry.</p><p><a href="model.blend">Packed Blender model</a> · <a href="asset.blend">Appendable asset</a> · <a href="{relative(source,review)}">Original GLB</a> · <a href="metadata.json">Measured model details</a></p><nav><label for="view">View</label><select id="view">{options}</select><button id="material">Show shape only</button></nav><div class="pair"><article><h2>Reference art</h2><div class="stage"><img id="reference" src="{inputs['front']}" alt="Approved reference"></div></article><article><h2>Actual Blender render</h2><div class="stage"><img id="model" src="rendered/preview.png?v={version}" alt="Tripo model render"></div></article></div><section><h2>Measured results</h2><p>{count:,} triangles · {len(data['meshes'])} mesh parts · texture maps {html.escape(str(sizes))} · {task['credits_consumed']:g} credits.</p><p>Feet detected: {len(support['feet'])}. Maximum lowest-point difference from the review floor: {max_lift:.3f} mm. These are vertex-based support diagnostics; they do not certify load-bearing contacts or animation deformation.</p><p>Characters are unrigged. Generated geometry and original textures are preserved. This is a model review candidate, not a published guide replacement.</p></section><section><h2>Six model projections</h2><img src="projections.jpg?v={version}" alt="Six actual Blender projections"></section>'''
        script=f'''<script>const refs={json.dumps(inputs)},v=document.querySelector('#view');let shape=false;function update(){{document.querySelector('#reference').src=refs[v.value];document.querySelector('#model').src=(shape?'shape/':'rendered/')+v.value+'.png?v={version}';document.querySelector('#material').textContent=shape?'Show original materials':'Show shape only';}}v.onchange=update;document.querySelector('#material').onclick=()=>{{shape=!shape;update()}};</script>'''
        (review/'index.html').write_text(page(title,body,script))
        rel=relative(review,INDEX);cards.append(f'<article><h2><a href="{rel}/index.html">{title}</a></h2><div class="pair"><a href="{rel}/index.html"><img src="{rel}/rendered/preview.png?v={version}" alt="{title}"></a><div><p>{count:,} triangles · {task["credits_consumed"]:g} API credits</p><p>Textures: {html.escape(str(sizes))}. Unrigged review candidate.</p><p><a href="{rel}/index.html">Inspect reference, model and shape</a></p><p><a href="{rel}/model.blend">Blender file</a> · <a href="{relative(source,INDEX)}">Original GLB</a></p><p>Maximum foot clearance: {max_lift:.3f} mm.</p></div></div></article>')
        records.append(dict(id=aid,title=title,task_id=task_id,credits_consumed=task['credits_consumed'],triangles=count,review=str(review.relative_to(BASE)),original=str(source.relative_to(BASE)),source_sha256=data['source_sha256'],textures=sizes,armatures=data['armatures'],support=support,status='review_candidate'))
    total=sum(r['credits_consumed'] for r in records)
    body=f'<h1>Tripo model trials</h1><p>Three new models generated from the existing approved reference views. Actual generation cost: {total:g} API credits. Inspect both original materials and uniform-material shape views before using these candidates in scenes.</p><p><a href="../creator/tripo-comparison/index.html">Earlier creator comparison</a> · <a href="../objects/reconstructed.html">Existing model library</a> · <a href="setup-checks.json">CLI diagnostic report</a> · <a href="generation-report.json">Generation and support measurements</a></p>'+''.join(cards)
    (INDEX/'index.html').write_text(page('Loca Tripo model trials',body))
    report=dict(status='three_models_generated_and_rendered',models=records,actual_credits_consumed=total,estimated_credits=manifest['estimated_generation_credits'],render_images_verified=len(verified),source_files_unmodified=True,api_guide_assets_replaced=False)
    (INDEX/'generation-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(models=len(records),actual_credits=total,render_images=len(verified))))

if __name__=='__main__':build()
