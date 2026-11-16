"""Catalog actual neural assets and their scene proofs separately from rejected proxies."""
import hashlib,html,json
from pathlib import Path
from PIL import Image,ImageDraw
from inventory import run as inventory
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parents[1]
PROPS=['croissant','croissant_oozing','dining_chair','dining_table','latte_cup','saucer','bar_counter','bar_stool','wall_shelf','bottle','drinking_glass','rack_shelf_tray','pastry_rack']
CHARACTERS=['barista','barista_head','creator','creator_head','friend_locs','friend_locs_head']
VIEWS=['front','back','left','right','top','bottom']

def build():
    inventory();cards=[];records=[]
    for asset in PROPS+CHARACTERS:
        out=ROOT/asset/'reconstructed';p=out/'metadata.json'
        if not p.exists():continue
        d=json.loads(p.read_text());sheet=Image.new('RGB',(1200,850),'#f7f2e7');draw=ImageDraw.Draw(sheet)
        for i,view in enumerate(VIEWS):
            f=out/(view+'.png');im=Image.open(f).convert('RGBA');im.thumbnail((400,400))
            bg=Image.new('RGBA',(400,400),'#f7f2e7');bg.alpha_composite(im,((400-im.width)//2,(400-im.height)//2))
            x=i%3*400;y=i//3*425;sheet.paste(bg.convert('RGB'),(x,y+25));draw.text((x+12,y+7),view.upper(),fill='#354839')
        sheet.save(out/'projections.jpg',quality=93)
        version=hashlib.sha256((out/'preview.png').read_bytes()).hexdigest()[:12]
        status='Unapproved character study: face fidelity, rig and hands need work; excluded from guide publication' if asset in CHARACTERS else 'Reviewed for scene proof'
        cards.append(f'<article><h2>{html.escape(asset.replace("_"," "))}</h2><p>{status}</p><div class="pair"><img src="{asset}/reconstructed/preview.png?v={version}" alt="{asset}"><img src="{asset}/reconstructed/projections.jpg?v={version}" alt="Six actual Blender projections"></div><p><a href="{asset}/reconstructed/model.blend">Open Blender model</a> · <a href="{asset}/reconstructed/asset.blend">Appendable asset</a> · <a href="{asset}/reconstructed/metadata.json">Provenance and dimensions</a></p></article>')
        records.append(dict(id=asset,status=status,path=str(out.relative_to(ROOT)),views=6,source_report=d['source_report']))
    style='body{font:16px system-ui;color:#293e32;background:#eee9dd;margin:24px auto;padding:0 20px;max-width:1250px}article{background:#fffaf0;border-radius:20px;padding:24px;margin:24px 0}.pair{display:grid;grid-template-columns:1fr 2fr;gap:20px}img{width:100%;height:auto;object-fit:contain}a{color:#34654d}p{line-height:1.5}@media(max-width:700px){.pair{grid-template-columns:1fr}}'
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Loca reconstructed asset library</title><style>'+style+'</style><h1>Image-driven clay assets</h1><p>Local neural reconstructions with six actual Blender projections. The modular rack reuses reconstructed trays and pastries with authored structural posts; its food remains independently editable. Source images and inferred meshes are preserved. Unseen surfaces are inferred from one input view. Failed monolithic rack and storefront trials are excluded.</p><p><a href="../../catalog/clay-scenes/index.html">Color and ghost scene previews</a> · <a href="inventory.md">Complete guide inventory</a> · <a href="index.html">Archived parametric prototypes</a></p>'+''.join(cards)+'</html>'
    if (BASE/'model_refferences/tripo-cli/index.html').exists():
        page=page.replace('<h1>Image-driven clay assets</h1>','<h1>Image-driven clay assets</h1><p><strong>New:</strong> <a href="../tripo-cli/index.html">Tripo barista, friend and dining-chair trials</a> · <a href="../creator/tripo-comparison/index.html">Imported creator comparison</a></p>',1)
    (ROOT/'reconstructed.html').write_text(page)
    manifest=dict(date='2026-10-28',method='local TripoSR',workflow_approved_by_owner=True,reconstructed_props=len([r for r in records if r['id'] in PROPS]),character_studies=len([r for r in records if r['id'] in CHARACTERS]),records=records)
    (ROOT/'reconstructed-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from scene_gallery import build as scene_gallery
    scene_gallery()
    print(json.dumps({k:manifest[k] for k in ['reconstructed_props','character_studies']}))

if __name__=='__main__':build()
