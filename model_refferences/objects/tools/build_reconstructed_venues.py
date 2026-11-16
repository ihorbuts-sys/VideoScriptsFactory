"""Continuous phone-camera venue guides built from reviewed reconstructed assets."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_reconstructed_scene as C
P=C.P

def ease(t,a,b):
    u=max(0,min(1,(t-a)/(b-a)))
    return .5-.5*math.cos(math.pi*u)

def role(root,fill,line,frame=None):
    linear=lambda v:v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    for obj in C.meshes(root):
        obj.color=(linear(fill),linear(line),0,1)
        if frame is not None:obj.keyframe_insert('color',frame=frame)

def bar():
    gid='bar_low_truckr_mm';C.OUT=C.BASE/'catalog/clay-scenes'/gid;C.FPS=15;C.COUNT=180
    C.OUT.mkdir(parents=True,exist_ok=True)
    P.clear();scene=bpy.context.scene;P.studio(scene)
    scene.name='Loca clay bar / one continuous public-side camera'
    scene.render.resolution_x=540;scene.render.resolution_y=960
    scene.render.fps=C.FPS;scene.frame_start=1;scene.frame_end=C.COUNT
    scene['static_geometry']=True
    counter=C.instance('bar_counter',(-.65,.55,0),role='hero')
    counter_objects=[counter];bottles=[];contacts=[]
    for x in [-1.45,-.65,.15]:
        stool=C.instance('bar_stool',(x,-.32,0),math.pi,role='background')
        counter_objects.append(stool)
    for z in [1.17,1.70]:
        for x in [-1.25,-.05]:
            shelf=C.instance('wall_shelf',(x,1.28,z),role='support')
            counter_objects.append(shelf)
            for dx in [-.43,-.14,.15,.44]:
                px=x+dx;py=1.24;support=C.surface_z(shelf,px,py,from_z=z+.35)
                bottle=C.instance('bottle',(px,py,support),role='support');bottles.append(bottle)
                contacts.append(dict(asset='bottle',position=[px,py,support],support='shelf',error_m=0))
    # Customer-side drinks remain attached to their actual counter support.
    for px in [-1.05,-.25]:
        py=.28;support=C.surface_z(counter,px,py)
        glass=C.instance('drinking_glass',(px,py,support),role='support');counter_objects.append(glass)
        contacts.append(dict(asset='drinking_glass',position=[px,py,support],support='bar_counter',error_m=0))
    tx,ty=1.8,-.65
    table=C.instance('dining_table',(tx,ty,0),role='background')
    chairs=[C.instance('dining_chair',(tx,ty-.74,0),math.pi),C.instance('dining_chair',(tx,ty+.74,0))]
    table_objects=[table,*chairs];drinks=[]
    # Two usable opposite place settings; the table centre remains clear.
    for dx,dy in [(-.18,-.19),(.18,.19)]:
        px,py=tx+dx,ty+dy;support=C.surface_z(table,px,py)
        drink=C.instance('drinking_glass',(px,py,support),role='background');drinks.append(drink)
        contacts.append(dict(asset='drinking_glass',position=[px,py,support],support='dining_table',off_centre=True,error_m=0))
    # A second quiet setting makes the turn read as one shared public interior.
    quiet=C.instance('dining_table',(2.65,.15,0));C.instance('dining_chair',(2.65,-.59,0),math.pi)
    C.instance('dining_chair',(2.65,.89,0))
    floor=P.block('Color-only / quiet floor',(0,0,-.035),(9,8,.06),'cream',.02)
    floor.color=(0,0,0,1);floor['ghost_role']='absent'
    wall=P.block('Color-only / shelf support',(0,1.55,1.32),(5,.09,2.64),'cream',.02)
    wall.color=(0,0,0,1);wall['ghost_role']='absent'
    # These fixed sources reveal clay curvature during camera motion.
    P.lighting(Vector((.25,-.45,1.05)),2.2)
    data=bpy.data.cameras.new('Phone / truck, lift, turn and approach')
    camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
    data.sensor_fit='VERTICAL';data.sensor_height=36;data.lens=32
    start=Vector((-.85,-.95,1.18));truck=Vector((-.25,-.95,1.18))
    aisle=Vector((.65,-1.65,1.60));end=Vector((1.10,-1.75,1.65));target=Vector((tx,ty,.81))
    samples=[];previous=None;max_speed=0;max_angular_speed=0;previous_rotation=None
    for frame in range(1,C.COUNT+1):
        t=(frame-1)/C.FPS
        u=ease(t,1.2,3.0);v=ease(t,4,8.3);w=ease(t,8.3,10.7)
        position=start.lerp(truck,u).lerp(aisle,v).lerp(end,w)
        forward=Vector((0,1,.23)).normalized().to_track_quat('-Z','Y')
        destination=(target-position).to_track_quat('-Z','Y')
        rotation=forward.slerp(destination,ease(t,4.15,7.1))
        camera.location=position;camera.rotation_mode='QUATERNION';camera.rotation_quaternion=rotation
        camera.keyframe_insert('location',frame=frame);camera.keyframe_insert('rotation_quaternion',frame=frame)
        # Shift overlay emphasis with the action, without changing scene geometry.
        for obj in [counter,*bottles]:role(obj,.25*(1-v)+.04*v,1*(1-v)+.18*v,frame)
        for obj in table_objects:role(obj,.04*(1-v)+.17*v,.20*(1-v)+.68*v,frame)
        for obj in drinks:role(obj,.04*(1-v)+.25*v,.20*(1-v)+1*v,frame)
        if previous is not None:max_speed=max(max_speed,(position-previous).length*C.FPS)
        if previous_rotation is not None:max_angular_speed=max(max_angular_speed,previous_rotation.rotation_difference(rotation).angle*C.FPS)
        previous=position;previous_rotation=rotation
        assert position.y<-.85,'Camera must stay on the public side of the counter'
        samples.append(dict(frame=frame,time_s=round(t,4),position=list(position),quaternion=list(rotation)))
    for obj in [camera,*[o for o in scene.objects if o.animation_data]]:
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves if hasattr(obj.animation_data.action,'fcurves') else []:
                for point in fcurve.keyframe_points:point.interpolation='LINEAR'
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(C.OUT/'scene.blend'),compress=True)
    spec=dict(id=gid,status='proof_render_pending',method='one shared Blender interior assembled from local image-driven reconstructions',
        frame_count=C.COUNT,fps=C.FPS,duration_s=C.COUNT/C.FPS,scope='shot_and_handover',handover_status='included',
        source_description=json.loads((C.BASE/'guides/templates'/f'{gid}.json').read_text())['description'],
        next_guide='table_seat_high_in_mc',transition_method='one_camera_shared_interior',take_end_s=4,
        phases=[dict(start_s=0,end_s=4,action='Low counter-height truck right from the visitor side'),
                dict(start_s=4,end_s=8.3,action='Lift and turn through the same public aisle'),
                dict(start_s=8.3,end_s=12,action='Approach a high oblique view of the same best table and settle')],
        composition=['Counter edge and bottle rhythm lead into the aisle','Chairs face the table with real sitting clearance',
                     'Two drinks occupy opposite off-centre settings','Ghost emphasis transfers from counter to destination without a scene cut'],
        assets=['bar_counter','bar_stool','wall_shelf','bottle','drinking_glass','dining_table','dining_chair'],
        contacts=contacts,lighting='Fixed broad window-style soft light; no bloom, no animated practicals',
        camera=dict(lens_mm=32,max_speed_m_s=max_speed,max_angular_speed_deg_s=math.degrees(max_angular_speed),samples=samples),
        mobile='Slow lateral phone move, standing-height lift, turn and one step backwards in a public aisle',
        render_variants=['full_color','transparent_ghost'],ghost=dict(whole_overlay_alpha=.65,wall_alpha=0,viewfinder_embedded=False),
        probe_frames=[1,46,61,91,121,150,180],published=False)
    (C.OUT/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    return scene

if __name__=='__main__':
    scene=bar();C.render(scene,'--probes' in sys.argv,[1,46,61,91,121,150,180],list(range(1,61)) if '--refresh-take' in sys.argv else None)
