"""Inspect all queued native scenes before accepting their rendered guide artifacts."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_place_settings import inspect as inspect_place_settings
BASE=Path(__file__).resolve().parents[2];OUT=BASE/'catalog/blender-animations'
ids=sys.argv[sys.argv.index('--')+1:];results=[]
if '--profile' in ids and ids[ids.index('--profile')+1]=='p0':
    from verify_p0_scene import run as verify_p0
    verify_p0()
    raise SystemExit(0)
if '--root' in ids:
    position=ids.index('--root');OUT=Path(ids[position+1]);ids=ids[:position]+ids[position+2:]
for gid in ids:
    folder=OUT/gid;spec=json.loads((folder/'scene-spec.json').read_text());errors=[]
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    place_settings=inspect_place_settings(scene)
    for row in place_settings:
        if row['too_central']:errors.append('Personal dish is too close to table centre: '+row['plate'])
    stages=[(round(s['t']*spec['fps'])+1,bpy.data.objects[s['name']]) for s in spec['camera_stages']]
    hands=[o for o in scene.objects if o.get('visible_hand_count')==1 and not any(c.get('visible_hand_count')==1 for c in o.children_recursive)]
    lights=[o for o in scene.objects if o.type=='LIGHT']
    if not lights or any(o.animation_data is not None or o.data.animation_data is not None for o in lights):errors.append('Lighting must stay fixed')
    positions={};travel={};maximum_hands=0;maximum_people=0;heights=[];body_motion=False;first={};hero_visible=0
    pitch=[];samples=[];quaternions={};maximum_angular_step=0
    heads=[o for o in scene.objects if o.type=="MESH" and o.name.startswith("Mouthless schematic head")]
    for f in range(1,min(scene.frame_end,spec.get("frame_count",scene.frame_end))+1):
        scene.frame_set(f);bpy.context.view_layer.update();camera=[c for start,c in stages if start<=f][-1]
        p=camera.matrix_world.translation.copy();heights.append(p.z)
        samples.append(list(p));q=camera.matrix_world.to_quaternion();forward=q@Vector((0,0,-1));pitch.append(math.degrees(math.atan2(forward.z,math.hypot(forward.x,forward.y))))
        if camera.name in quaternions:
            angle=math.degrees(q.rotation_difference(quaternions[camera.name]).angle)
            maximum_angular_step=max(maximum_angular_step,min(angle,360-angle))
        quaternions[camera.name]=q.copy()
        if camera.name in positions:travel[camera.name]=travel.get(camera.name,0)+(p-positions[camera.name]).length
        positions[camera.name]=p
        visible_people=0
        for head in heads:
            centre=sum((Vector(corner) for corner in head.bound_box),Vector())/8
            q=world_to_camera_view(scene,camera,head.matrix_world@centre)
            if -.05<q.x<1.05 and -.05<q.y<1.05 and q.z>camera.data.clip_start:visible_people+=1
        maximum_people=max(maximum_people,visible_people)
        visible=0
        for hand in hands:
            points=[world_to_camera_view(scene,camera,hand.matrix_world.translation)]
            points.extend(world_to_camera_view(scene,camera,obj.matrix_world.translation) for obj in hand.children_recursive if obj.type=='MESH')
            if any(-.03<q.x<1.03 and -.03<q.y<1.03 and q.z>camera.data.clip_start for q in points):visible+=1
        maximum_hands=max(maximum_hands,visible)
        if visible>2 and 'Too many visible hands' not in errors:errors.append('Too many visible hands')
        for obj in scene.objects:
            if obj.type!='MESH':continue
            matrix=tuple(round(v,5) for row in obj.matrix_world for v in row)
            if obj.name in first and matrix!=first[obj.name]:body_motion=True
            first.setdefault(obj.name,matrix)
            if obj.get('composition_role')=='hero' or obj.name in spec.get('framing_landmarks',[]):
                centre=sum((Vector(corner) for corner in obj.bound_box),Vector())/8
                point=world_to_camera_view(scene,camera,obj.matrix_world@centre)
                if -.05<point.x<1.05 and -.05<point.y<1.05 and point.z>0:hero_visible+=1
    if (BASE/"guides/blender_motion/people-policy.json").exists() and maximum_people:errors.append("Published range contains a deferred person")
    if max(heights)>2.01:errors.append('Phone rises above a reachable two-metre limit')
    if min(heights)<.12:errors.append('Phone path intersects the floor')
    feasibility=spec.get('mobile_feasibility',{})
    walk_bound=feasibility.get('max_walk_m',2.0) if isinstance(feasibility,dict) else 2.0
    if max(travel.values(),default=0)>walk_bound+.01:errors.append('Phone travel exceeds the reviewed ordinary walk')
    if not hero_visible:errors.append('Primary subject has no visible framing landmark')
    if any(c.data.animation_data for _,c in stages):errors.append('Lens must stay fixed')
    if len(spec.get('subject_actions',spec.get('composition',[])))<2:errors.append('Missing action/context explanation')
    chair_checks=[]
    for chair in [obj for obj in scene.objects if obj.get('dining_table_root')]:
        table=bpy.data.objects[chair['dining_table_root']]
        back=next(obj for obj in chair.children_recursive if obj.name.startswith('Dining chair bent back'))
        centre=sum((Vector(v) for v in back.bound_box),Vector())/8
        back_offset=(back.matrix_world@centre-chair.matrix_world.translation).xy
        to_table=(table.matrix_world.translation-chair.matrix_world.translation).xy
        alignment=back_offset.normalized().dot(to_table.normalized())
        chair_checks.append(dict(chair=chair.name,table=table.name,backrest_alignment_toward_table=alignment,facing_table=alignment<-.95))
        if alignment>=-.95:errors.append('Dining chair faces away from its table: '+chair.name)
    facts=dict(id=gid,status='failed' if errors else 'passed',errors=errors,maximum_visible_hands=maximum_hands,maximum_visible_people=maximum_people,
               pitch_range_deg=[min(pitch),max(pitch)],translation_range_xyz_m=[max(p[i] for p in samples)-min(p[i] for p in samples) for i in range(3)],maximum_angular_step_deg=maximum_angular_step,
               camera_height_range_m=[min(heights),max(heights)],camera_travel_per_take_m=travel,
               camera_lens_mm=[c.data.lens for _,c in stages],lighting_fixed=True,subject_geometry_moves=body_motion,
               physical_contacts_at_start=spec.get('physical_contact_checks',[]),scope=spec.get('scope'),
               dining_chairs=chair_checks,
               dining_place_settings=place_settings,
               source_adaptations=spec.get('source_adaptations',[]),source_review=spec['pre_render_review'])
    (folder/'geometry-checks.json').write_text(json.dumps(facts,indent=2)+'\n');results.append(facts)
    print('SCENE_AUDIT',gid,facts['status'],errors,flush=True)
aggregate=OUT/'rollout-geometry-checks.json'
previous=json.loads(aggregate.read_text()) if aggregate.exists() else []
by_id={row['id']:row for row in previous}
by_id.update({row['id']:row for row in results})
aggregate.write_text(json.dumps(list(by_id.values()),indent=2)+'\n')
if any(r['errors'] for r in results):sys.exit(1)
