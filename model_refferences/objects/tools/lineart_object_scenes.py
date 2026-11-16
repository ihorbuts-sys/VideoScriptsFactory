"""Supported object assemblies and smooth phone moves, using native Line Art."""
import argparse
import hashlib
import itertools
import json
import math
import shutil
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector, Quaternion
from bpy_extras.object_utils import world_to_camera_view

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_shared_venue as C
import build_assets as P
import prepare_creator_tripo as B
import lineart_render as L
import lineart_orbit_study as O

SPECS = {
    'cup-saucer': dict(title='Coffee / cup on its saucer', arc=90, pitch=(45, 45),
        direction='Sit beside the cup. Keep the cup on its saucer and trace a short arc around it. Lower and raise the phone gently to show the heart without changing the lens.'),
    'coffee-pastry': dict(title='Coffee and pastry / rising diagonal', arc=50, pitch=(35, 60),
        direction='Leave the cup on its saucer beside the croissant on one tray. Begin low beside the pastry, then arc gently right while raising the phone to show the coffee heart. Keep both supported objects in the same take.'),
    'dessert': dict(title='Cake / descending arc', arc=50, pitch=(55, 35),
        direction='Keep the cake on its plate at your place setting. From a seated position trace a short arc left while lowering the phone slightly, moving from the top to the cake layers. Settle without changing the lens.'),
}
BASE_STROKES=L.strokes_setup
FRAGMENT_CHECKS={}


def clean_strokes(scene,collection,args,distance,fov_y,motion_end):
    """Drop only disconnected contours shorter than 12 screen pixels."""
    obj,counts=BASE_STROKES(scene,collection,args,distance,fov_y,motion_end)
    removed=0;kept=0;tan_y=math.tan(fov_y/2);tan_x=tan_y*L.WIDTH/L.HEIGHT
    for layer in obj.data.layers:
        counts[layer.name]=0
        for frame in layer.frames:
            scene.frame_set(frame.frame_number);bpy.context.view_layer.update()
            drawing=frame.drawing;attr=drawing.attributes.get('position')
            if attr is None:continue
            points=np.empty((len(attr.data),3),dtype=np.float32);attr.data.foreach_get('vector',points.ravel())
            transform=np.asarray(scene.camera.matrix_world.inverted()@obj.matrix_world,dtype=np.float64)
            xyz=points@transform[:3,:3].T+transform[:3,3]
            depth=np.maximum(-xyz[:,2],1e-7)
            pixels=np.column_stack((xyz[:,0]/depth*L.WIDTH/(2*tan_x),xyz[:,1]/depth*L.HEIGHT/(2*tan_y)))
            drop=[];start=0
            for index,stroke in enumerate(drawing.strokes):
                end=start+len(stroke.points)
                length=float(np.linalg.norm(np.diff(pixels[start:end],axis=0),axis=1).sum())
                if length<12:drop.append(index)
                start=end
            if drop:drawing.remove_strokes(indices=drop)
            removed+=len(drop);kept+=len(drawing.strokes);counts[layer.name]+=len(drawing.strokes)
    FRAGMENT_CHECKS.update(minimum_disconnected_stroke_length_px=12,removed_strokes=removed,retained_strokes=kept,
        source_geometry_changed=False,scope='Only disconnected short strokes; long contours and occlusion unchanged')
    obj.data.update_tag()
    return obj,counts


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def supported(root, support, contacts):
    """Seat a rigid prop using its actual lower patch and support mesh rays."""
    objects=C.meshes(root)
    points=np.array([tuple(o.matrix_world@v.co) for o in objects for v in o.data.vertices])
    patch=points[points[:,2] <= points[:,2].min()+.003]
    patch=patch[::max(1,len(patch)//160)]
    hits=[]
    for x,y,z in patch:
        try:level=C.surface(support,float(x),float(y))
        except AssertionError:continue
        hits.append((float(x),float(y),float(z),level))
    if len(hits)<min(8,len(patch)):
        raise ValueError('Insufficient supporting surface for '+root.name)
    shift=max(level-z for x,y,z,level in hits)+.0002
    root.location.z+=shift
    bpy.context.view_layer.update()
    gaps=[z+shift-level for x,y,z,level in hits]
    assert min(gaps)>=.000199 and min(gaps)<.000201
    assert max(gaps)<.008,('Object bridges the rim instead of sitting in the dish',root.name,max(gaps))
    assert len(hits)==len(patch),('Footprint extends beyond support',root.name)
    contacts.append(dict(object=root.get('asset_family'),support=support.get('asset_family'),
        sampled_footprint_points=len(hits),minimum_gap_m=min(gaps),maximum_patch_gap_m=max(gaps),
        contact_tolerance_m=.0002,all_sampled_points_supported=True))


def coffee(root):
    anchors=json.loads((P.ROOT/'latte_cup/functional/metadata.json').read_text())['anchors']
    rim=next(o for o in root.children_recursive if o.get('function')=='rim').matrix_world.translation.copy()
    radius=anchors['radius']*.97;level=rim.z-.0025
    bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=radius,depth=.0004,location=(rim.x,rim.y,level-.0002))
    disk=bpy.context.object;disk.name='Coffee / hides handle inside cup'
    xy=np.array([(16*math.sin(t)**3,13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)) for t in np.linspace(0,math.tau,128,endpoint=False)])
    xy-=(xy.min(axis=0)+xy.max(axis=0))/2
    xy*=radius*.76/np.ptp(xy[:,0])
    mesh=bpy.data.meshes.new('Foam heart')
    mesh.from_pydata([(rim.x+x,rim.y+y,level+.0002) for x,y in xy],[],[tuple(range(len(xy)))])
    mesh.update();heart=bpy.data.objects.new('Foam heart',mesh);bpy.context.scene.collection.objects.link(heart)
    for obj in [disk,heart]:
        world=obj.matrix_world.copy();obj.parent=root;obj.matrix_world=world
    bpy.context.view_layer.update()
    rays=0
    for x in np.linspace(-.9,.9,15):
        for y in np.linspace(-.9,.9,15):
            if x*x+y*y>.81:continue
            hit,p,n,i,obj,m=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),
                Vector((rim.x+x*radius,rim.y+y*radius,rim.z+.1)),Vector((0,0,-1)),distance=.25)
            assert hit and obj in [disk,heart],('Opening not covered',obj.name if hit else None)
            rays+=1
    return dict(heart=True,clearance_m=.0025,opening_occlusion_rays=rays,opening_covered=True)


