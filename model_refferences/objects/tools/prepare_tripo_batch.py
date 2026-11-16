"""Review original Tripo CLI results as native assets, with physical support diagnostics."""
import bpy,bmesh,hashlib,json,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as CREATOR
REFS=P.ROOT.parent
HEIGHTS={'barista':1.72,'friend_locs':1.72,'dining_chair':.82}

def setup(asset):
    P.clear();scene=bpy.context.scene;P.studio(scene);scene.view_layers[0].material_override=None
    scene.render.resolution_x=640;scene.render.resolution_y=800 if asset!='dining_chair' else 640
    scene.cycles.samples=12;height=HEIGHTS[asset]
    P.block('Review floor',(0,0,-.015),(6,6,.03),'cream',.01)
    P.lighting(Vector((0,0,height*.55)),height*.93)
    return scene

def load(asset,source,yaw):
    before=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(source))
    imported=set(bpy.context.scene.objects)-before;root=P.empty('Loca / Tripo '+asset)
    for obj in imported:
        if obj.parent not in imported:obj.parent=root
    root.rotation_euler.z=math.radians(yaw);meshes=[o for o in root.children_recursive if o.type=='MESH']
    lo,hi=CREATOR.bounds(meshes);factor=HEIGHTS[asset]/(hi.z-lo.z);root.scale=(factor,)*3
    lo,hi=CREATOR.bounds(meshes);root.location-=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    root['asset_id']=asset+'_tripo';root['source_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
    root['source_geometry_unmodified']=True;root['units']='metres';root['canonical_front']='-Y'
    bpy.context.view_layer.update()
    return root,meshes,factor

def contacts(asset,meshes):
    lo,hi=CREATOR.bounds(meshes);height=hi.z-lo.z
    points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices if (o.matrix_world@v.co).z<height*.12]
    result=[]
    if asset=='dining_chair':
        for xsign in [-1,1]:
            for ysign in [-1,1]:
                selected=[p.z for p in points if p.x*xsign>.04 and p.y*ysign>.04]
                result.append(dict(foot=('left' if xsign>0 else 'right')+'_'+('back' if ysign>0 else 'front'),min_z_m=min(selected) if selected else None))
    else:
        for xsign in [-1,1]:
            selected=[p.z for p in points if p.x*xsign>.015]
            result.append(dict(foot='left' if xsign>0 else 'right',min_z_m=min(selected) if selected else None))
    return dict(lowest_vertex_z=lo.z,feet=result,
        all_expected_feet_detected=all(x['min_z_m'] is not None for x in result),
        max_foot_height_difference_m=max((x['min_z_m'] for x in result if x['min_z_m'] is not None),default=0),
        limitation='Per-foot vertex minima are geometric diagnostics; they do not certify load-bearing contacts or deformation')

def views(scene,asset,folder,probes=False,shape=False):
    folder.mkdir(parents=True,exist_ok=True);height=HEIGHTS[asset];target=Vector((0,0,height*.5))
    scene.view_layers[0].material_override=P.material('cream') if shape else None
    scene.render.resolution_x=640;scene.render.resolution_y=800 if asset!='dining_chair' else 640
    cam=CREATOR.camera(scene,target,(0,-1,0),height*1.19)
    directions={'front':(0,-1,0),'back':(0,1,0),'left':(1,0,0),'right':(-1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(.9,-1.7,.8 if asset=='dining_chair' else .20)}
    if probes:directions={k:directions[k] for k in ['front','left','back','right']}
    floor=next(o for o in scene.objects if o.name.startswith('Review floor'))
    for name,direction in directions.items():
        floor.hide_render=name=='bottom';cam.location=target+Vector(direction).normalized()*height*4
        cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
    floor.hide_render=False
    if not probes and asset!='dining_chair':
        scene.render.resolution_x=800;scene.render.resolution_y=800
        for name,point,scale in [('face',(0,0,height*.855),height*.36),('right-hand',(-height*.175,0,height*.43),height*.23),('left-hand',(height*.175,0,height*.43),height*.23)]:
            cam.data.ortho_scale=scale;cam.location=Vector(point)+Vector((0,-4,0));cam.rotation_euler=(Vector(point)-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)

def run():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('asset',choices=HEIGHTS);p.add_argument('source');p.add_argument('--out',required=True);p.add_argument('--yaw',type=float,default=0);p.add_argument('--probes',action='store_true')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(args.source).resolve();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    scene=setup(args.asset);root,meshes,factor=load(args.asset,source,args.yaw)
    if args.probes:views(scene,args.asset,out/'orientation-probes',True);return
    orientation={}
    if args.asset=='dining_chair':
        upper=[o.matrix_world@v.co for o in meshes for v in o.data.vertices if (o.matrix_world@v.co).z>HEIGHTS[args.asset]*.70]
        assert upper,'No backrest vertices were found after updating the placement transform'
        centre=sum(upper,Vector())/len(upper)
        assert centre.y>.03,'Chair front is reversed: its backrest must lie behind the seat at positive Y'
        orientation=dict(backrest_centre=list(centre),front_direction='-Y',basis='Visually reviewed profile and measured high backrest position')
    collection=bpy.data.collections.new('Loca Tripo / '+args.asset);scene.collection.children.link(collection)
    for obj in [root,*root.children_recursive]:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark();collection.asset_data.description='Loca Tripo CLI '+args.asset+'; original model retained; review candidate'
    bpy.ops.file.pack_all();bpy.data.libraries.write(str(out/'asset.blend'),{collection},fake_user=True,compress=True)
    height=HEIGHTS[args.asset];cam=CREATOR.camera(scene,(0,0,height*.5),(.9,-1.7,.8 if args.asset=='dining_chair' else .20),height*1.19)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);bpy.data.objects.remove(cam,do_unlink=True)
    mesh_rows=[]
    for obj in meshes:
        bm=bmesh.new();bm.from_mesh(obj.data)
        mesh_rows.append(dict(name=obj.name,vertices=len(obj.data.vertices),triangles=sum(len(poly.vertices)-2 for poly in obj.data.polygons),raw_boundary_edges=sum(e.is_boundary for e in bm.edges)));bm.free()
    lo,hi=CREATOR.bounds(meshes)
    data=dict(id=args.asset,provider='Tripo CLI H3.1',status='rendered_pending_visual_review',source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        model='model.blend',appendable_asset='asset.blend',source_geometry_unmodified=True,root_yaw_deg=args.yaw,uniform_scale_factor=factor,dimensions_m=list(hi-lo),
        meshes=mesh_rows,textures=[dict(name=i.name,resolution=list(i.size),packed=bool(i.packed_file)) for i in bpy.data.images if i.type=='IMAGE'],
        armatures=sum(o.type=='ARMATURE' for o in root.children_recursive),support=contacts(args.asset,meshes),orientation=orientation,
        limitations=['Raw boundary counts include UV/normal seams','No rig or deformation validation','Normalization uses nominal height; it is not a dimensional reconstruction certificate'])
    (out/'metadata.json').write_text(json.dumps(data,indent=2)+'\n')
    views(scene,args.asset,out/'rendered');views(scene,args.asset,out/'shape',shape=True)
    print('TRIPO_ASSET_REVIEW_PREPARED',args.asset,sum(r['triangles'] for r in mesh_rows),flush=True)

if __name__=='__main__':run()
