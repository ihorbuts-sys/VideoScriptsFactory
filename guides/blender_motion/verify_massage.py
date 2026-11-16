"""Check the actual massage mesh/contact and crop across every published frame."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
BASE=Path(__file__).resolve().parents[2];folder=BASE/'catalog/blender-animations/hands_during_top_hold';spec=json.loads((folder/'scene-spec.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
patch=bpy.data.objects['Cropped curved massage surface'];mesh=next(o for o in scene.objects if o.name.startswith('Anatomical massage hand'));cam=bpy.data.objects[spec['camera_stages'][0]['name']]
hand=mesh.parent;camera_matrices=[];hand_rotations=[];positions=[];skin_states=[];rows=[]
lowest=min(v.co.y for v in mesh.data.vertices);cut=[v for v in mesh.data.vertices if v.co.y<lowest+.001];vertices=[v for v in mesh.data.vertices if v.co.y>0]
for f in range(1,spec['frame_count']+1):
    scene.frame_set(f);bpy.context.view_layer.update();tree=BVHTree.FromObject(patch,bpy.context.evaluated_depsgraph_get());palm=[];gaps=[]
    for v in vertices:
        world=mesh.matrix_world@v.co;hit=tree.ray_cast(Vector((world.x,world.y,2)),Vector((0,0,-1)),2)[0]
        if hit:
            gap=world.z-hit.z;gaps.append(gap)
            if .015<v.co.y<.095 and abs(v.co.x)<.040:palm.append(gap)
    q=max(world_to_camera_view(scene,cam,mesh.matrix_world@v.co).y for v in cut)
    assert q<0,'Forearm end enters the picture'
    assert min(gaps)>-.0025,'The hand clips through the contact surface'
    assert abs(min(palm))<.003,'The palm loses contact'
    camera_matrices.append(tuple(round(v,7) for row in cam.matrix_world for v in row));hand_rotations.append(tuple(round(v,7) for v in hand.rotation_euler));positions.append(list(hand.matrix_world.translation));skin_states.append(tuple(key.value for key in patch.data.shape_keys.key_blocks)[1:])
    rows.append(dict(frame=f,minimum_hand_gap_m=min(gaps),minimum_palm_gap_m=min(palm),forearm_cut_max_y=q))
assert len(set(camera_matrices))==1 and len(set(hand_rotations))==1
assert max(p[1] for p in positions)-min(p[1] for p in positions)>.12
assert skin_states[0]==skin_states[-1] and all(abs(a-b)<1e-6 for a,b in zip(positions[0],positions[-1]))
assert max(max(state) for state in skin_states)>.9
result=dict(status='passed',frames_checked=spec['frame_count'],duration_seconds=spec['frame_count']/15,camera_locked=True,one_hand=True,full_body_model=False,forearm_end_outside_frame=True,stroke_translation_xyz_m=[max(p[i] for p in positions)-min(p[i] for p in positions) for i in range(3)],loop_closes=True,skin_pressure_deforms=True,contact_tolerance_m=.003,minimum_signed_hand_gap_m=min(r['minimum_hand_gap_m'] for r in rows),maximum_closest_palm_gap_m=max(r['minimum_palm_gap_m'] for r in rows),frame_checks=rows)
(folder/'massage-checks.json').write_text(json.dumps(result,indent=2)+'\n');print('MASSAGE_CHECKS_PASSED',spec['frame_count'],'frames',flush=True)
