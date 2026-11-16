"""Prepare a standalone, measurable clay target and a lightweight geometry proxy."""
import argparse
import hashlib
import json
import math
import sys
import zipfile
from pathlib import Path

import bpy
import bmesh
from mathutils import Matrix,Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_tripo_props as T
import prepare_creator_tripo as B
import build_shared_venue as C
from render_coffee_hologram import material as fields_material
from build_reconstructed_scene import mask_material

PLAN=P.BASE/'model_refferences/tripo-cli/primary-targets-2026-10-29/plan.json'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def ray(meshes,start,direction):
    hits=[];deps=bpy.context.evaluated_depsgraph_get()
    for obj in meshes:
        evaluated=obj.evaluated_get(deps);inverse=evaluated.matrix_world.inverted()
        ok,p,normal,_=evaluated.ray_cast(inverse@Vector(start),inverse.to_3x3()@Vector(direction))
        if ok:
            point=evaluated.matrix_world@p
            hits.append(((point-Vector(start)).length,point))
    return min(hits,key=lambda h:h[0])[1] if hits else None


def geometry_bounds(meshes):
    return B.bounds(meshes)


def repair_guitar(root):
    """Replace the reference's four-string paint with six supported real strings."""
    import numpy as np
    meshes=C.meshes(root);lo,hi=geometry_bounds(meshes);height=hi.z-lo.z
    bridge_z=lo.z+height*.165;nut_z=lo.z+height*.80
    front=lo.y-max(hi-lo)
    bridge_hit=ray(meshes,(0,front,bridge_z),(0,1,0))
    nut_hit=ray(meshes,(0,front,nut_z),(0,1,0))
    assert bridge_hit is not None and nut_hit is not None
    points=np.array([o.matrix_world@v.co for o in meshes for v in o.data.vertices])
    band=points[(abs(points[:,2]-bridge_z)<height*.019)&(abs(points[:,0])<height*.105)]
    bridge_y=float(band[:,1].min())-.004
    nut_y=nut_hit.y-.004
    def string_y(z):return bridge_y+(nut_y-bridge_y)*(z-bridge_z)/(nut_z-bridge_z)
    # Clay palette materials remove the baked four-string picture. The six
    # replacement strings are geometry, so their count stays correct in 3D.
    from prepare_coffee_functional import samples
    for obj in meshes:
        centres,rgb=samples(obj)
        obj.data=obj.data.copy();first=len(obj.data.materials)
        keys=['cream','gold','brown','sage','charcoal']
        for key in keys:
            mat=P.material(key);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.73
            obj.data.materials.append(mat)
        normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
        for face,p,color in zip(obj.data.polygons,centres,rgb):
            r,g,b=color
            key='cream' if min(color)>.28 and max(color)>.50 else 'sage' if g>r*.97 and g>b*1.05 else 'gold' if r>.4 and g>.17 and r>g*1.15 else 'charcoal' if max(color)<.12 else 'brown'
            normal=normal_matrix@face.normal
            if normal.y<-.08:
                if abs(p[0])<height*.047 and p[2]>nut_z and key!='sage':key='brown'
            face.material_index=first+keys.index(key)
    bpy.ops.object.select_all(action='DESELECT')
    before=set(bpy.data.objects)
    board_lo=height*.405;board_hi=nut_z
    verts=[]
    for z,width in [(board_lo,height*.10),(board_hi,height*.078)]:
        hit=ray(meshes,(0,front,z),(0,1,0));back=(hit.y if hit else string_y(z)+.012)+.004
        face_y=string_y(z)+.003
        for x,y in [(-width/2,face_y),(width/2,face_y),(-width/2,max(back,face_y+.005)),(width/2,max(back,face_y+.005))]:verts.append((x,y,z))
    data=bpy.data.meshes.new('Guitar / supported tapered fingerboard')
    data.from_pydata(verts,[],[(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3),(0,1,3,2),(4,6,7,5)]);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:]);bm.to_mesh(data);bm.free()
    board=bpy.data.objects.new(data.name,data);bpy.context.collection.objects.link(board);data.materials.append(P.material('brown'))
    bevel=board.modifiers.new('Soft fingerboard edge','BEVEL');bevel.width=.001;bevel.segments=3
    back_y=bridge_hit.y+.003
    P.block('Guitar / continuous six-pin bridge',(0,(bridge_y+back_y)/2,bridge_z),
            (height*.215,max(.009,back_y-bridge_y),height*.037),'brown',.003)
    P.block('Guitar / six-slot nut',(0,nut_y+.003,nut_z),(height*.081,.007,.006),'cream',.001)
    # A dark lining masks the old painted strings inside the reconstructed
    # cavity; no coarse face-color patches spill onto the cream soundboard.
    cavity=height*.343
    inside=(points[:,0]/(height*.060))**2+((points[:,2]-cavity)/(height*.064))**2<1
    lining_y=float(points[inside,1].min())-.001
    lining=P.lathe('Guitar / dark cavity lining',[(0,0),(height*.060,0),(height*.060,.001),(0,.001)],c='charcoal')
    lining.rotation_euler.x=math.pi/2;lining.scale.y=1.05
    lining.location=(0,lining_y,cavity)
    for index in range(6):
        x_bridge=(index/5-.5)*height*.076;x_nut=(index/5-.5)*height*.060
        left=index<3;peg_x=(-1 if left else 1)*height*.032
        peg_z=height*([.86,.91,.96,.96,.91,.86][index])
        peg=ray(meshes,(peg_x,front,peg_z),(0,1,0))
        peg_y=peg.y-.001 if peg else nut_y
        radius=.0008+(5-index)*.00005
        string=P.tube('Guitar / string '+str(index+1),[(x_bridge,bridge_y-.001,bridge_z),
            (x_nut,nut_y-.001,nut_z)],radius,'cream')
        string['string_number']=index+1
        P.tube('Guitar / tuner string '+str(index+1),[(x_nut,nut_y-.001,nut_z),(peg_x,peg_y,peg_z)],radius,'cream')
        P.ball('Guitar / tuner post '+str(index+1),(peg_x,peg_y+.001,peg_z),(.0045,.003,.0045),'cream')
        pin=P.ball('Guitar / bridge pin '+str(index+1),(x_bridge,bridge_y-.001,bridge_z),(.0035,.0025,.0035),'cream')
        pin['bridge_pin_number']=index+1
    frets=[]
    for n in range(1,20):
        z=nut_z-(nut_z-bridge_z)*(1-2**(-n/12))
        if z<board_lo+.003:continue
        width=height*(.10+(.078-.10)*(z-board_lo)/(board_hi-board_lo))*.94
        P.tube('Guitar / fret '+str(n),[(-width/2,string_y(z)+.0015,z),(width/2,string_y(z)+.0015,z)],.0007,'cream');frets.append(n)
    repair=P.group('Guitar / local six-string hardware',before)
    repair.parent=root;repair.matrix_parent_inverse=root.matrix_world.inverted()
    collection=root.users_collection[0]
    for obj in [repair,*repair.children_recursive]:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
    report=dict(strings=6,bridge_pins=6,tuning_pegs='Six retained from reconstructed headstock',
        frets=frets,scale_length_m=nut_z-bridge_z,bridge_z=bridge_z,nut_z=nut_z,
        original_four_string_markings_replaced=True,source_download_unmodified=True,
        limitation='Hand/finger contact and musical performance are not rigged or validated by this repair')
    root['local_repair']='Six strings, six bridge pins and measured equal-temperament fret positions'
    return report


