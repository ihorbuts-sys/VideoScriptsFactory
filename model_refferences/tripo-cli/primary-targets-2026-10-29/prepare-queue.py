"""Prepare downloaded targets serially; native render jobs never overlap."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parents[2]
TOOLS=BASE/'model_refferences/objects/tools'
sys.path.insert(0,str(TOOLS))
from hologram_ghost import render
import primary_target_gallery as gallery
BLENDER='/Applications/Blender.app/Contents/MacOS/Blender'
start=time.monotonic();complete=set()
while len(complete)<16:
 plan=json.loads((ROOT/'plan.json').read_text())
 for row in plan['objects']:
  aid=row['id'];folder=BASE/'model_refferences/objects'/aid/'tripo-generated';review=folder/'review'
  if aid in complete:continue
  sources=list((folder/'tripo-out').glob('*/model.glb'))
  if not sources:continue
  task=sources[0].parent/'task.json'
  if not task.exists() or json.loads(task.read_text()).get('status')!='success':continue
  if not (review/'native-ready.json').exists():
   with (ROOT/(aid+'-native.log')).open('w') as log:
    subprocess.run([BLENDER,'--background','--python-exit-code','1','--python',str(TOOLS/'prepare_primary_target.py'),'--',aid],stdout=log,stderr=subprocess.STDOUT,check=True)
  component=json.loads((review/'component.json').read_text())
  for name,data in component['files'].items():assert hashlib.sha256((review/name).read_bytes()).hexdigest()==data['sha256'],(aid,name)
  with Image.open(review/'overlay-fields.png') as fields,Image.open(review/'overlay-mask.png') as mask:
   image=render(fields,np.array(mask.convert('RGBA')),0,opacity=1,solid_surfaces=True)
  assert image.getchannel('A').getextrema()==(0,255)
  image.save(review/'ghost-preview.png')
  component['files']['ghost-preview.png']=dict(bytes=(review/'ghost-preview.png').stat().st_size,sha256=hashlib.sha256((review/'ghost-preview.png').read_bytes()).hexdigest())
  component.update(static_overlay_preview=True,animation_embedded=False,preview_alpha_factor=1,image_view_opacity=.65)
  (review/'component.json').write_text(json.dumps(component,indent=2)+'\n')
  row['status']='native_ready_for_visual_review';row['actual_credits']=component['credits_consumed']
  (ROOT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
  complete.add(aid);gallery.run();print('PRIMARY_TARGET_PREPARED',aid,len(complete),16,flush=True)
 assert time.monotonic()-start<7200,'Generation or native preparation did not finish'
 if len(complete)<16:time.sleep(3)
print('PRIMARY_TARGET_PREPARATION_COMPLETE',flush=True)
