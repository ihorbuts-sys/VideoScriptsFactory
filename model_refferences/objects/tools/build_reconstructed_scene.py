"""First filming proof assembled from reconstructed props, in color and ghost masks."""
import bpy,json,math,sys,shutil
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
ROOT=P.ROOT;BASE=ROOT.parents[1]
OUT=BASE/'catalog/clay-scenes/cup_eye_orbitr_cc'
FPS=15;COUNT=60
ASSET_CACHE={}

def instance(asset,position=(0,0,0),turn=0,role='background'):
    path=ROOT/asset/'reconstructed/asset.blend'
    if asset not in ASSET_CACHE:
        with bpy.data.libraries.load(str(path),link=False) as (source,destination):
            destination.collections=[source.collections[0]]
        collection=destination.collections[0];ASSET_CACHE[asset]=collection
    else:
        original=ASSET_CACHE[asset];collection=bpy.data.collections.new(original.name+' instance')
        clones={o:o.copy() for o in original.objects}
        for original_object,clone in clones.items():
            collection.objects.link(clone)
            if original_object.parent in clones:clone.parent=clones[original_object.parent]
    bpy.context.scene.collection.children.link(collection)
    root=next(o for o in collection.objects if o.get('asset_id')==asset)
    root.location=position;root.rotation_euler.z=turn
    role_values={'hero':(.25,1),'support':(.17,.68),'background':(.05,.25)}
    fill,line=role_values[role]
    linear=lambda x:x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
    for o in root.children_recursive:
        if o.type=='MESH':
            o['ghost_role']=role;o.color=(linear(fill),linear(line),0,1)
    return root

def meshes(root):return [o for o in root.children_recursive if o.type=='MESH']

def surface_z(root,x,y,from_z=3):
    obj=meshes(root)[0];bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    matrix=evaluated.matrix_world;origin=matrix.inverted()@Vector((x,y,from_z))
    direction=matrix.to_3x3().inverted()@Vector((0,0,-1))
    hit,loc,normal,index=evaluated.ray_cast(origin,direction)
    assert hit,'Prop placement must intersect the actual tabletop'
    return (matrix@loc).z

