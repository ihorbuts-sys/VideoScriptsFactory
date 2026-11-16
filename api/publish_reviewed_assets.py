"""Publish a staged reviewed-animation refresh; no server source changes."""
import hashlib,json,os,shutil
from pathlib import Path
b=Path(__file__).resolve().parent.parent
stage=b/'api/bundle';live=Path('/Users/ihor.buts/Documents/Development/VideoEditorKit/tools/scriptwriter/catalog')
new=json.loads((stage/'catalog.json').read_text());old=json.loads((live/'catalog.json').read_text())
changed=[gid for gid,g in new['guides'].items() if g['sha256']!=old['guides'][gid]['sha256'] or g['scenario']!=old['guides'][gid]['scenario']]
policy=json.loads((b/'guides/blender_motion/people-policy.json').read_text()) if (b/'guides/blender_motion/people-policy.json').exists() else {}
original=json.loads((b/'api/pre-blender-catalog.json').read_text())
assert all(new['guides'][gid]['style']=='blender' or (gid in policy.get('deferred_guides',[]) and new['guides'][gid].get('sourceSha256',new['guides'][gid]['sha256'])==original['guides'][gid]['sha256']) for gid in changed)
backup=b/'api/pre-blender-catalog.json'
if not backup.exists():shutil.copy2(live/'catalog.json',backup)
for gid in changed:
 for key in ['overlay','poster','strip','scenario']:
  rel=new['guides'][gid][key];dst=live/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(stage/rel,dst)
  assert hashlib.sha256(dst.read_bytes()).digest()==hashlib.sha256((stage/rel).read_bytes()).digest()
  alias=live/dst.parent.parent.name/dst.name
  tmp=alias.with_name(alias.name+'.blender-tmp');tmp.unlink(missing_ok=True);os.link(dst,tmp);os.replace(tmp,alias)
# Publish each per-step context asset before switching the index. No flat aliases for variants.
context_files=0
for overrides in new.get('stepGuideOverrides',{}).values():
 for guide in overrides.values():
  for key in ['overlay','poster','strip']:
   rel=guide[key];dst=live/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists():shutil.copy2(stage/rel,dst)
   assert hashlib.sha256(dst.read_bytes()).digest()==hashlib.sha256((stage/rel).read_bytes()).digest()
   context_files+=1
for sequence in new.get('scriptGuideSequences',{}).values():
 for key in ['overlay','video','poster','strip']:
  rel=sequence[key];dst=live/rel;dst.parent.mkdir(parents=True,exist_ok=True)
  if not dst.exists():shutil.copy2(stage/rel,dst)
  assert hashlib.sha256(dst.read_bytes()).digest()==hashlib.sha256((stage/rel).read_bytes()).digest()
# Check every indexed asset before atomically switching the live catalog.
for g in new['guides'].values():
 for key in ['overlay','poster','strip','scenario','model3D']:assert (live/g[key]).exists(),g[key]
tmp=live/'catalog.blender-tmp';tmp.write_text(json.dumps(new,indent=1));os.replace(tmp,live/'catalog.json')
native=[gid for gid,g in new['guides'].items() if g['style']=='blender']
report=dict(changed_guides=changed,count=len(changed),blender_guides=native,total_blender_guides=len(native),live_catalog=str(live),server_source_changed=False,raw_transparent_assets=True,contextual_handovers='reviewed object handovers; people deferred')
(b/'api/blender-publication.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(changed_guides=len(changed),blender_guides=len(native),context_steps=len(new.get('stepGuideOverrides',{})),context_files=context_files,server_source_changed=False)))
