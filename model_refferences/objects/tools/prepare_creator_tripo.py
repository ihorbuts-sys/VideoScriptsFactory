"""Preserve the user-exported Tripo model and render a matched local-model comparison."""
import bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
ROOT=P.ROOT.parents[0]/'creator'
SOURCE=ROOT/'3d female character.glb'
OUT=ROOT/'tripo-comparison'

def bounds(objects):
    bpy.context.view_layer.update()
    coords=[o.matrix_world@v.co for o in objects if o.type=='MESH' for v in o.data.vertices]
    return Vector([min(p[i] for p in coords) for i in range(3)]),Vector([max(p[i] for p in coords) for i in range(3)])

def camera(scene,target,direction,scale,ortho=True):
    data=bpy.data.cameras.new('Comparison camera');obj=bpy.data.objects.new(data.name,data);scene.collection.objects.link(obj);scene.camera=obj
    data.type='ORTHO' if ortho else 'PERSP';data.ortho_scale=scale;data.lens=65
    obj.location=Vector(target)+Vector(direction).normalized()*scale*4
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler();return obj

def studio():
    P.clear();scene=bpy.context.scene;P.studio(scene)
    scene.view_layers[0].material_override=None
    scene.render.resolution_x=640;scene.render.resolution_y=800;scene.cycles.samples=16
    floor=P.block('Review floor',(0,0,-.015),(6,6,.03),'cream',.01)
    P.lighting(Vector((0,0,.95)),1.6)
    return scene

def imported(yaw):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE));objects=list(set(bpy.context.scene.objects)-before)
    # Import creates its own node hierarchy; keep it intact under one placement control.
    root=P.empty('Creator / Tripo original');nodes=set(objects)
    for obj in objects:
        if obj.parent not in nodes:obj.parent=root
    root.rotation_euler.z=math.radians(yaw)
    meshes=[o for o in root.children_recursive if o.type=='MESH'];low,high=bounds(meshes)
    factor=1.72/(high.z-low.z);root.scale=(factor,)*3
    low,high=bounds(meshes);root.location-=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
    root['asset_id']='creator_tripo';root['units']='metres';root['source_sha256']=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    root['source_geometry_unmodified']=True;root['placement_only']='Uniform scale, root yaw and ground translation'
    root['rig_status']='No armature in imported GLB'
    return root,meshes,factor

def baseline():
    path=P.ROOT/'creator/reconstructed/asset.blend'
    with bpy.data.libraries.load(str(path),link=False) as (s,d):d.collections=[s.collections[0]]
    collection=d.collections[0];bpy.context.scene.collection.children.link(collection)
    root=next(o for o in collection.objects if o.get('asset_id')=='creator')
    meshes=[o for o in root.children_recursive if o.type=='MESH'];lo,hi=bounds(meshes)
    root.scale*=1.72/(hi.z-lo.z);lo,hi=bounds(meshes);root.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    return root,meshes

def render_views(scene,meshes,folder,probes=False,only_views=None):
    folder.mkdir(parents=True,exist_ok=True)
    override=scene.view_layers[0].material_override
    if folder.name in ['tripo','local-triposr']:assert override is None,'Textured comparison must use the original materials'
    if folder.name in ['tripo-shape','local-shape']:assert override is not None,'Shape comparison must use the uniform diagnostic material'
    (folder/'material-pass.json').write_text(json.dumps(dict(material_override=override.name if override else None,
        mesh_materials=[m.name for o in meshes for m in o.data.materials]),indent=2)+'\n')
    target=Vector((0,0,.86));cam=camera(scene,target,(0,-1,0),2.02)
    views={'front':(0,-1,0),'back':(0,1,0),'left':(1,0,0),'right':(-1,0,0),'three-quarter':(.8,-1.7,.20),'top':(0,0,1),'bottom':(0,0,-1)}
    if probes:views={k:views[k] for k in ['front','back','left','right']}
    if only_views:views={k:views[k] for k in only_views}
    floors=[o for o in scene.objects if o.name.startswith('Review floor')]
    for name,direction in views.items():
        for floor in floors:floor.hide_render=name=='bottom'
        cam.location=target+Vector(direction).normalized()*8
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
    for floor in floors:floor.hide_render=False
    if not probes and not only_views:
        for name,target,scale,direction in [('face',(0,-.015,1.47),.62,(0,-1,0)),('face-three-quarter',(0,-.015,1.47),.62,(.8,-1.7,.1)),
                ('right-hand',(-.30,-.02,.70),.38,(0,-1,0)),('left-hand',(.30,-.02,.70),.38,(0,-1,0))]:
            cam.data.ortho_scale=scale;cam.location=Vector(target)+Vector(direction).normalized()*4
            cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.render.resolution_x=800;scene.render.resolution_y=800
            scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
    return cam

