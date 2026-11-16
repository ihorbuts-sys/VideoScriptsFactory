"""Preserve generated modeling sheets and separate their six orthographic requests."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
VIEWS=['front','back','left','right','top','bottom']

def record(asset,source,prompt):
    out=ROOT/asset/'design';out.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,out/'sheet.png')
    image=Image.open(out/'sheet.png');w,h=image.size
    for i,name in enumerate(VIEWS):
        box=(round((i%3)*w/3),round((i//3)*h/2),round((i%3+1)*w/3),round((i//3+1)*h/2))
        image.crop(box).save(out/(name+'.png'))
    (out/'prompt.txt').write_text(prompt+'\n')
    (out/'provenance.json').write_text(json.dumps(dict(tool='built-in image_gen',source=source,
        sha256=hashlib.sha256((out/'sheet.png').read_bytes()).hexdigest(),views=VIEWS,
        status='generated_design_reference',limitation='AI views are design guidance, not measured geometry. Model-rendered projections are stored separately.'),indent=2)+'\n')
    print(json.dumps(dict(asset=asset,sheet=str(out/'sheet.png'),views=6)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('asset');p.add_argument('source');p.add_argument('prompt');a=p.parse_args()
    record(a.asset,a.source,a.prompt)
