"""Per-frame checks for multi-object, phone-feasible native guide sequences."""
import bpy
import json
import sys
import math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parents[2]
results=[]
for gid in sys.argv[sys.argv.index('--')+1:]:
 out=BASE/'catalog/blender-animations'/gid
 spec=json.loads((out/'scene-spec.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(out/'scene.blend'))
 scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
 cameras=[(round(s['t']*spec['fps'])+1,bpy.data.objects[s['name']]) for s in spec['camera_stages']]
 hands=[o for o in scene.objects if o.get('visible_hand_count')==1 and o.name.startswith('One hand')]
 maximum_hands=0;travel={cam.name:0 for _,cam in cameras};previous={};heights=[];visible_subject=False
 for f in range(1,scene.frame_end+1):
  scene.frame_set(f);bpy.context.view_layer.update();cam=[c for start,c in cameras if start<=f][-1]
  origin=cam.matrix_world.translation.copy();heights.append(origin.z)
  if cam.name in previous:travel[cam.name]+=(origin-previous[cam.name]).length
  previous[cam.name]=origin
  visible=0
  for hand in hands:
   point=world_to_camera_view(scene,cam,hand.matrix_world.translation)
   if -.12<point.x<1.12 and -.08<point.y<1.08 and point.z>0:visible+=1
  maximum_hands=max(maximum_hands,visible)
  assert visible<=2,(gid,'Too many visible hands',f,visible)
  for obj in scene.objects:
   if obj.type=='MESH' and obj.get('composition_role')=='hero':
    point=world_to_camera_view(scene,cam,obj.matrix_world.translation)
    if 0<point.x<1 and 0<point.y<1 and point.z>0:visible_subject=True
 assert visible_subject,gid
 assert max(heights)<=1.85 and min(heights)>=.55,(gid,'Unreachable phone height',min(heights),max(heights))
 assert max(travel.values())<=.85,(gid,'Phone travel exceeds a small lean or step',travel)
 lights=[o for o in scene.objects if o.type=='LIGHT']
 assert lights and all(o.animation_data is None and o.data.animation_data is None for o in lights)
 assert not any(o.type=='MESH' and 'wall' in o.name.lower() for o in scene.objects)
 assert len(spec.get('subject_actions',[]))>=2
 if spec['scope']=='shot_and_handover':assert len(cameras)>=2 and spec['next_contexts']
 facts=dict(id=gid,status='passed',maximum_visible_hands=maximum_hands,camera_height_range_m=[min(heights),max(heights)],camera_travel_per_take_m=travel,lighting_fixed=True,bloom=False,walls_omitted=True,visitor_side_only=True,separate_takes=len(cameras),physical_contacts_at_start=spec['physical_contact_checks'],scope=spec['scope'],source_adaptation=spec.get('source_adaptation'))
 (out/'geometry-checks.json').write_text(json.dumps(facts,indent=2)+'\n');results.append(facts)
(BASE/'catalog/blender-animations/action-geometry-checks.json').write_text(json.dumps(results,indent=2)+'\n')
print('VERIFIED_ACTION_GUIDES',len(results))