def anchors(meshes,row):
    lo,hi=geometry_bounds(meshes);middle=(lo+hi)/2;extent=max(hi-lo)
    records={}
    def add(name,point,kind='mesh_surface'):
        if point is None:return
        records[name]=dict(kind=kind,position_blender_m=list(point),position_gltf_m=[point.x,point.z,-point.y])
    add('placement',Vector((0,0,lo.z)),'support_plane_origin')
    add('bounds_center',middle,'bounds_center')
    for name,axis in [('positive_x',(1,0,0)),('negative_x',(-1,0,0)),
                      ('front',(0,-1,0)),('back',(0,1,0)),('top',(0,0,1)),('bottom',(0,0,-1))]:
        direction=Vector(axis);add(name,ray(meshes,middle+direction*extent*2,-direction))
    seat=ray(meshes,Vector((0,0,hi.z+extent)),Vector((0,0,-1)))
    add('support_surface',seat)
    if row['id'] in ['dinner_plate','serving_bowl','stemmed_glass']:
        add('opening_center',Vector((middle.x,middle.y,hi.z)),'bounds_estimated_opening; inspect before pouring')
    if row['id'] in ['hair_clipper','dumbbell','acoustic_guitar']:
        z=lo.z+(hi.z-lo.z)*(.68 if row['id']=='acoustic_guitar' else .5)
        add('grip_candidate',ray(meshes,Vector((0,lo.y-extent,z)),Vector((0,1,0))))
    if row['id'] in ['salon_chair','treatment_bed']:
        add('seat_or_treatment_surface',seat,'center_ray_surface; setup-specific verification required')
    return records


