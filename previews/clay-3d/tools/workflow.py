"""Single-writer bookkeeping, image normalization and contact-sheet assembly."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import argparse,fcntl,hashlib,html,json,shutil,os
ROOT=Path(__file__).resolve().parents[1]

def read():return json.loads((ROOT/'manifest.json').read_text())
def save(m):
 p=ROOT/'manifest.tmp.json';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(ROOT/'manifest.json')
def roots(m):return {e['stem']:e for e in m['entries'] if e['stem']==e['canonical_stem']}
def counts(m):return {s:sum(e['status']==s for e in m['entries']) for s in sorted({e['status'] for e in m['entries']})}
def record(args):
 with (ROOT/'.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);m=read();entry=roots(m)[args.stem]
  folder=ROOT/'originals'/args.stem;folder.mkdir(parents=True,exist_ok=True);attempt=len(entry['attempts'])+1
  source=Path(args.source);original=folder/f'attempt-{attempt:02d}.png';shutil.copy2(source,original)
  prompt=Path(args.prompt).read_text().strip() if args.prompt else entry['prompt']
  item=dict(original=str(original.relative_to(ROOT)),tool_source=str(source),status=args.status,review=args.reason or 'Pending visual review',prompt=prompt,reference_images=args.reference or [])
  entry['attempts'].append(item)
  if args.status!='rejected':
   with Image.open(original) as im:
    im=ImageOps.fit(ImageOps.exif_transpose(im).convert('RGB'),(1080,1920),Image.Resampling.LANCZOS)
    for e in m['entries']:
     if e['canonical_stem']!=args.stem:continue
     stem=e['stem'];im.save(ROOT/'assets'/f'{stem}.png',optimize=True);im.save(ROOT/'assets'/f'{stem}.jpg',quality=94,subsampling=0,optimize=True)
     e.update(art_direction=m.get('art_direction','soft-clay-v1'),status=args.status,source=str(original.relative_to(ROOT)),source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),actual_prompt=prompt,review=args.reason or 'Pending visual review')
   entry['prompt']=prompt
  save(m)
 print(json.dumps(dict(stem=args.stem,status=args.status,counts=counts(m))))
def review(args):
 with (ROOT/'.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);m=read()
  for e in m['entries']:
   if e['canonical_stem'] in args.stems:
    assert e.get('source');e.update(status='approved',review=args.reason)
  for stem in args.stems:roots(m)[stem]['attempts'][-1].update(status='approved',review=args.reason)
  save(m)
 print(json.dumps(dict(reviewed=len(args.stems),counts=counts(m))))
def sheet(stems,path,width=180,columns=7):
 available=[s for s in stems if (ROOT/'assets'/f'{s}.jpg').exists()]
 if not available:return
 height=round(width*16/9);gap=round(width/12);rows=(len(available)+columns-1)//columns
 out=Image.new('RGB',(columns*width+(columns+1)*gap,rows*height+(rows+1)*gap),'#10120f')
 mask=Image.new('L',(width,height));ImageDraw.Draw(mask).rounded_rectangle((0,0,width-1,height-1),radius=round(width*.09),fill=255)
 for i,stem in enumerate(available):
  im=Image.open(ROOT/'assets'/f'{stem}.jpg').resize((width,height),Image.Resampling.LANCZOS)
  out.paste(im,(gap+(i%columns)*(width+gap),gap+(i//columns)*(height+gap)),mask)
 out.save(path,quality=94,subsampling=0)
def report(args):
 m=read();groups={}
 live_message="The reviewed collection is published through the API." if m.get("publication",{}).get("api_published") else "The live API still uses the previous collection."
 for e in m['entries']:groups.setdefault(e['template'],[]).append(e)
 current=[e for e in m["entries"] if e.get("art_direction")==m.get("art_direction") and e["status"] in ["candidate","approved"]]
 cards=[]
 for tid,entries in groups.items():
  complete=[e for e in entries if e.get('source')]
  if not complete:continue
  sheet([e['stem'] for e in entries],ROOT/'contact-sheets'/f'{tid}.jpg',width=216,columns=len(entries))
  parts=[]
  for e in entries:
   if not e.get('source'):parts.append('<article><p>'+html.escape(e['title'])+'</p><p>Not generated yet</p></article>');continue
   parts.append(f'<article><img loading="lazy" src="assets/{e["stem"]}.jpg"><p>{html.escape(e["title"])}</p><small>{html.escape(e["status"])}</small></article>')
  cards.append(f'<section id="{tid}"><h2>{tid}</h2><a href="contact-sheets/{tid}.jpg">Contact sheet</a><div class="grid">'+''.join(parts)+'</div></section>')
 body='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Loca Camera plasticine step previews</title><style>body{background:#f8f5ee;color:#253d3b;font:15px/1.5 system-ui;margin:24px}main{max-width:1500px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,210px));gap:16px}img{width:100%;aspect-ratio:9/16;object-fit:cover;border-radius:18px}article p{margin:6px 0}small{color:#687c75}section{padding:24px 0;border-top:1px solid #d8ded5}a{color:#34777e}</style><main><h1>Plasticine step previews</h1>'''
 body+=f'<p>{len(current)} / {m["steps"]} step files have current plasticine revisions; {sum(e["status"]=="approved" for e in m["entries"])} visually approved. Earlier drafts are labelled needs_regeneration. Original artwork remains preserved; {live_message}</p><p><a href="collection.jpg">Collection contact sheet (includes earlier drafts)</a> · <a href="plasticine-collection.jpg">Current plasticine revisions</a> · <a href="prompts.md">Prompts</a> · <a href="manifest.json">Manifest</a></p>'+''.join(cards)+'</main></html>'
 (ROOT/'index.html').write_text(body)
 ordered=[e['stem'] for e in m['entries']];sheet(ordered,ROOT/'collection.jpg',width=144,columns=16)
 current=[e['stem'] for e in m['entries'] if e.get('art_direction')==m.get('art_direction') and e['status'] in ['approved','candidate']]
 sheet(current,ROOT/'plasticine-collection.jpg',width=180,columns=8)
 p=['# Plasticine generation prompts','','One full-bleed 9:16 illustration per canonical scene; shared aliases keep compatible filenames.','']
 for e in m['entries']:
  p.extend([f'## {e["stem"]}',f'Status: {e["status"]}. Canonical: `{e["canonical_stem"]}`.','',e.get('actual_prompt',e['prompt']),''])
 (ROOT/'prompts.md').write_text('\n'.join(p))
 print(json.dumps(dict(counts=counts(m),canonical_generated=sum(bool(e.get('source')) for e in roots(m).values()),current_revision_generated=sum(e.get('art_direction')==m.get('art_direction') and e['status'] in ['approved','candidate'] for e in roots(m).values()),canonical_total=len(roots(m)))))
def batch(args):
 m=read();by=roots(m);todo=[by[s] for s in args.stems] if args.stems else [by[s] for s in m['canonical_queue'] if not by[s].get('source') or by[s]['status']=='needs_regeneration']
 print(json.dumps([dict(stem=e['stem'],prompt=e['prompt'],template=e['template'],visitor_character=e.get('visitor_character','creator'),shot=e.get('render_shot',e.get('shot')),angle=e['source_plan']['angle'],framing=e['source_plan']['start'],direction=e['actual_direction']) for e in todo[:args.count]]))
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('record');a.add_argument('--stem',required=True);a.add_argument('--source',required=True);a.add_argument('--prompt');a.add_argument('--reference',action='append');a.add_argument('--status',choices=['candidate','approved','rejected'],default='candidate');a.add_argument('--reason')
 a=sub.add_parser('review');a.add_argument('stems',nargs='+');a.add_argument('--reason',required=True)
 a=sub.add_parser('batch');a.add_argument('--count',type=int,default=4);a.add_argument('--stems',nargs='*')
 sub.add_parser('report');args=p.parse_args();{'record':record,'review':review,'batch':batch,'report':report}[args.cmd](args)