def build(args):
    source=args.out/'assembly.blend'
    if source.exists():
        raise ValueError('Assembly already exists; use a new output directory')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    P.MATS.clear();C.CACHE.clear();contacts=[];sources=[]
    def load(aid,quality=None,position=(0,0,0),turn=0,scale=1):
        root=C.load(aid,position=position,quality=quality,turn=turn,scale=scale)
        path=P.BASE/root['source_file']
        sources.append(dict(id=aid,path=str(path),sha256=sha(path),instance_scale=scale))
        return root
    def cup_on(saucer,xy=(0,0)):
        cup=load('latte_cup','functional')
        rim=next(o for o in cup.children_recursive if o.get('function')=='rim').matrix_world.translation.copy()
        cup.location.x+=xy[0]-rim.x;cup.location.y+=xy[1]-rim.y
        bpy.context.view_layer.update();supported(cup,saucer,contacts)
        return cup
    filling=None
    if args.scene=='cup-saucer':
        saucer=load('saucer','local');cup=cup_on(saucer);filling=coffee(cup)
    elif args.scene=='coffee-pastry':
        tray=load('serving_tray')
        saucer=load('saucer','local',position=(.07,.075,0))
        supported(saucer,tray,contacts)
        cup=cup_on(saucer,(.07,.075));filling=coffee(cup)
        pastry=load('croissant','approved-v2',position=(-.07,-.075,0),turn=math.radians(20))
        supported(pastry,tray,contacts)
        cup_box=B.bounds(C.meshes(cup));pastry_box=B.bounds(C.meshes(pastry))
        # Cup and pastry must have separated plan-view bounding rectangles.
        assert cup_box[0].y>pastry_box[1].y or cup_box[0].x>pastry_box[1].x
    else:
        plate=load('dinner_plate')
        cake=load('cake_slice',position=(.004,.002,0),turn=math.radians(20),scale=.8)
        supported(cake,plate,contacts)
    # Retain evaluated mesh geometry only: no textures, lights, rigs or UI.
    deps=bpy.context.evaluated_depsgraph_get();copies=[];originals=list(bpy.data.objects)
    for obj in list(bpy.context.scene.objects):
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps)
        data=bpy.data.meshes.new_from_object(evaluated,depsgraph=deps)
        data.transform(evaluated.matrix_world);data.materials.clear()
        copy=bpy.data.objects.new(obj.name,data);copies.append(copy)
    for obj in originals:bpy.data.objects.remove(obj,do_unlink=True)
    for obj in copies:bpy.context.scene.collection.objects.link(obj)
    args.out.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(source),compress=True)
    report=dict(scene=args.scene,title=SPECS[args.scene]['title'],direction=SPECS[args.scene]['direction'],
        sources=sources,support_contacts=contacts,coffee=filling,credits_used=0,
        materials=0,assembly=str(source),assembly_sha256=sha(source),
        notes=['No table-centred staging: these are isolated supported place-setting objects.',
               'Walls, floor, hands and viewfinder are excluded.'])
    (args.out/'assembly.json').write_text(json.dumps(report,indent=2)+'\n')
    return source,report


