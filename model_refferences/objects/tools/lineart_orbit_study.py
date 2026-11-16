"""Smooth front-side cup orbits, reusing the generic native Line Art renderer."""
import argparse,hashlib,itertools,json,math,shutil,sys
from pathlib import Path
import bpy
import numpy as np
from mathutils import Quaternion,Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import lineart_render as L

PLAN={}
BASE_PREPARE=L.prepare_meshes


def smootherstep(u):
    u=max(0.,min(1.,u));return u*u*u*(10.+u*(-15.+6.*u))


def view(center,distance,pitch,yaw):
    position,rotation=L.pose(Vector(),distance,pitch)
    turn=Quaternion(Vector((0,0,1)),math.radians(yaw))
    return center+turn@position,turn@rotation


def add_coffee(meshes,args,options):
    before_lo,before_hi=L.evaluated_bounds(meshes)
    lo,hi,bevel=BASE_PREPARE(meshes)
    if not options.coffee:return lo,hi,bevel
    path=options.cup_metadata or args.model.parent/'metadata.json'
    data=json.loads(path.read_text());anchors=data['anchors']
    shift=Vector((-(before_lo.x+before_hi.x)/2,-(before_lo.y+before_hi.y)/2,-before_lo.z))
    rim=Vector(anchors['rim'])+shift;radius=anchors['radius']*.97;level=rim.z-options.coffee_clearance
    collection=meshes[0].users_collection[0]
    def link(obj,name):
        obj.name=name
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj);obj.data.materials.clear();meshes.append(obj)
        obj['coincident_vertices_welded']=0
        return obj
    # A real opaque surface closes the opening for native Line Art occlusion.
    # Its faces never reach the delivered PNG: all source meshes are hidden
    # after contour extraction by the base renderer.
    bpy.ops.mesh.primitive_cylinder_add(vertices=192,radius=radius,depth=.0004,
        location=(rim.x,rim.y,level-.0002))
    liquid=link(bpy.context.object,'Coffee / opaque surface below rim')
    foam=None
    if options.heart:
        points=[]
        for i in range(128):
            t=i*2*math.pi/128
            points.append((16*math.sin(t)**3,13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t)))
        xy=np.asarray(points);xy-=(xy.min(axis=0)+xy.max(axis=0))/2;xy*=radius*.76/(xy[:,0].max()-xy[:,0].min())
        mesh=bpy.data.meshes.new('Foam heart / raised silhouette')
        mesh.from_pydata([(rim.x+x,rim.y+y,level+.0002) for x,y in xy],[],[tuple(range(len(xy)))])
        mesh.update();foam=bpy.data.objects.new(mesh.name,mesh);collection.objects.link(foam);meshes.append(foam)
        foam['coincident_vertices_welded']=0
    bpy.context.view_layer.update()
    # Check the opening independently of the render: top rays through its
    # central 90% must land on coffee/foam, not on an intruding handle.
    hits=[]
    for dx in np.linspace(-.9,.9,15):
        for dy in np.linspace(-.9,.9,15):
            if dx*dx+dy*dy>.9**2:continue
            start=Vector((rim.x+dx*radius,rim.y+dy*radius,rim.z+.1))
            hit,point,normal,index,obj,matrix=bpy.context.scene.ray_cast(bpy.context.evaluated_depsgraph_get(),start,Vector((0,0,-1)),distance=.25)
            if not hit or obj not in [liquid,foam]:raise ValueError('Coffee does not fully cover the opening: '+str((dx,dy,obj.name if hit else None)))
            hits.append(obj.name)
    PLAN['coffee']=dict(enabled=True,heart=bool(foam),surface_z=level,rim_z=rim.z,radius=radius,
        clearance_m=options.coffee_clearance,metadata=str(path),opening_occlusion_rays=len(hits),opening_occlusion_check='passed',
        source_faces_rendered=False,heart_is_geometry=True)
    return *L.evaluated_bounds(meshes),bevel


