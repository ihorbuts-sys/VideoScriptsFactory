"""Preserve a generated original, normalize the requested output size, record review."""
import argparse,hashlib,json,shutil
from pathlib import Path
from PIL import Image

def run(stem,source,review):
    root=Path(__file__).resolve().parent
    for name in ['originals','assets']:(root/name).mkdir(exist_ok=True)
    original=root/'originals'/(stem+'.png');asset=root/'assets'/(stem+'.jpg')
    if original.exists() and original.read_bytes()!=source.read_bytes():raise ValueError('Preserve existing original; use a versioned stem')
    shutil.copy2(source,original)
    with Image.open(source) as image:
        assert abs(image.width/image.height-9/16)<.01
        image.convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS).save(asset,quality=95)
    path=root/'generation-queue.json';data=json.loads(path.read_text());row=next(e for e in data['entries'] if e['stem']==stem)
    row.update(status='visually_reviewed',original=str(original.relative_to(root)),asset=str(asset.relative_to(root)),
        source_generated_image=str(source),review=review,sha256=hashlib.sha256(asset.read_bytes()).hexdigest())
    path.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps(dict(stem=stem,status=row['status'],path=str(asset))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--stem',required=True);p.add_argument('--source',required=True,type=Path);p.add_argument('--review',required=True)
    a=p.parse_args();run(a.stem,a.source,a.review)
