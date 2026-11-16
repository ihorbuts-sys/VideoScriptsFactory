from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import argparse,json,shutil,hashlib,html
ROOT=Path(__file__).resolve().parents[1]
def read():return json.loads((ROOT/'manifest.json').read_text())
def save(m):
 p=ROOT/'manifest.tmp.json';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(ROOT/'manifest.json')
def batch(args):
 m=read();by={e['character']+'.'+e['view']:e for e in m['entries']};pending=[by[k] for k in m['queue'] if by[k]['status'] in ['pending','needs_regeneration']]
 fronts=[e for e in pending if e['view']=='front'];todo=fronts or pending[:args.count]
 for e in todo:
  e['references']=[e['source']]
  front=ROOT/e['character']/'front.png'
  if e['view']!='front' and hashlib.sha256(Path(e['source']).read_bytes()).hexdigest()!=hashlib.sha256(front.read_bytes()).hexdigest():e['references'].append(str(front))
 print(json.dumps(todo))
def record(args):
 m=read();e=next(e for e in m['entries'] if e['character']==args.character and e['view']==args.view);source=Path(args.source);folder=ROOT/args.character
 shutil.copy2(source,folder/'originals'/f'{args.view}.png');shutil.copy2(source,folder/f'{args.view}.png')
 e.setdefault('attempts',[]).append(dict(tool_source=str(source),status='candidate',prompt=e['prompt']))
 e.update(status='candidate',tool_source=str(source),file=f'{args.character}/{args.view}.png',sha256=hashlib.sha256(source.read_bytes()).hexdigest(),reference_images=[e['source']]+([str(folder/'front.png')] if args.view!='front' else []))
 save(m);print('MODEL_VIEW_SAVED',args.character,args.view)
def report(args):
 m=read();cards=[]
 for c in m['characters']:
  all_e=[e for e in m['entries'] if e['character']==c];frames=[]
  for e in all_e:
   if not e.get('file'):continue
   frames.append(e)
   cards.append(f'<figure><img src="{e["file"]}"><figcaption>{c}: {e["view"]}</figcaption></figure>')
  if frames:
   out=Image.new('RGB',(3*512,2*512),'#f4f1e8')
   for i,e in enumerate(frames):
    im=Image.open(ROOT/e['file']).convert('RGB');im=ImageOps.pad(im,(512,512),color='#f4f1e8');out.paste(im,((i%3)*512,(i//3)*512))
   out.save(ROOT/c/'contact-sheet.jpg',quality=96,subsampling=0)
 body='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca character references</title><style>body{font:16px/1.5 system-ui;background:#f5f2e9;color:#263b37;margin:24px}.grid{display:grid;grid-template-columns:repeat(3,minmax(160px,1fr));gap:20px;max-width:1500px}figure{margin:0}img{width:100%;aspect-ratio:1;object-fit:contain}a{color:#34777e}</style><h1>Character model references</h1><p>Front, back, anatomical left, anatomical right, top and bottom. Source images and prompts are preserved. Top/bottom are illustrative high/low views, not measured orthographic projections.</p><p><a href="creator/contact-sheet.jpg">Creator sheet</a> · <a href="barista/contact-sheet.jpg">Barista sheet</a> · <a href="friend_locs/contact-sheet.jpg">Locs friend sheet</a> · <a href="manifest.json">Provenance</a></p><div class="grid">'+''.join(cards)+'</div></html>'
 (ROOT/'index.html').write_text(body);print('MODEL_REFERENCE_PROGRESS',len(cards),m['total_views'])
if __name__=='__main__':
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
 a=s.add_parser('batch');a.add_argument('--count',type=int,default=5)
 a=s.add_parser('record');a.add_argument('--character',required=True);a.add_argument('--view',required=True);a.add_argument('--source',required=True)
 s.add_parser('report');a=p.parse_args();{'batch':batch,'record':record,'report':report}[a.cmd](a)