def camera_setup(scene,args,lo,hi,options):
    data=bpy.data.cameras.new('Phone / smooth cup orbit');camera=bpy.data.objects.new('Phone camera',data)
    scene.collection.objects.link(camera);scene.camera=camera
    data.type='PERSP';data.lens=L.LENS[args.lens];data.sensor_fit='VERTICAL';data.sensor_width=data.sensor_height=36.
    data.clip_start=.001;data.clip_end=100
    center=(lo+hi)/2;fov_y=2*math.atan(36/(2*data.lens));tan_y=math.tan(fov_y/2);tan_x=tan_y*L.WIDTH/L.HEIGHT
    corners=[Vector(p) for p in itertools.product(*zip(lo,hi))]
    # Both versions share one distance, sized to the entire pitch/yaw envelope.
    # This avoids camera zoom/pumping while changing the viewing angle.
    distance=0.;min_focus=.15 if args.lens=='wide' else 0.
    for pitch in np.linspace(45-options.pitch_swing,45+options.pitch_swing,9):
        for yaw in np.linspace(-options.arc/2,options.arc/2,121):
            _,rotation=view(center,1.,float(pitch),float(yaw));right=rotation@Vector((1,0,0));up=rotation@Vector((0,1,0));back=rotation@Vector((0,0,1))
            for point in corners:
                relative=point-center;x=relative.dot(right);y=relative.dot(up);z=relative.dot(back)
                distance=max(distance,z+abs(x)/((1-2*options.margin)*tan_x),z+abs(y)/(L.FILL[args.size]*tan_y),z+min_focus)
    distance*=1.002
    count=1 if options.probe else round(args.duration*L.FPS)
    lead=0 if options.probe else round(options.lead_hold*L.FPS)
    hold=0 if options.probe else round(options.end_hold*L.FPS)
    motion_start=1+lead;motion_end=1 if options.probe else count-hold+1
    if not options.probe and motion_end-motion_start<60:raise ValueError('Allow at least two seconds for the actual orbit, in addition to the holds')
    scene.frame_start=1;scene.frame_end=count;camera.rotation_mode='QUATERNION'
    frames=[];previous=None
    for number in range(1,count+1):
        u=.5 if options.probe else max(0.,min(1.,(number-motion_start)/(motion_end-motion_start)))
        progress=smootherstep(u);yaw=-options.arc/2+options.arc*progress
        pitch=45.
        if options.profile=='cinematic':
            # Smooth pitch reversal spread over the whole move; zero velocity
            # and acceleration at both ends, with no pauses in the orbit.
            pitch-=options.pitch_swing*math.sin(2*math.pi*u)*math.sin(math.pi*u)**2/(3*math.sqrt(3)/8)
        position,rotation=view(center,distance,pitch,yaw)
        if previous and previous.dot(rotation)<0:rotation.negate()
        camera.location=position;camera.rotation_quaternion=rotation;previous=rotation.copy()
        if count>1:camera.keyframe_insert('location',frame=number);camera.keyframe_insert('rotation_quaternion',frame=number)
        scene.frame_set(number);bpy.context.view_layer.update()
        points=[world_to_camera_view(scene,camera,p) for p in corners]
        xs=[float(p.x) for p in points];ys=[float(p.y) for p in points]
        frames.append(dict(frame=number,time_s=(number-1)/L.FPS,camera_position=list(camera.matrix_world.translation),
            camera_rotation_quaternion=list(camera.matrix_world.to_quaternion()),camera_distance=distance,
            pitch_degrees=pitch,azimuth_degrees=yaw,trajectory_u=u,orbit_progress=progress,
            bbox_frame=dict(x_min=min(xs),x_max=max(xs),y_min=min(ys),y_max=max(ys)),bbox_frame_origin='bottom_left',
            height_fraction=max(ys)-min(ys),bbox_pixels_top_left=[min(xs)*L.WIDTH,(1-max(ys))*L.HEIGHT,max(xs)*L.WIDTH,(1-min(ys))*L.HEIGHT],
            fits_frame=min(xs)>=0 and max(xs)<=1 and min(ys)>=0 and max(ys)<=1))
    if camera.animation_data:
        action=camera.animation_data.action;curves=getattr(action,'fcurves',None)
        if curves is None:curves=[f for l in action.layers for s in l.strips for f in s.channelbag(camera.animation_data.action_slot).fcurves]
        for curve in curves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
    xyz=np.array([r['camera_position'] for r in frames]);velocity=np.diff(xyz,axis=0)*L.FPS
    speeds=np.linalg.norm(velocity,axis=1)
    turns=[]
    for a,b in zip(frames,frames[1:]):
        turns.append(math.degrees(Quaternion(a['camera_rotation_quaternion']).rotation_difference(Quaternion(b['camera_rotation_quaternion'])).angle)*L.FPS)
    if len(speeds):
        assert speeds.max()<.30,('Phone translation too fast',float(speeds.max()))
        assert max(turns)<45,('Phone turning too fast',max(turns))
    assert all(r['fits_frame'] for r in frames),'The cup must remain fully visible during this study'
    PLAN.update(profile=options.profile,arc_degrees=options.arc,pitch_swing_degrees=options.pitch_swing if options.profile=='cinematic' else 0,
        distance=distance,lead_hold_frames=lead,start_motion_frame=motion_start,end_motion_frame=motion_end,
        initial_drawing_hold_through=motion_start if not options.probe else 1,
        max_speed_m_s=float(speeds.max()) if len(speeds) else 0,max_turn_deg_s=max(turns) if turns else 0,
        pitch_range=[min(r['pitch_degrees'] for r in frames),max(r['pitch_degrees'] for r in frames)],
        camera_height_range=[min(r['camera_position'][2] for r in frames),max(r['camera_position'][2] for r in frames)],
        easing='quintic smootherstep for azimuth; smooth continuous pitch wave',safe_margin=options.margin,
        entire_front_side=True,probe=options.probe)
    return camera,center,distance,distance,fov_y,frames,motion_end,hold