def run():
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    yaw=float(args[args.index('--yaw')+1]) if '--yaw' in args else 0
    probes='--probes' in args;OUT.mkdir(parents=True,exist_ok=True)
    if '--refresh-local-materials' in args:
        scene=studio();root,meshes=baseline();render_views(scene,meshes,OUT/'local-triposr');return
    scene=studio();root,meshes,factor=imported(yaw)
    if '--refresh-bottom' in args:
        render_views(scene,meshes,OUT/'tripo',only_views=['bottom'])
        scene.view_layers[0].material_override=P.material('cream');render_views(scene,meshes,OUT/'tripo-shape',only_views=['bottom'])
        scene=studio();root,meshes=baseline();render_views(scene,meshes,OUT/'local-triposr',only_views=['bottom'])
        scene.view_layers[0].material_override=P.material('cream');render_views(scene,meshes,OUT/'local-shape',only_views=['bottom'])
        return
    if probes:
        scene.cycles.samples=8;render_views(scene,meshes,OUT/'orientation-probes',True);return
    collection=bpy.data.collections.new('Loca imported creator / Tripo');scene.collection.children.link(collection)
    for obj in [root,*root.children_recursive]:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark();collection.asset_data.description='Original user-generated Tripo creator, with embedded materials; unrigged'
    bpy.ops.file.pack_all();bpy.data.libraries.write(str(OUT/'asset.blend'),{collection},fake_user=True,compress=True)
    cam=camera(scene,(0,0,.86),(.8,-1.7,.20),2.02)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'creator.blend'),compress=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    records=[]
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data)
        part_low,part_high=bounds([obj])
        records.append(dict(name=obj.name,bounds_min=list(part_low),bounds_max=list(part_high),vertices=len(obj.data.vertices),faces=len(obj.data.polygons),triangles=sum(len(p.vertices)-2 for p in obj.data.polygons),
            boundary_edges=sum(e.is_boundary for e in bm.edges),non_manifold_edges=sum(not e.is_manifold for e in bm.edges),
            material_names=[m.name for m in obj.data.materials]));bm.free()
    images=[dict(name=i.name,size=list(i.size),packed=bool(i.packed_file)) for i in bpy.data.images if i.type=='IMAGE' and i.name!='Render Result']
    render_views(scene,meshes,OUT/'tripo')
    # Geometry diagnostic: override materials, keeping the exact same mesh and view.
    mat=P.material('cream');scene.view_layers[0].material_override=mat
    render_views(scene,meshes,OUT/'tripo-shape')
    lo,hi=bounds(meshes)
    metadata=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        imported_provider='Tripo',model='creator.blend',appendable_asset='asset.blend',source_geometry_unmodified=True,
        root_yaw_deg=yaw,uniform_scale_factor=factor,dimensions_m=list(hi-lo),mesh_parts=records,
        textures=images,armatures=sum(o.type=='ARMATURE' for o in root.children_recursive),
        animations=sum(bool(o.animation_data) for o in root.children_recursive),status='comparison_only_pending_visual_review',
        comparison='Same 1.72m height, orthographic framing and fixed studio lighting for both models',
        limitations=['Imported file contains no rig or animations','Source generation settings and input view count were not supplied','No contact or deformation validation has been performed'])
    (OUT/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    scene=studio();root,meshes=baseline();render_views(scene,meshes,OUT/'local-triposr')
    scene.view_layers[0].material_override=P.material('cream');render_views(scene,meshes,OUT/'local-shape')
    print('CREATOR_TRIPO_COMPARISON_RENDERED',len(records),sum(r['triangles'] for r in records),flush=True)

if __name__=='__main__':run()
