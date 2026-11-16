"""Check first-visible geometry along every native food-camera view ray."""
import bpy,json
from pathlib import Path
from mathutils import Vector
base=Path(__file__).resolve().parents[3]/'catalog/glass-rollout/coffee'
results=[]
for key in ['burger-hero','brunch-spread','dessert-orbit']:
 folder=base/key;spec=json.loads((folder/'scene-spec.json').read_text())
 bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.context.scene
 hits=[]
 for sample in spec['camera']['samples']:
  scene.frame_set(sample['frame']);start=Vector(sample['position']);target=Vector(sample['target'])
  hit,point,normal,index,obj,matrix=scene.ray_cast(bpy.context.evaluated_depsgraph_get(),start,(target-start).normalized(),distance=(target-start).length+.05)
  assert hit,(key,sample['frame'],'No physical subject')
  parent=obj;family=None
  while parent:
   if parent.get('asset_family'):family=parent['asset_family'];break
   parent=parent.parent
  allowed={'brunch_toast','dinner_plate','dining_table'} if key=='brunch-spread' else {'burger'} if key=='burger-hero' else {'cake_slice'}
  assert family in allowed,(key,sample['frame'],family,obj.name)
  assert (point-start).length>.12,(key,sample['frame'],'Lens too close to geometry')
  hits.append(dict(frame=sample['frame'],first_visible_asset=family,distance_m=(point-start).length))
 report=dict(status='passed',frames=len(hits),first_visible_assets=sorted({h['first_visible_asset'] for h in hits}),minimum_lens_clearance_m=min(h['distance_m'] for h in hits))
 (folder/'camera-visibility-check.json').write_text(json.dumps(report,indent=2)+'\n');results.append(dict(scene=key,**report))
print(json.dumps(results))