def run():
    p=argparse.ArgumentParser(add_help=False)
    p.add_argument('--profile',choices=['steady','cinematic'],default='cinematic');p.add_argument('--arc',type=float,default=90.)
    p.add_argument('--pitch-swing',type=float,default=8.);p.add_argument('--lead-hold',type=float,default=.6);p.add_argument('--end-hold',type=float,default=.8)
    p.add_argument('--margin',type=float,default=.06);p.add_argument('--probe',action='store_true')
    p.add_argument('--coffee',action=argparse.BooleanOptionalAction,default=True);p.add_argument('--heart',action=argparse.BooleanOptionalAction,default=True)
    p.add_argument('--coffee-clearance',type=float,default=.0025);p.add_argument('--cup-metadata',type=Path)
    options,rest=p.parse_known_args(sys.argv[sys.argv.index('--')+1:])
    for flag,value in [('--angle','high'),('--size','medium'),('--move','orbit'),('--duration','8')]:
        if flag not in rest:rest += [flag,value]
    sys.argv=[sys.argv[0],'--',*rest];args=L.arguments()
    if args.angle!='high' or args.move!='orbit':raise ValueError('This study uses --angle high --move orbit')
    if not 0<options.arc<=120 or not 0<=options.pitch_swing<=15:raise ValueError('Use an arc in (0,120] and a pitch swing in [0,15]')
    if not 0<=options.margin<.3 or options.lead_hold<0 or options.end_hold<.5:raise ValueError('Invalid margin or hold durations')
    if not .001<=options.coffee_clearance<=.015:raise ValueError('Coffee clearance must be 1–15 mm below the rim')
    if options.probe:args.move='none'
    L.prepare_meshes=lambda meshes:add_coffee(meshes,args,options)
    L.camera_setup=lambda scene,args,lo,hi:camera_setup(scene,args,lo,hi,options)
    L.run(args)
    # Retain an identical opening alignment pose as well as the settled finish.
    lead=PLAN['initial_drawing_hold_through']
    for number in range(2,lead+1):shutil.copyfile(args.out/'frame_0001.png',args.out/f'frame_{number:04d}.png')
    obj=next(o for o in bpy.context.scene.objects if o.type=='GREASEPENCIL')
    for layer in obj.data.layers:
        for number in [f.frame_number for f in layer.frames if 1<f.frame_number<=lead]:layer.frames.remove(number)
    bpy.context.scene.frame_set(1);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(args.out/'scene.blend'),compress=True)
    path=args.out/'meta.json';meta=json.loads(path.read_text());meta.update(camera_profile=PLAN,
        profile_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),minimum_focus_limited=False,
        safe_zone_limited=True,framing_note='One fixed distance fits the entire yaw/pitch envelope, retaining the handle and a 6% horizontal margin. No lens zoom or object animation.')
    path.write_text(json.dumps(meta,indent=2)+'\n')
    print('CUP_ORBIT_READY',options.profile,len(meta['frames']),json.dumps(PLAN),flush=True)


if __name__=='__main__':
    try:run()
    except BaseException as error:
        print('CUP_ORBIT_ERROR',str(error),file=sys.stderr,flush=True)
        raise