def setup():
    P.clear();scene=bpy.context.scene;P.studio(scene)
    scene.name='Loca reconstructed cafe / color';scene.render.resolution_x=540;scene.render.resolution_y=960
    scene.cycles.samples=20;scene.render.fps=FPS;scene.frame_start=1;scene.frame_end=COUNT
    try:
        preferences=bpy.context.preferences.addons['cycles'].preferences
        if '--metal' in sys.argv:
            preferences.compute_device_type='METAL';preferences.get_devices()
        metal=[d for d in preferences.devices if d.type=='METAL'] if '--metal' in sys.argv else []
        if metal:
            for device in preferences.devices:device.use=device.type=='METAL'
            scene.cycles.device='GPU'
    except (TypeError,RuntimeError):pass
    table=instance('dining_table');near=instance('dining_chair',(0,-.71,0),math.pi)
    far=instance('dining_chair',(0,.71,0),0)
    # Both chair fronts face the table. All props belong to one physical room.
    x,y=.20,-.20;z=surface_z(table,x,y)
    saucer=instance('saucer',(x,y,z),role='support')
    seat_z=surface_z(saucer,x,y)
    cup_data=json.loads((ROOT/'latte_cup/reconstructed/metadata.json').read_text())
    axis=cup_data['coffee_plane']['centre']
    cup=instance('latte_cup',(x-axis[0],y-axis[1],seat_z),role='hero')
    bpy.context.view_layer.update();cup_mesh=meshes(cup)[0]
    low,high=P.bounds([cup_mesh]);target=Vector((x,y,z+(high.z-low.z)*.51))
    floor=P.block('Color-only / quiet floor',(0,0,-.035),(4,4,.06),'cream',.02)
    floor.color=(0,0,0,1);floor['ghost_role']='absent'
    # Fixed soft window light, not animated shelf lighting or bloom.
    P.lighting(Vector((0,0,.8)),1)
    data=bpy.data.cameras.new('Phone / eye-level coffee orbit');cam=bpy.data.objects.new(data.name,data)
    scene.collection.objects.link(cam);scene.camera=cam
    data.type='PERSP';data.sensor_fit='VERTICAL';data.sensor_height=36;data.lens=40
    samples=[]
    for f in range(1,COUNT+1):
        t=(f-1)/FPS;u=max(0,min(1,(t-1.2)/1.8));u=(1-math.cos(math.pi*u))/2
        angle=math.radians(-35+60*u);position=target+Vector((.48*math.sin(angle),-.48*math.cos(angle),0))
        cam.location=position;cam.rotation_euler=(target-position).to_track_quat('-Z','Y').to_euler()
        cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f)
        samples.append(dict(frame=f,position=list(position),target=list(target),angle_deg=-35+60*u))
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    scene.frame_set(1);OUT.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'scene.blend'),compress=True)
    # Check the actual evaluated cup support rather than a nominal box height.
    deps=bpy.context.evaluated_depsgraph_get();ev=cup_mesh.evaluated_get(deps)
    base=min((ev.matrix_world@v.co).z for v in ev.data.vertices)
    assert abs(base-seat_z)<.004,(base,seat_z)
    spec=dict(id='cup_eye_orbitr_cc',status='proof_render_pending',method='scene assembled from local image-driven reconstructions',
        frame_count=COUNT,fps=FPS,duration_s=COUNT/FPS,scope='base_shot_only',handover_status='creator sip remains pending character rig and contact validation',
        source_description=json.loads((BASE/'guides/templates/cup_eye_orbitr_cc.json').read_text())['description'],
        composition=['Stationary cup and open handle provide the orbit landmark','Cup sits at a usable off-centre setting','Opposed chairs face the same table; context stays subordinate'],
        lighting='Fixed broad window-style studio lights; no bloom or moving fixtures',
        camera=dict(lens_mm=40,orbit_degrees=60,radius_m=.48,eye_level=True,samples=samples),
        mobile='Approximately half a metre of slow phone travel around a stationary cup; no gimbal or crane',
        assets=['dining_table','dining_chair','latte_cup','saucer'],
        contacts=dict(tabletop_z=z,saucer_seat_z=seat_z,cup_base_z=base,error_m=abs(base-seat_z)),
        render_variants=['full_color','transparent_ghost'],ghost=dict(fill_base_alpha=.25,whole_overlay_alpha=.65,context_fill_alpha=.05,viewfinder_embedded=False),
        published=False)
    (OUT/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    return scene

def mask_material():
    m=bpy.data.materials.new('Ghost role mask / fill and line');m.use_nodes=True;n=m.node_tree.nodes;n.clear()
    info=n.new('ShaderNodeObjectInfo');emission=n.new('ShaderNodeEmission');output=n.new('ShaderNodeOutputMaterial')
    m.node_tree.links.new(info.outputs['Color'],emission.inputs['Color']);m.node_tree.links.new(emission.outputs[0],output.inputs[0])
    return m

def render(scene,probes=False,probe_numbers=None,frame_numbers=None):
    numbers=frame_numbers or ((probe_numbers or [1,round(COUNT/2),COUNT]) if probes else list(range(1,COUNT+1)));mask=mask_material()
    for name,is_mask in [('color',False),('mask',True)]:
        folder=OUT/(('probes-' if probes else '')+name);folder.mkdir(exist_ok=True)
        scene.view_layers[0].material_override=mask if is_mask else None
        scene.view_settings.view_transform='Standard' if is_mask else 'AgX';scene.view_settings.exposure=0 if is_mask else -.7
        scene.cycles.samples=2 if is_mask else 12
        rendered={}
        for f in numbers:
            scene.frame_set(f);scene.render.filepath=str(folder/('frame_%04d.png'%f))
            signature=tuple(round(v,8) for row in scene.camera.matrix_world for v in row)
            if is_mask:
                signature+=tuple(round(v,6) for o in scene.objects if o.type=='MESH' for v in o.color)
            if scene.get('static_geometry') and signature in rendered:shutil.copy2(rendered[signature],scene.render.filepath)
            else:
                bpy.ops.render.render(write_still=True)
                if scene.get('static_geometry'):rendered[signature]=scene.render.filepath
    print('RECONSTRUCTED_SCENE_RENDERED','probes' if probes else 'full',flush=True)

if __name__=='__main__':
    scene=setup();render(scene,'--probes' in sys.argv)
