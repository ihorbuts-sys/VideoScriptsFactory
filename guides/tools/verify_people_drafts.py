"""Hand-run of verify_p0_people's checks on draft scenes (that script reads only registry guides)."""
import json,math,sys
from pathlib import Path
import bpy,numpy as np
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
B=Path(sys.argv[-2]);ids=sys.argv[-1].split(',')
def wv(obj):
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    p=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',p)
    m=np.array(ev.matrix_world);p=p.reshape(-1,3)@m[:3,:3].T+m[:3,3];ev.to_mesh_clear();return p
def named(arm,s):return next(b for b in arm.pose.bones if b.name.split(':')[-1]==s)
out={}
for gid in ids:
    folder=B/gid/'render';meta=json.loads((folder/'meta.json').read_text());record=meta['record']
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));sc=bpy.context.scene
    rigs=[o for o in sc.objects if o.type=='ARMATURE'];assert len(rigs)==1;arm=rigs[0]
    skin=next(o for o in sc.objects if o.type=='MESH' and o.name.startswith('Canonical creator continuous'))
    r=dict(skinning=any(m.type=='ARMATURE' and m.object==arm and m.show_render for m in skin.modifiers),
           detached_hands=sum(1 for o in sc.objects if o.get('p0_hand')),
           hand_bones=len([b for b in arm.pose.bones if b.name.endswith(('LeftHand','RightHand'))]),
           eye_marks=len([o for o in sc.objects if o.get('p0_face_feature') and not o.get('p0_framing_mask')]))
    group=skin.vertex_groups.get(named(arm,'LeftHand').name)
    idx=[v.index for v in skin.data.vertices if any(g.group==group.index and g.weight>.6 for g in v.groups)]
    samples=[s for s in meta['camera_samples'] if s['phase']=='demonstration']
    chosen=[samples[round((len(samples)-1)*q)] for q in [0,.2,.4,.5,.7,.9,1]]
    prop=next((o for o in sc.objects if o.get('p0_held_cup') or o.get('p0_held_fork')),None)
    plate=next((o for o in sc.objects if o.get('p0_held_plate')),None)
    head=named(arm,'Head');eye_local=(arm.matrix_world@head.bone.matrix_local).inverted()@Vector((0.,-.145,1.483))
    verts=[];bends=[];contacts=[];facing=[];thumbs=[];flex_ok=True;index_up=True;cam_head=[];cam_eye=[];face_d=[];plate_rows=[]
    for s in chosen:
        sc.frame_set(s['frame']);bpy.context.view_layer.update()
        pts=wv(skin);verts.append(pts[idx].copy())
        elbow=arm.matrix_world@named(arm,'LeftForeArm').head;wrist=arm.matrix_world@named(arm,'LeftHand').head
        index=arm.matrix_world@named(arm,'LeftHandIndex1').head;pinky=arm.matrix_world@named(arm,'LeftHandPinky1').head
        bends.append(math.degrees((wrist-elbow).angle((index+pinky)/2-wrist)))
        cam=sc.camera.location;eye=arm.matrix_world@head.matrix@eye_local
        cam_head.append(cam.z-(arm.matrix_world@head.tail).z);cam_eye.append(cam.z-eye.z);face_d.append((cam-(arm.matrix_world@head.tail)).length)
        if not prop and not plate and .45<=s['u']<=.6:
            f=((index+pinky)/2-wrist).normalized();a=(index-pinky).normalized()
            facing.append(f.cross(a).normalized().dot((cam-(index+pinky)/2).normalized()))
        if prop:
            thumb=arm.matrix_world@named(arm,'LeftHandThumb3').tail;pad=arm.matrix_world@named(arm,'LeftHandIndex2').tail;web=(thumb+pad)/2
            local=Vector((.081,.003,.096))*prop.scale.x if prop.get('p0_held_cup') else Vector(prop.get('p0_grip_local',(0,.005,0)))
            point=prop.matrix_world.translation+prop.rotation_euler.to_matrix()@local;contacts.append((point-web).length)
            f=((index+pinky)/2-wrist).normalized();rad=(index-pinky).normalized();palm=f.cross(rad).normalized()
            index_up&=index.z>pinky.z+.025
            for fi in ['Index','Middle','Ring','Pinky']:
                for j in [1,2,3]:
                    b=named(arm,'LeftHand'+fi+str(j));d=(arm.matrix_world.to_3x3()@(b.tail-b.head)).normalized()
                    flex_ok&=d.dot(palm)>.05
            if prop.get('p0_held_cup'):thumbs.append(thumb.z-(arm.matrix_world@named(arm,'LeftHandIndex3').tail).z)
        if plate:
            pl=next(o for o in plate.children_recursive if o.name.startswith('Plate with formed rim'));pp=wv(pl)
            pr=[world_to_camera_view(sc,sc.camera,Vector(p)) for p in pp[::7]]
            hand=pts[[i for i in range(len(pts)) if i in set(idx)]] if False else None
            plate_rows.append(dict(y_from_top=[round(1-max(p.y for p in pr),3),round(1-min(p.y for p in pr),3)],x=[round(min(p.x for p in pr),3),round(max(p.x for p in pr),3)]))
    r.update(skin_motion_m=round(max(float(np.linalg.norm(p-verts[0],axis=1).max()) for p in verts),4),
             max_wrist_bend_deg=round(max(bends),1),wrist_bend_limit=45 if prop else 78,
             lens_minus_head_tail_m=[round(min(cam_head),3),round(max(cam_head),3)],lens_minus_eye_m=round(cam_eye[0],3),
             lens_to_head_tail_m=[round(min(face_d),3),round(max(face_d),3)],preview_mirrored=meta['preview_mirrored'])
    if prop:r.update(max_grip_error_m=round(max(contacts),5),index_side_up=bool(index_up),fingers_flex_to_palm=bool(flex_ok),grip=prop['p0_grip_style'])
    if thumbs:r['min_thumb_above_index_m']=round(min(thumbs),4)
    if facing:r['min_palm_camera_dot']=round(min(facing),3)
    if plate_rows:r['plate_in_frame']=plate_rows
    checks=[r['skinning'],r['detached_hands']==0,r['hand_bones']==2,r['eye_marks']>0,r['skin_motion_m']>.025,r['max_wrist_bend_deg']<=r['wrist_bend_limit']]
    if prop:checks+=[r['max_grip_error_m']<.002,r['index_side_up'],r['fingers_flex_to_palm']]
    if thumbs:checks.append(r['min_thumb_above_index_m']>.004)
    if facing:checks.append(r['min_palm_camera_dot']>.4)
    if record['camera']=='front':checks+=[max(face_d)<.9,meta['preview_mirrored']]
    else:checks+=[.8<min(face_d)<1.5,not meta['preview_mirrored']]
    r['passed']=all(checks);r['checks']=[bool(c) for c in checks]
    perf=[p for p in meta['performance_checks'] if 'seated' in p]
    r['table_or_seat_clash']=dict(arm_in_table_slab=max(p['seated']['arm_in_table_slab'] for p in perf),body_in_table_slab=max(p['seated']['body_in_table_slab'] for p in perf),
        leg_in_table_slab=max(p['seated']['leg_in_table_slab'] for p in perf))
    out[gid]=r;print('VERIFY',gid,json.dumps(r))
Path(sys.argv[-2]).joinpath('verify_people_drafts.json').write_text(json.dumps(out,indent=1)+'\n') if len(ids)>1 else None
