"""Check real evaluated contact geometry, actor reach, floor contact and clip continuity."""
import json,sys,math,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_creator_interactions as I
import build_shared_venue as C
import prepare_creator_tripo as B
from prepare_rigged_characters import named
from bpy_extras.object_utils import world_to_camera_view


def tree(root,handle=False):
    points=[];faces=[];inverse=root.matrix_world.inverted()
    for obj in C.meshes(root):
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        matrix=inverse@obj.matrix_world;offset=len(points)
        points += [matrix@v.co for v in mesh.vertices]
        for face in mesh.polygons:
            inds=[offset+i for i in face.vertices]
            if not handle or sum(points[i].x for i in inds)/len(inds)>.04:faces.append(inds)
        evaluated.to_mesh_clear()
    return BVHTree.FromPolygons(points,faces,all_triangles=False)


def run():
    results=[]
    for key in I.SCENES:
        folder=I.G.ROOT/key;bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
        scene=bpy.context.scene;spec=json.loads((folder/'scene-spec.json').read_text())
        actor=next(o for o in scene.objects if o.get('asset_family')=='creator')
        arm=next(o for o in actor.children_recursive if o.type=='ARMATURE')
        side='Right' if key=='creator-pastry-select' else 'Left'
        floor=next(o for o in scene.objects if o.name.endswith('/ floor'))
        floor_z=max((floor.matrix_world@v.co).z for v in floor.data.vertices)
        shoes=[o for o in C.meshes(actor) if o.name.split('.')[0] in ['tripo_part_5','tripo_part_6']]
        samples={o:[v.index for v in sorted(o.data.vertices,key=lambda v:(o.matrix_world@v.co).z)[:16]] for o in shoes}
        baseline=None;motion=scale_error=flex=reach=0;grounds=[];contact_rows=[];framing=[]
        if key=='creator-coffee-present':
            cup=next(o for o in scene.objects if o.get('asset_family')=='latte_cup' and o.location.y<2.5)
            handle=tree(cup,True);skin=[]
            for obj in C.meshes(actor):
                groups={g.index:g.name for g in obj.vertex_groups}
                for finger in ['Thumb','Index','Middle']:
                    ids=[v.index for v in obj.data.vertices if any(g.weight>.4 and side+'Hand'+finger in groups.get(g.group,'') for g in v.groups)]
                    if ids:skin.append((obj,finger,ids[::max(1,len(ids)//160)]))
        for frame,record in enumerate(spec['interaction_checks']['frames'],1):
            scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get()
            feet=[o.matrix_world@o.evaluated_get(deps).data.vertices[i].co for o in shoes for i in samples[o]]
            if baseline is None:
                baseline=[v.copy() for v in feet];grounds=[min(v.z for v in feet[n*16:(n+1)*16])-floor_z for n in range(2)]
            motion=max(motion,max((a-b).length for a,b in zip(feet,baseline)))
            for s in ['Left','Right']:
                hand=named(arm,s+'Hand');scale_error=max(scale_error,max(abs(v-1) for v in hand.scale))
            hand=named(arm,side+'Hand');fore=named(arm,side+'ForeArm');upper=named(arm,side+'Arm')
            wrist=arm.matrix_world@hand.head;shoulder=arm.matrix_world@upper.head
            length=(arm.matrix_world.to_3x3()@(upper.tail-upper.head)).length+(arm.matrix_world.to_3x3()@(fore.tail-fore.head)).length
            reach=max(reach,(wrist-shoulder).length/length)
            knuckles=sum((arm.matrix_world@named(arm,side+'Hand'+f+'1').head for f in ['Index','Pinky']),Vector())/2
            flex=max(flex,math.degrees((knuckles-wrist).angle(wrist-arm.matrix_world@fore.head)))
            if key=='creator-coffee-present' and record['phase']=='held' and frame%10==0:
                inverse=cup.matrix_world.inverted();distances={f:1 for f in ['Thumb','Index','Middle']}
                for obj,finger,ids in skin:
                    evaluated=obj.evaluated_get(deps)
                    for i in ids:
                        p=inverse@(obj.matrix_world@evaluated.data.vertices[i].co)
                        found=handle.find_nearest(p)
                        if found[0] is not None:distances[finger]=min(distances[finger],found[3])
                contact_rows.append(dict(frame=frame,handle_surface_distance_m=distances))
            elif key=='creator-pack-box' and record['phase']=='held' and frame%10==0:
                pastry=next(o for o in scene.objects if o.get('asset_family')=='croissant' and abs(o.location.x-record['pastry_position'][0])<.005 and abs(o.location.y-record['pastry_position'][1])<.005)
                tongs=next(o for o in scene.objects if o.get('asset_family')=='kitchen_tongs')
                bread=tree(pastry);to_bread=pastry.matrix_world.inverted();root_inverse=tongs.matrix_world.inverted();cal=spec['interaction_checks']['tongs_calibration']
                distances=[1.,1.]
                for obj in C.meshes(tongs):
                    evaluated=obj.evaluated_get(deps)
                    for i in range(0,len(obj.data.vertices),5):
                        original=root_inverse@(obj.matrix_world@obj.data.vertices[i].co)
                        if abs(original.y-cal['jaw_local'][1])>.035:continue
                        side_index=int(original.z>cal['grip_local'][2])
                        point=to_bread@(obj.matrix_world@evaluated.data.vertices[i].co)
                        found=bread.find_nearest(point)
                        if found[0] is not None:distances[side_index]=min(distances[side_index],found[3]*pastry.scale.x)
                contact_rows.append(dict(frame=frame,jaw_surface_distance_m=distances))
        report=dict(status='measured',frames=spec['frame_count'],max_foot_motion_m=motion,
            sole_to_floor_m=grounds,max_hand_scale_error=scale_error,max_wrist_flex_deg=flex,max_reach_fraction=reach,contact_samples=contact_rows)
        (folder/'interaction-review.json').write_text(json.dumps(report,indent=2)+'\n');results.append(dict(scene=key,**report))
        assert motion<.002 and scale_error<.005 and max(map(abs,grounds))<.002,(key,'Body contact',report)
        assert reach<1.001,(key,'Arm extended beyond length',reach)
        assert flex<80,(key,'Wrist bend',flex)
        if key=='creator-coffee-present':
            assert contact_rows
            for contact in contact_rows:
                d=contact['handle_surface_distance_m'];assert max(d['Index'],d['Middle'])<.004 and d['Thumb']<.012,(key,contact)
        if key=='creator-pack-box':
            assert contact_rows
            assert all(max(c['jaw_surface_distance_m'])<.006 for c in contact_rows),(key,contact_rows)
        report['status']='passed'
        results[-1]['status']='passed'
        (folder/'interaction-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(results))

if __name__=='__main__':run()