def scene_camera(scene,args,lo,hi,options,spec):
    """C2 start/stop, fixed lens/radius, simultaneous height and yaw changes."""
    if options.scene=='cup-saucer':
        return O.camera_setup(scene,args,lo,hi,options)
    camera_data=bpy.data.cameras.new('Fixed-lens phone');camera=bpy.data.objects.new('Phone / short commercial arc',camera_data)
    scene.collection.objects.link(camera);scene.camera=camera;camera.rotation_mode='QUATERNION'
    camera_data.lens=24;camera_data.sensor_fit='VERTICAL';camera_data.sensor_width=camera_data.sensor_height=36
    camera_data.clip_start=.001;camera_data.clip_end=100
    center=(lo+hi)/2;corners=[Vector(p) for p in itertools.product(*zip(lo,hi))]
    fov=2*math.atan(36/48);tan_y=math.tan(fov/2);tan_x=tan_y*L.WIDTH/L.HEIGHT
    def pose(u,distance):
        u=O.smootherstep(u);pitch=spec['pitch'][0]+(spec['pitch'][1]-spec['pitch'][0])*u
        yaw=(-.5+u)*spec['arc']*(1 if options.scene=='coffee-pastry' else -1)
        position,rotation=O.view(center,distance,pitch,yaw)
        return position,rotation,pitch,yaw
    distance=0
    for u in np.linspace(0,1,241):
        _,rotation,_,_=pose(float(u),1)
        right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0));back=rotation@Vector((0,0,1))
        for point in corners:
            r=point-center;x,y,z=r.dot(right),r.dot(up),r.dot(back)
            distance=max(distance,z+abs(x)/(.88*tan_x),z+abs(y)/(.6*tan_y),z+.15)
    distance*=1.002
    count=1 if options.probe else round(args.duration*30)
    lead=18 if count>1 else 0;hold=24 if count>1 else 0;end=count-hold+1 if count>1 else 1
    scene.frame_start=1;scene.frame_end=count;rows=[];previous=None
    for number in range(1,count+1):
        u=.5 if options.probe else max(0,min(1,(number-1-lead)/(end-1-lead)))
        position,rotation,pitch,yaw=pose(u,distance)
        if previous is not None and previous.dot(rotation)<0:rotation.negate()
        previous=rotation.copy();camera.location=position;camera.rotation_quaternion=rotation
        if count>1:camera.keyframe_insert('location',frame=number);camera.keyframe_insert('rotation_quaternion',frame=number)
        scene.frame_set(number);bpy.context.view_layer.update()
        points=[world_to_camera_view(scene,camera,p) for p in corners];xs=[p.x for p in points];ys=[p.y for p in points]
        rows.append(dict(frame=number,time_s=(number-1)/30,camera_position=list(position),camera_rotation_quaternion=list(rotation),
            camera_distance=distance,pitch_degrees=pitch,azimuth_degrees=yaw,
            bbox_frame=dict(x_min=min(xs),x_max=max(xs),y_min=min(ys),y_max=max(ys)),bbox_frame_origin='bottom_left',
            bbox_pixels_top_left=[min(xs)*L.WIDTH,(1-max(ys))*L.HEIGHT,max(xs)*L.WIDTH,(1-min(ys))*L.HEIGHT],
            height_fraction=max(ys)-min(ys),fits_frame=min(xs)>=0 and max(xs)<=1 and min(ys)>=0 and max(ys)<=1))
    if camera.animation_data:
        for layer in camera.animation_data.action.layers:
            for strip in layer.strips:
                for fcurve in strip.channelbag(camera.animation_data.action_slot).fcurves:
                    for key in fcurve.keyframe_points:key.interpolation='LINEAR'
    assert all(r['fits_frame'] for r in rows)
    O.PLAN.update(profile=options.scene,initial_drawing_hold_through=lead+1 if count>1 else 1,
        distance=distance,pitch_range=sorted(spec['pitch']),arc_degrees=spec['arc'],safe_margin=.06,
        easing='Quintic smootherstep for simultaneous yaw and pitch; fixed lens and radius',
        end_motion_frame=end,lead_hold_frames=lead,final_hold_frames=hold)
    return camera,center,distance,distance,fov,rows,end,hold


