"""Independently inspect saved character skinning, grips and camera placement."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'guides/tools'));sys.path.insert(0,str(ROOT/'model_refferences/objects/tools'))
import p0_catalog
from prepare_rigged_characters import named


def world_vertices(obj):
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    points=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',points)
    matrix=np.array(evaluated.matrix_world);points=points.reshape(-1,3)@matrix[:3,:3].T+matrix[:3,3]
    evaluated.to_mesh_clear();return points


def run():
    source=ROOT/'model_refferences/creator/lineart/metadata.json';prepared=json.loads(source.read_text())
    assert hashlib.sha256((ROOT/prepared['source']).read_bytes()).hexdigest()==prepared['source_sha256']
    results=[]
    for record in p0_catalog.registry()['guides']:
        if not record.get('allowedPeople') or record.get('availability')=='archived':continue
        folder=ROOT/'catalog/p0/animations-light'/record['id'];meta=json.loads((folder/'meta.json').read_text())
        bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.context.scene
        rigs=[o for o in scene.objects if o.type=='ARMATURE'];assert len(rigs)==1
        arm=rigs[0];skin=next(o for o in scene.objects if o.type=='MESH' and o.name.startswith('Canonical creator continuous'))
        assert any(m.type=='ARMATURE' and m.object==arm and m.show_viewport and m.show_render for m in skin.modifiers)
        assert not any(o.get('p0_hand') for o in scene.objects),'No detached replacement hands'
        assert len([b for b in arm.pose.bones if b.name.endswith(('LeftHand','RightHand'))])==2
        features=[o for o in scene.objects if o.get('p0_face_feature') and not o.get('p0_framing_mask')]
        assert features,'Actual texture-derived eye marks must be retained'
        group=skin.vertex_groups.get(named(arm,'LeftHand').name)
        indices=[v.index for v in skin.data.vertices if any(g.group==group.index and g.weight>.6 for g in v.groups)]
        assert indices
        samples=[s for s in meta['camera_samples'] if s['phase']=='demonstration']
        chosen=[samples[round((len(samples)-1)*q)] for q in [0,.2,.4,.5,.7,.9,1]]
        vertices=[];wrist_bends=[];contacts=[];face_distances=[];eye_heights=[];palm_facing=[];thumb_clearance=[]
        prop=next((o for o in scene.objects if o.get('p0_held_cup') or o.get('p0_held_fork')),None)
        plate_checks=None
        if record['id']=='verdict_high_plate':
            table=next(o for o in scene.objects if o.get('p0_verdict_table'))
            dish=next(o for o in scene.objects if o.get('p0_verdict_dish'))
            plate=next(o for o in dish.children_recursive if o.name.startswith('Plate with formed rim'))
            points=world_vertices(plate)
            assert np.max(np.linalg.norm(points[:,:2]-np.array(table.location[:2]),axis=1))<.34-.06
            assert abs(float(points[:,2].min())-1.095)<.001
            projected=[world_to_camera_view(scene,scene.camera,Vector(p)) for p in points]
            assert min(p.y for p in projected)>.34 and max(p.y for p in projected)<.72,'Dish must clear recording controls'
            assert min(p.x for p in projected)>.015 and max(p.x for p in projected)<.985,'Show the complete plate rim'
            plate_checks=dict(supported=True,off_center=True,rim_margin_6cm=True,clear_of_recording_controls=True,complete_rim_in_frame=True)
        for sample in chosen:
            scene.frame_set(sample['frame']);bpy.context.view_layer.update()
            points=world_vertices(skin);vertices.append(points[indices].copy())
            elbow=arm.matrix_world@named(arm,'LeftForeArm').head;wrist=arm.matrix_world@named(arm,'LeftHand').head
            index=arm.matrix_world@named(arm,'LeftHandIndex1').head;pinky=arm.matrix_world@named(arm,'LeftHandPinky1').head
            wrist_bends.append(math.degrees((wrist-elbow).angle((index+pinky)/2-wrist)))
            assert wrist_bends[-1]<=(45 if prop else 78),(record['id'],'Excessive wrist bend',wrist_bends[-1])
            camera=scene.camera.location;face=arm.matrix_world@named(arm,'Head').tail
            if not prop and .45<=sample['u']<=.6:
                forward=((index+pinky)/2-wrist).normalized();across=(index-pinky).normalized()
                normal=forward.cross(across).normalized()
                facing=normal.dot((camera-(index+pinky)/2).normalized());palm_facing.append(facing)
                assert facing>.4,(record['id'],'Palm is turned away from the camera',facing)
            face_distances.append((camera-face).length);eye_heights.append(camera.z-face.z)
            assert all(o.hide_render for o in scene.objects if o.type=='MESH')
            if prop:
                thumb=arm.matrix_world@named(arm,'LeftHandThumb3').tail
                index_pad=arm.matrix_world@named(arm,'LeftHandIndex2').tail
                web=(thumb+index_pad)/2
                if prop.get('p0_held_cup'):local=Vector((.081,.003,.096))*prop.scale.x
                else:local=Vector((0,.005,0))
                point=prop.matrix_world.translation+prop.rotation_euler.to_matrix()@local
                contacts.append((point-web).length)
                assert contacts[-1]<.002,(record['id'],'Grip detached from prop')
                forward=((index+pinky)/2-wrist).normalized();radial=(index-pinky).normalized()
                palm=forward.cross(radial).normalized()
                assert index.z>pinky.z+.025,(record['id'],'Index/thumb side is upside down')
                for finger in ['Index','Middle','Ring','Pinky']:
                    for joint in [1,2,3]:
                        bone=named(arm,'LeftHand'+finger+str(joint))
                        direction=(arm.matrix_world.to_3x3()@(bone.tail-bone.head)).normalized()
                        assert direction.dot(palm)>.05,(record['id'],finger,joint,'Finger bends away from palm')
                if prop.get('p0_held_cup'):
                    tip=arm.matrix_world@named(arm,'LeftHandIndex3').tail
                    thumb_clearance.append(thumb.z-tip.z)
                    assert thumb_clearance[-1]>.004,(record['id'],'Thumb must be above hooked index')
        motion=max(float(np.linalg.norm(p-vertices[0],axis=1).max()) for p in vertices)
        assert motion>.025,(record['id'],'Bones moved but the visible hand skin did not')
        if record['camera']=='front':
            assert max(face_distances)<.9 and meta['preview_mirrored']
            if record['id'] in ['sip_high_lean','verdict_high_plate']:assert min(eye_heights)>.12
            else:assert max(abs(h) for h in eye_heights)<.09
        else:assert .8<min(face_distances)<1.5 and not meta['preview_mirrored']
        results.append(dict(id=record['id'],status='passed',original_skinning_retained=True,
            actual_hand_skin_motion_m=motion,maximum_wrist_bend_degrees=max(wrist_bends),
            maximum_grip_error_m=max(contacts,default=0),camera=record['camera'],
            preview_mirrored=meta['preview_mirrored'],face_distance_m=[min(face_distances),max(face_distances)],
            lens_height_above_head_reference_m=[min(eye_heights),max(eye_heights)],eye_patch_meshes=len(features)))
        results[-1]['plate']=plate_checks
        if palm_facing:results[-1]['minimum_active_palm_camera_dot']=min(palm_facing)
        if prop:results[-1].update(positive_finger_flexion=True,index_side_upright=True,grip_style=prop['p0_grip_style'])
        if thumb_clearance:results[-1]['minimum_thumb_above_index_m']=min(thumb_clearance)
    report=dict(status='passed',guides=len(results),source_character_unchanged=True,records=results,
        facial_animation=False,physical_phone_tested=False,visual_anatomy_requires_owner_review=True)
    (ROOT/'catalog/p0/people-scene-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print('P0_PEOPLE_CHECKED',len(results),flush=True)


if __name__=='__main__':run()
