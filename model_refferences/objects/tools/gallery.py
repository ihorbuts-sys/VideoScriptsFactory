"""Reviewable object catalog; generated designs and actual model renders stay distinct."""
import hashlib,html,json
from pathlib import Path
from PIL import Image,ImageDraw
from inventory import run as inventory
ROOT=Path(__file__).resolve().parents[1]
VIEWS=['front','back','left','right','top','bottom']

def run():
    inventory();data=json.loads((ROOT/'inventory.json').read_text());cards=[];checks=[]
    for row in data['assets']:
        id=row['id'];out=ROOT/id
        meta=out/'metadata.json'
        if meta.exists():
            m=json.loads(meta.read_text());sheet=Image.new('RGB',(960,700),'#f7f2e7');d=ImageDraw.Draw(sheet)
            for i,v in enumerate(VIEWS):
                p=out/'rendered'/(v+'.png')
                if not p.exists():continue
                im=Image.open(p).convert('RGBA');im.load();alpha=im.getchannel('A')
                assert alpha.getextrema()[1]>0,(id,v,'Empty render')
                im.thumbnail((310,310));bg=Image.new('RGBA',im.size,'#f7f2e7');bg.alpha_composite(im)
                x=i%3*320;y=i//3*350
                sheet.paste(bg.convert('RGB'),(x+(320-im.width)//2,y+28));d.text((x+12,y+8),v.upper(),fill='#354839')
                checks.append(dict(asset=id,view=v,size=Image.open(p).size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),alpha_nonzero=True))
            sheet.save(out/'model-projections.jpg',quality=92)
            append_link=f' · <a href="{id}/asset.blend">Appendable asset</a>' if (out/'asset.blend').exists() else ''
            cards.append(f'<article><h2>{html.escape(id.replace("_"," "))}</h2><p><strong>{html.escape(m["status"])}</strong></p><a href="{id}/model.blend">Archived Blender draft</a>{append_link}<p>{html.escape(row["description"])}</p><h3>AI design reference</h3><img src="{id}/design/sheet.png" loading="lazy"><h3>Rejected native prototype projections</h3><img src="{id}/model-projections.jpg" loading="lazy"></article>')
        elif (out/'design/sheet.png').exists():cards.append(f'<article><h2>{html.escape(id)}</h2><p>Model pending</p><img src="{id}/design/sheet.png" loading="lazy"></article>')
    (ROOT/'verification.json').write_text(json.dumps(dict(rendered_views=len(checks),assets_with_models=len({c['asset'] for c in checks}),checks=checks),indent=2)+'\n')
    document='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Loca clay object library</title><style>body{font:16px system-ui;background:#eee9dd;color:#28392f;margin:24px auto;max-width:1200px;padding:0 20px}a{color:#30644f}article{background:#fffaf0;border-radius:20px;padding:24px;margin:24px 0}img{display:block;width:100%;height:auto;border-radius:10px}p{max-width:900px;line-height:1.5}h3{font-size:16px}</style><h1>Loca clay object library</h1><p><strong>The parametric models below are rejected: they do not follow the approved reference art closely enough. None has replaced a published guide.</strong> Saved generated designs will be used for an image-driven reconstruction trial. Full-color and 65% ghost renders remain required for future accepted scenes.</p><p><a href="inventory.md">Full guide-object inventory</a> · <a href="../index.html">Approved character references</a> · <a href="rollout-status.json">Rollout status</a></p>'+''.join(cards)+'</html>'
    (ROOT/'index.html').write_text(document)
    print('GALLERY',len(cards),'cards;',len(checks),'rendered orthographic views')

if __name__=='__main__':run()