def run():
    p=argparse.ArgumentParser()
    p.add_argument('--scene',choices=SPECS,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--profile',choices=['steady','cinematic'],default='cinematic')
    p.add_argument('--probe',action='store_true');p.add_argument('--duration',type=float,default=8)
    options=p.parse_args(sys.argv[sys.argv.index('--')+1:]);options.out=options.out.resolve()
    if options.duration<5:raise ValueError('Allow at least five seconds for a gentle arc')
    source,assembly=build(options)
    args=argparse.Namespace(model=source,out=options.out,angle='high',size='medium',lens='wide',
        move='none' if options.probe else 'orbit',duration=options.duration,hidden=False)
    options.arc=90;options.pitch_swing=8;options.lead_hold=.6;options.end_hold=.8;options.margin=.06
    L.camera_setup=lambda scene,a,lo,hi:scene_camera(scene,a,lo,hi,options,SPECS[options.scene])
    L.strokes_setup=clean_strokes
    L.run(args)
    lead=O.PLAN['initial_drawing_hold_through']
    for frame in range(2,lead+1):shutil.copyfile(options.out/'frame_0001.png',options.out/f'frame_{frame:04d}.png')
    gp=next(o for o in bpy.context.scene.objects if o.type=='GREASEPENCIL')
    for layer in gp.data.layers:
        for number in [f.frame_number for f in layer.frames if 1<f.frame_number<=lead]:layer.frames.remove(number)
    bpy.context.scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(options.out/'scene.blend'),compress=True)
    path=options.out/'meta.json';meta=json.loads(path.read_text())
    meta.update(assembly=assembly,camera_profile=O.PLAN,minimum_focus_limited=False,safe_zone_limited=True,
        contour_cleanup=FRAGMENT_CHECKS,
        profile_script_sha256=sha(Path(__file__)),framing_note='One fixed lens and radius fit every pose, with 6% horizontal margin.')
    path.write_text(json.dumps(meta,indent=2)+'\n')
    print('OBJECT_SCENE_READY',options.scene,options.profile,len(meta['frames']),flush=True)


if __name__=='__main__':
    try:run()
    except BaseException as error:
        print('OBJECT_SCENE_ERROR',str(error),file=sys.stderr,flush=True)
        raise
