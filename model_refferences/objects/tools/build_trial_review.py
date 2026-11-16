"""Compare generated design, original reconstruction and matte-clay cleanup."""
import html,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reconstruction-trial/croissant-triposr'
VIEWS=['front','back','left','right','top','bottom']

def tile(path,size=(360,360)):
    im=Image.open(path).convert('RGBA');im.thumbnail(size,Image.Resampling.LANCZOS)
    bg=Image.new('RGBA',size,'#f7f2e7');bg.alpha_composite(im,((size[0]-im.width)//2,(size[1]-im.height)//2))
    return bg.convert('RGB')

def run():
    report=json.loads((OUT/'report.json').read_text())
    sheets=[]
    for title,folder in [('Generated design references',ROOT/'croissant/design'),('Original neural reconstruction',OUT/'rendered'),('Clean clay material and surface smoothing',OUT/'cleaned')]:
        sheet=Image.new('RGB',(2160,405),'#f7f2e7');draw=ImageDraw.Draw(sheet);draw.text((12,8),title,fill='#293c30')
        for i,view in enumerate(VIEWS):
            sheet.paste(tile(folder/(view+'.png')),(i*360,43));draw.text((i*360+12,28),view.upper(),fill='#293c30')
        sheets.append(sheet)
    combined=Image.new('RGB',(2160,1215),'#f7f2e7')
    for i,sheet in enumerate(sheets):combined.paste(sheet,(0,i*405))
    combined.save(OUT/'comparison.jpg',quality=94)
    reference=ROOT/'croissant/design/front.png'
    review=dict(status='local_trial_completed_pending_owner_style_feedback',shape='Front silhouette follows the generated design more closely than the rejected parametric proxy.',
        limitations=['Only the front reference conditions TripoSR inference. The back, sides, top and bottom are inferred, not six-view fitted.',
            'Original inferred vertex colors contain ring-like artifacts and dark marks. The cleaned variant uses a flat matte clay material and gentle mesh smoothing.',
            'No character reconstruction, rig validation or scene animation replacement has been completed by this trial.'],
        original_vertices=report['vertices'],original_faces=report['faces'],watertight=report['watertight'],
        original_meshes=['reconstruction.glb','reconstruction.ply'],blender_models=['reconstructed.blend','clay-cleaned.blend'],
        native_projection_images=14,published_animation_replacements=0,source_image=str(reference.relative_to(ROOT)))
    (OUT/'visual-review.json').write_text(json.dumps(review,indent=2)+'\n')
    text=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Loca local image-to-3D trial</title>
<style>body{{font:16px system-ui;background:#eee9dd;color:#293c30;max-width:1350px;padding:24px;margin:auto}}img{{max-width:100%;height:auto;border-radius:16px}}article{{background:#fffaf0;padding:24px;border-radius:18px;margin:20px 0}}a{{color:#35634e}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}p,li{{line-height:1.5}}</style>
<h1>Local image-driven reconstruction: croissant</h1>
<p>Official MIT-licensed TripoSR ran locally on the Apple GPU. {report['faces']:,} triangles, {report['vertices']:,} vertices, watertight mesh. Inference and extraction: {report['duration_s']:.1f} seconds, excluding setup and downloads.</p>
<p><a href="clay-cleaned.blend">Open clean clay Blender model</a> · <a href="reconstructed.blend">Open original reconstructed Blender model</a> · <a href="reconstruction.glb">Original GLB</a> · <a href="../../index.html">Object design library</a></p>
<article><h2>Input and actual Blender result</h2><div class="pair"><div><p>Generated reference</p><img src="../../croissant/design/front.png"></div><div><p>Reconstructed mesh with clay material</p><img src="cleaned/preview.png"></div></div></article>
<article><h2>Six-view comparison</h2><p>Top row: generated references. Middle: original reconstruction with inferred vertex colors. Bottom: the same reconstructed geometry with a flat clay material and light surface smoothing.</p><a href="comparison.jpg"><img src="comparison.jpg"></a></article>
<article><h2>What is still unverified</h2><ul>'''+''.join('<li>'+html.escape(x)+'</li>' for x in review['limitations'])+'''</ul><p>The original reconstruction and source images are preserved. No published guide was changed by this experiment.</p></article></html>'''
    (OUT/'index.html').write_text(text)
    status=ROOT/'rollout-status.json';d=json.loads(status.read_text());d['stage']='local_triposr_trial_completed';d['local_trial']='reconstruction-trial/croissant-triposr/index.html';d['local_trial_faces']=report['faces'];d['next_action']='Assess reference fidelity before choosing local reconstruction for the wider prop and character rollout.';status.write_text(json.dumps(d,indent=2)+'\n')
    print('TRIAL_REVIEW_READY',str(OUT/'index.html'))

if __name__=='__main__':run()