def export_components(root,folder,records):
    scene=bpy.context.scene;meshes=C.meshes(root)
    collection=bpy.data.collections.new('EXPORT ONLY / normalized target');scene.collection.children.link(collection)
    export_root=bpy.data.objects.new('Target / '+root['asset_id'],None);collection.objects.link(export_root)
    export_root['units']='metres';export_root['registration']='manual_pose_and_scale';export_root['not_a_metric_scan']=True
    clones=[];deps=bpy.context.evaluated_depsgraph_get()
    for original in meshes:
        data=bpy.data.meshes.new_from_object(original.evaluated_get(deps),preserve_all_data_layers=True,depsgraph=deps)
        data.transform(original.matrix_world)
        clone=bpy.data.objects.new(original.name,data);collection.objects.link(clone);clone.parent=export_root;clones.append(clone)
    anchor_nodes=[]
    for name,row in records.items():
        obj=bpy.data.objects.new('Anchor / '+name,None);collection.objects.link(obj);obj.parent=export_root
        obj.location=row['position_blender_m'];obj['anchor_kind']=row['kind'];anchor_nodes.append(obj)
    def save(name,objects):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in [export_root,*anchor_nodes,*objects]:obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.export_scene.gltf(filepath=str(folder/name),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
        content=(folder/name).read_bytes();assert content[:4]==b'glTF'
        usd=folder/name.replace('.glb','.usdz')
        bpy.ops.wm.usd_export(filepath=str(usd),selected_objects_only=True,export_animation=False,
            export_materials=True,convert_orientation=True,export_global_forward_selection='NEGATIVE_Z',
            export_global_up_selection='Y',convert_scene_units='METERS',meters_per_unit=1,
            export_custom_properties=True)
        with zipfile.ZipFile(usd) as archive:
            assert any(p.endswith(('.usdc','.usda','.usd')) for p in archive.namelist())
    save('model.glb',clones)
    original_bounds=geometry_bounds(clones)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in clones:obj.select_set(True)
    bpy.context.view_layer.objects.active=clones[0];bpy.ops.object.join()
    proxy=bpy.context.object;proxy.name='Geometry proxy'
    bm=bmesh.new();bm.from_mesh(proxy.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.00001)
    bmesh.ops.triangulate(bm,faces=bm.faces[:]);bm.to_mesh(proxy.data);bm.free()
    original_triangles=len(proxy.data.polygons)
    proxy.data.materials.clear();proxy.data.materials.append(P.material('cream'))
    if original_triangles>8000:
        decimate=proxy.modifiers.new('Registration/render proxy / 8000 triangles','DECIMATE');decimate.ratio=8000/original_triangles
        bpy.ops.object.modifier_apply(modifier=decimate.name)
    new_bounds=geometry_bounds([proxy])
    error=max(abs(a-b) for old,new in zip(original_bounds,new_bounds) for a,b in zip(old,new))
    extent=max(original_bounds[1]-original_bounds[0]);assert error<extent*.025,(error,extent)
    save('geometry-proxy.glb',[proxy])
    result=dict(triangles=sum(len(f.vertices)-2 for f in proxy.data.polygons),bounds_deviation_m=error,
        purpose='Simplified registration/render geometry; not a tested collision hull or measured scan')
    for obj in list(collection.objects):bpy.data.objects.remove(obj,do_unlink=True)
    bpy.data.collections.remove(collection)
    return result


def views(root,out):
    scene=bpy.context.scene;meshes=C.meshes(root)
    floor=next(o for o in scene.objects if o.name.startswith('Review floor'))
    for mode in ['rendered','shape']:
        folder=out/mode;folder.mkdir(exist_ok=True)
        scene.view_layers[0].material_override=None if mode=='rendered' else P.material('cream')
        for name,direction in T.VIEWS.items():
            floor.hide_render=name=='bottom';cam=T.fit_camera(scene,meshes,direction)
            scene.render.filepath=str(folder/(name+'.png'));bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(cam,do_unlink=True)
    floor.hide_render=True
    cam=T.fit_camera(scene,meshes,T.VIEWS['preview'])
    C.role(root,'hero')
    for obj in scene.objects:
        if obj.type=='LIGHT':obj.hide_render=True
    scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0
    for name,material in [('mask',mask_material()),('fields',fields_material())]:
        scene.view_layers[0].material_override=material
        scene.render.filepath=str(out/('overlay-'+name+'.png'));bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    scene.view_layers[0].material_override=None


def run(aid,yaw,package_only=False):
    row=next(r for r in json.loads(PLAN.read_text())['objects'] if r['id']==aid)
    T.ASSETS[aid]=(row['category'],row['description'],row['dimensions_m'])
    P.MATS.clear()
    out=P.ROOT/aid/'tripo-generated/review'
    if package_only:bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'))
    else:T.run(aid,yaw,eevee=True,render_views=False)
    root=next(o for o in bpy.context.scene.objects if o.get('asset_id')==aid+'_tripo')
    repairs={}
    if not package_only and aid=='acoustic_guitar':repairs['guitar']=repair_guitar(root)
    if not package_only and aid=='treatment_bed':
        a,z=geometry_bounds(C.meshes(root));factor=.76/(z.z-a.z)
        root.scale.z*=factor;a,z=geometry_bounds(C.meshes(root));root.location.z-=a.z
        repairs['height_calibration']=dict(axis='Z',factor=factor,target_height_m=.76,reason='Usable treatment height; source mesh file preserved')
    mesh=C.meshes(root);lo,hi=geometry_bounds(mesh)
    assert abs(lo.z)<.0001 and all(math.isfinite(v) for v in [*lo,*hi])
    records=anchors(mesh,row);proxy=export_components(root,out,records)
    collection=root.users_collection[0]
    for name,record in records.items():
        if any(o.name=='Anchor / '+name for o in root.children_recursive):continue
        node=bpy.data.objects.new('Anchor / '+name,None);collection.objects.link(node)
        node.parent=root;node.matrix_parent_inverse=root.matrix_world.inverted()
        node.location=record['position_blender_m'];node.hide_render=True
        node.empty_display_size=.015;node['anchor_kind']=record['kind']
    bpy.ops.file.pack_all()
    bpy.data.libraries.write(str(out/'asset.blend'),{collection},fake_user=True,compress=True)
    cam=T.fit_camera(bpy.context.scene,mesh,T.VIEWS['preview'])
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True)
    bpy.data.objects.remove(cam,do_unlink=True)
    source=json.loads((out/'metadata.json').read_text())
    assert digest(Path(source['source']))==source['source_sha256']
    component=dict(id=aid,category=row['category'],primary_target=True,independently_placeable=True,
        provider='Tripo v3.1',source_geometry_file_preserved=True,source_sha256=source['source_sha256'],
        source_task_id=source['task_id'],credits_consumed=source['credits_consumed'],local_repairs=repairs,
        coordinate_systems=dict(blender='metres, Z up, canonical front -Y',gltf='metres, Y up; [x,z,-y] from Blender',usdz='metres, Y up; [x,z,-y] from Blender'),
        nominal_dimensions_m=row['dimensions_m'],actual_dimensions_m=list(hi-lo),
        actual_dimensions_gltf_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],
        bounds_blender_m=[list(lo),list(hi)],bounds_gltf_m=[[lo.x,lo.z,-hi.y],[hi.x,hi.z,-lo.y]],
        anchors=records,geometry_proxy=proxy,registration_mode=row['registration'],
        lidar_registration_verified=False,metric_scan=False,image_view_opacity=.65,
        candidate_guides=row['guide_candidates'],candidate_bindings=row['step_bindings'],
        constraints=['No scene, floor or decoration is embedded','Support tableware and food are separate targets',
            'Manual pose and scale alignment required; real object dimensions vary','Anchors are model measurements; hand and tool contacts require setup-specific review'],
        files={n:dict(bytes=(out/n).stat().st_size,sha256=digest(out/n)) for n in ['model.glb','geometry-proxy.glb','model.usdz','geometry-proxy.usdz','model.blend','asset.blend']})
    write(out/'component.json',component)
    if not package_only:views(root,out)
    write(out/'native-ready.json',dict(status='ready_for_visual_review',id=aid,front_yaw_deg=yaw,
        six_projections_rendered=True,source_unchanged=True,proxy=proxy))
    print('PRIMARY_TARGET_NATIVE_READY',aid,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('asset');parser.add_argument('--yaw',type=float,default=-90);parser.add_argument('--package-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);run(args.asset,args.yaw,args.package_only)
