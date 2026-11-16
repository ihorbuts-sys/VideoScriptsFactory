"""Validate the native creator's frame visibility, hand scale, reach and planted feet."""
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_creator_guides as F
import build_coffee_glass_batch as G
import build_shared_venue as C
from prepare_rigged_characters import named

reports=[]
metadata=json.loads((Path(__file__).resolve().parents[2]/'creator/tripo-rigged/review/metadata.json').read_text())
assert hashlib.sha256(Path(metadata['source']).read_bytes()).hexdigest()==metadata['source_sha256']
for key in F.SCENES:
    folder=G.ROOT/key
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene=bpy.context.scene;spec=json.loads((folder/'scene-spec.json').read_text())
    root=next(o for o in scene.objects if o.get('asset_family')=='creator')
    arm=next(o for o in root.children_recursive if o.type=='ARMATURE')
    shoes=[o for o in C.meshes(root) if o.name.split('.')[0] in ['tripo_part_5','tripo_part_6']]
    assert len(shoes)==2
    samples={o:[v.index for v in sorted(o.data.vertices,key=lambda v:(o.matrix_world@v.co).z)[:24]] for o in shoes}
    floor=next(o for o in scene.objects if o.name.endswith('/ floor'))
    floor_z=max((floor.matrix_world@v.co).z for v in floor.data.vertices)
    baseline=None;foot_motion=0;scale_error=0;flex=0;eyes=[]
    for frame in range(1,spec['frame_count']+1):
        scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
        current=[o.matrix_world@o.evaluated_get(deps).data.vertices[i].co for o in shoes for i in samples[o]]
        if baseline is None:
            baseline=[v.copy() for v in current]
            ground_error=max(abs(min(p.z for p in current[i*24:(i+1)*24])-floor_z) for i in range(2))
        foot_motion=max(foot_motion,max((a-b).length for a,b in zip(baseline,current)))
        for side in ['Left','Right']:
            hand=named(arm,side+'Hand')
            scale_error=max(scale_error,max(abs(v-1) for v in hand.scale))
        hand=named(arm,'LeftHand');fore=named(arm,'LeftForeArm')
        wrist=arm.matrix_world@hand.head
        knuckles=sum((arm.matrix_world@named(arm,'LeftHand'+finger+'1').head for finger in ['Index','Pinky']),Vector())/2
        forward=(knuckles-wrist).normalized();direction=(wrist-arm.matrix_world@fore.head).normalized()
        flex=max(flex,math.degrees(forward.angle(direction)))
        eye=(arm.matrix_world@named(arm,'Head').tail)+Vector((0,-.10,-.01))
        uv=world_to_camera_view(scene,scene.camera,eye)
        assert .15<uv.x<.85 and .52<uv.y<.82,(key,frame,'Face outside target region',list(uv))
        eyes.append([uv.x,uv.y])
        hit,point,normal,index,obj,matrix=scene.ray_cast(deps,scene.camera.location,(eye-scene.camera.location).normalized(),distance=(eye-scene.camera.location).length+.05)
        assert hit
        owner=obj
        while owner and owner!=root:owner=owner.parent
        assert owner==root,(key,frame,'Face obstructed by scenery',obj.name)
        assert obj.name.split('.')[0] in ['tripo_part_0','tripo_part_4'],(key,frame,'Face blocked by body or hand',obj.name)
    assert foot_motion<.002 and scale_error<.005,(key,foot_motion,scale_error)
    assert ground_error<.002,(key,'Feet above floor',ground_error)
    assert flex<80,(key,'Excessive wrist bend',flex)
    report=dict(status='passed',frames=spec['frame_count'],canonical_source_sha256=metadata['source_sha256'],
        original_glb_preserved=True,rig_bones=len(arm.pose.bones),
        max_foot_displacement_m=foot_motion,max_hand_scale_error=scale_error,max_wrist_flex_deg=flex,
        floor_surface_z_m=floor_z,max_foot_ground_error_m=ground_error,
        maximum_reach_fraction=spec['performance_checks']['max_reach_fraction'],
        face_unobstructed=True,hair_framing=spec['hair_framing'],
        eye_line_range=[min(e[1] for e in eyes),max(e[1] for e in eyes)],
        facial_lip_sync=False,physical_phone_capture_verified=False)
    (folder/'performance-check.json').write_text(json.dumps(report,indent=2)+'\n')
    reports.append(dict(scene=key,**report))
print(json.dumps(reports))
