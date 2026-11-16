"""Prepare reusable native assets from actual local neural reconstructions.

No proxy geometry is used. Original PLY/GLB and vertex colors remain unchanged.
Palette cleanup assigns matte materials to reconstructed faces; it does not
replace their geometry with primitives.
"""
import bpy,bmesh,colorsys,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
from catalog import ASSETS
ROOT=P.ROOT

def level_cup(mesh,colorattr):
    """Fit the reconstructed coffee plane and make its liquid surface level."""
    if colorattr is None or colorattr.domain!='POINT':return None
    points=np.array([tuple(v.co) for v in mesh.data.vertices])
    hsv=np.array([colorsys.rgb_to_hsv(*c.color_srgb[:3]) for c in colorattr.data])
    candidates=points[(hsv[:,1]>.25)&(hsv[:,2]<.86)&(points[:,2]>.55*points[:,2].max())]
    if len(candidates)<100:return None
    random=np.random.default_rng(42);best=None
    for i in range(100):
        p=candidates[random.choice(len(candidates),3,replace=False)]
        normal=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(normal)
        if length<1e-10:continue
        normal/=length
        if abs(normal[2])<.4:continue
        mask=np.abs((candidates-p[0])@normal)<.0018
        if best is None or mask.sum()>len(best):best=candidates[mask]
    if best is None:return None
    _,_,axes=np.linalg.svd(best-best.mean(0),full_matrices=False);normal=axes[-1]
    if normal[2]<0:normal=-normal
    rotation=Vector(normal).rotation_difference(Vector((0,0,1))).to_matrix()
    for v in mesh.data.vertices:v.co=rotation@v.co
    fit=np.array([tuple(rotation@Vector(p)) for p in best])
    low,high=P.bounds([mesh]);offset=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
    for v in mesh.data.vertices:v.co-=offset
    fit-=np.array(tuple(offset));mesh.data.update()
    qlow,qhigh=np.quantile(fit[:,:2],[.02,.98],axis=0)
    return dict(centre=list((qlow+qhigh)/2),radii=list((qhigh-qlow)/2),z=float(np.median(fit[:,2])),
                corrected_tilt_deg=float(np.degrees(np.arccos(normal[2]))))

def level_fixture(mesh,asset):
    points=np.array([tuple(v.co) for v in mesh.data.vertices]);height=np.ptp(points[:,2]);low=points[:,2].min()
    z0,z1=(.55,.85) if asset=='bar_stool' else (.65,1.01)
    candidates=np.array([tuple(p.center) for p in mesh.data.polygons if p.normal.z>.6 and low+height*z0<p.center.z<low+height*z1])
    if len(candidates)<30:return None
    rng=np.random.default_rng(42);best=None
    for i in range(90):
        p=candidates[rng.choice(len(candidates),3,replace=False)];n=np.cross(p[1]-p[0],p[2]-p[0]);length=np.linalg.norm(n)
        if length<1e-10:continue
        n/=length
        if abs(n[2])<.65:continue
        selected=candidates[np.abs((candidates-p[0])@n)<height*.008]
        if best is None or len(selected)>len(best):best=selected
    if best is None:return None
    _,_,axes=np.linalg.svd(best-best.mean(0),full_matrices=False);normal=axes[-1]
    if normal[2]<0:normal=-normal
    align=Vector(normal).rotation_difference(Vector((0,0,1))).to_matrix()
    for v in mesh.data.vertices:v.co=align@v.co
    mesh.data.update();return float(np.degrees(np.arccos(normal[2])))

def reference_face_colors(mesh,path):
    """Reuse approved face colors on the reconstructed surface, without redrawing."""
    old=next(iter(mesh.data.color_attributes),None)
    if old is None or old.domain!='POINT':return old
    image=bpy.data.images.load(str(path),check_existing=True);image.colorspace_settings.name='Non-Color'
    width,height=image.size;pixels=np.array(image.pixels[:],dtype=np.float32).reshape(height,width,4)
    ys,xs=np.where(pixels[:,:,3]>.5)
    if not len(xs):return old
    lo,hi=P.bounds([mesh]);span=hi-lo
    attr=mesh.data.color_attributes.new(name='Approved reference face colors',type='FLOAT_COLOR',domain='POINT')
    for vertex in mesh.data.vertices:
        x=(vertex.co.x-lo.x)/span.x;y=(vertex.co.z-lo.z)/span.z
        px=min(width-1,max(0,round(xs.min()+x*(xs.max()-xs.min()))));py=min(height-1,max(0,round(ys.min()+y*(ys.max()-ys.min()))))
        rgba=pixels[py,px];original=np.array(old.data[vertex.index].color_srgb)
        weight=max(0,min(1,((lo.y+hi.y)/2+span.y*.12-vertex.co.y)/(span.y*.24)))
        if rgba[3]<.5:weight=0
        color=original*(1-weight)+rgba*weight;color[3]=1
        attr.data[vertex.index].color_srgb=tuple(color)
    return attr

def region(asset,rgb):
    r,g,b=rgb;h,s,v=colorsys.rgb_to_hsv(r,g,b)
    if asset in ['croissant','filled_croissant','croissant_oozing']:
        if asset=='croissant':return 'gold'
        if v<.61:return 'chocolate'
        if s<.40:return 'cream'
        return 'gold'
    if asset=='dining_chair':return 'brown' if v<.74 else 'yellow'
    if asset in ['cup_saucer','latte_cup']:return 'coffee' if s>.30 and v<.81 else 'cream'
    if asset=='saucer':return 'cream'
    if asset=='drinking_glass':return 'coffee' if s>.40 and h<.16 else 'glass'
    if asset=='dining_table':return 'charcoal' if v<.40 else 'brown'
    if asset in ['bar_counter','pastry_rack','wall_shelf','storefront','bar_stool','bottle']:
        if s<.18 and v<.35:return 'charcoal'
        if .16<h<.48 and s>.10:return 'sage'
        if .08<h<.18 and s>.5 and v>.62:return 'yellow'
        if s<.26 and v>.67:return 'cream'
        return 'brown' if asset!='bottle' else 'sage'
    return None

def prepare(asset,render=True,trial=None):
    source=ROOT/'reconstruction-trial'/(trial or asset+'-triposr')
    report=json.loads((source/'report.json').read_text())
    P.clear();scene=bpy.context.scene;P.studio(scene);scene.name='Loca reconstructed / '+asset
    bpy.ops.wm.ply_import(filepath=str(source/'reconstruction.ply'))
    mesh=bpy.context.object;mesh.name='Reconstructed / '+asset
    bm=bmesh.new();bm.from_mesh(mesh.data)
    normals_reversed=bm.calc_volume(signed=True)<0
    if normals_reversed:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    bm.normal_update();bm.to_mesh(mesh.data);bm.free()
    rotation=Matrix.Rotation(-math.pi/2,3,'Z')
    for v in mesh.data.vertices:v.co=rotation@v.co
    if asset in ['dining_chair','bar_stool'] and trial:
        # The three-quarter input is not a canonical front elevation. Align the
        # reconstructed backrest plane before defining standard asset views.
        pts=np.array([tuple(v.co) for v in mesh.data.vertices])
        upper=pts[pts[:,2]>np.quantile(pts[:,2],.75)]
        values,axes=np.linalg.eigh(np.cov(upper[:,:2].T));front=axes[:,0]
        if front[1]>0:front=-front
        delta=-math.pi/2-math.atan2(front[1],front[0]);align=Matrix.Rotation(delta,3,'Z')
        for v in mesh.data.vertices:v.co=align@v.co
    if asset in ['bar_counter','pastry_rack','storefront','wall_shelf','rack_shelf_tray']:
        points=np.array([tuple(v.co) for v in mesh.data.vertices]);values,axes=np.linalg.eigh(np.cov(points[:,:2].T));long_axis=axes[:,-1]
        if long_axis[0]<0:long_axis=-long_axis
        align=Matrix.Rotation(-math.atan2(long_axis[1],long_axis[0]),3,'Z')
        for v in mesh.data.vertices:v.co=align@v.co
    fixture_leveling=level_fixture(mesh,asset) if asset in ['bar_counter','bar_stool'] else None
    if asset in ['saucer','rack_shelf_tray']:
        points=np.array([tuple(v.co) for v in mesh.data.vertices])
        values,axes=np.linalg.eigh(np.cov(points.T));normal=axes[:,0]
        if normal[2]<0:normal=-normal
        align=Vector(normal).rotation_difference(Vector((0,0,1))).to_matrix()
        for v in mesh.data.vertices:v.co=align@v.co
    lo,hi=P.bounds([mesh])
    if asset in ['dining_chair','dining_table','bar_counter','bar_stool','pastry_rack','storefront','bottle']:factor=ASSETS[asset][2][2]/(hi.z-lo.z)
    else:factor=ASSETS[asset][2][0]/(hi.x-lo.x) if asset in ASSETS else 1.72/(hi.z-lo.z)
    origin=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    for v in mesh.data.vertices:v.co=(v.co-origin)*factor
    if asset in ['bar_counter','pastry_rack','storefront','wall_shelf','rack_shelf_tray']:
        low,high=P.bounds([mesh]);size=high-low;target=ASSETS[asset][2]
        for v in mesh.data.vertices:
            for i in range(3):v.co[i]*=target[i]/size[i]
    mesh.data.update()
    for poly in mesh.data.polygons:poly.use_smooth=True
    colorattr=next(iter(mesh.data.color_attributes),None)
    coffee_plane=level_cup(mesh,colorattr) if asset in ['cup_saucer','latte_cup','drinking_glass'] else None
    calibration=None
    if asset in ['latte_cup','saucer','drinking_glass']:
        low,high=P.bounds([mesh]);z_scale=ASSETS[asset][2][2]/(high.z-low.z)
        for v in mesh.data.vertices:v.co.z*=z_scale
        if coffee_plane:coffee_plane['z']*=z_scale
        calibration=dict(z_scale=z_scale,reason='Match the standalone reference proportions and physical vessel thickness',target_height_m=ASSETS[asset][2][2])
        mesh.data.update()
    lo,hi=P.bounds([mesh]);height=hi.z-lo.z
    seat_plane=None
    if asset in ['dining_chair','bar_stool']:
        zlow,zhigh=(.55,.85) if asset=='bar_stool' else (.35,.68)
        pts=np.array([tuple(p.center) for p in mesh.data.polygons if p.normal.z>.65 and height*zlow<p.center.z<height*zhigh])
        if len(pts)>30:
            seat_plane=np.linalg.lstsq(np.c_[pts[:,0],pts[:,1],np.ones(len(pts))],pts[:,2],rcond=None)[0]
    character=asset.removesuffix('_head')
    is_character=character in ['barista','creator','friend_locs']
    if is_character and asset.endswith('_head'):
        colorattr=reference_face_colors(mesh,source/'input-alpha.png')
    palette=not is_character
    slots={}
    if palette:
        for poly in mesh.data.polygons:
            if colorattr:
                values=[colorattr.data[mesh.data.loops[i].vertex_index if colorattr.domain=='POINT' else i].color_srgb[:3] for i in poly.loop_indices]
                rgb=tuple(sum(c[k] for c in values)/len(values) for k in range(3))
            else:rgb=(1,.7,.2)
            centre=poly.center
            h,s,v=colorsys.rgb_to_hsv(*rgb)
            # Restrict materials to their physical regions. Inferred shading
            # on a cream cup must not turn into brown stains on its walls.
            key=region(asset,rgb)
            if asset in ['cup_saucer','latte_cup','drinking_glass']:
                key='cream'
                if coffee_plane:
                    dx=(centre.x-coffee_plane['centre'][0])/coffee_plane['radii'][0]
                    dy=(centre.y-coffee_plane['centre'][1])/coffee_plane['radii'][1]
                    h,s,v=colorsys.rgb_to_hsv(*rgb)
                    if dx*dx+dy*dy<1.10 and abs(centre.z-coffee_plane['z'])<.0035 and s>.22:key='coffee'
            if asset=='dining_chair':
                seat_z=float(seat_plane@[centre.x,centre.y,1]) if seat_plane is not None else height*.54
                key='yellow' if centre.z>height*.68 or abs(centre.z-seat_z)<height*.075 else 'brown'
            if asset=='dining_table':key='brown' if centre.z>height*.87 else 'charcoal'
            if asset in ['filled_croissant','croissant_oozing'] and abs(centre.x)>ASSETS[asset][2][0]*.24:key='gold'
            if asset=='croissant_oozing':
                h,s,v=colorsys.rgb_to_hsv(*rgb)
                facing_break=abs(centre.x)<.047 and poly.normal.x*(1 if centre.x>0 else -1)<-.20 and poly.normal.z<.55
                hanging_fill=abs(centre.x)<.019 and centre.z<height*.45 and v<.61
                key='chocolate' if hanging_fill or (facing_break and v<.61) else 'cream' if facing_break else 'gold'
            if asset=='bar_counter':
                key='brown' if centre.z>height*.90 else 'yellow' if centre.y<-.32 and height*.07<centre.z<height*.33 else 'sage'
            if asset=='bar_stool':
                seat_z=float(seat_plane@[centre.x,centre.y,1]) if seat_plane is not None else height*.74
                key='yellow' if centre.z>height*.84 or abs(centre.z-seat_z)<height*.055 else 'charcoal' if v<.48 and s<.30 else 'brown'
            if asset=='wall_shelf':key='sage' if rgb[1]>rgb[0]*1.02 else 'brown'
            if asset=='rack_shelf_tray':key='brown' if s>.25 and v<.80 else 'cream'
            if asset=='pastry_rack' and 'TripoSG' in report.get('method',''):
                key='sage' if abs(centre.x)>.41 else 'cream' if poly.normal.z>.60 else 'brown'
            if asset=='storefront':key='yellow' if s>.45 and .08<h<.18 and centre.z>height*.75 else 'sage' if rgb[1]>rgb[0]*1.02 else 'cream'
            if asset=='bottle':
                key='yellow' if centre.z>height*.90 else 'cream' if height*.20<centre.z<height*.61 and centre.y<-.012 and abs(centre.x)<.021 else 'sage'
            if key is None:palette=False;break
            if key not in slots:slots[key]=len(slots);mesh.data.materials.append(P.material(key))
            poly.material_index=slots[key]
    if not palette:
        mesh.data.materials.clear();mat=bpy.data.materials.new('Image-driven clay colors');mat.use_nodes=True
        p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Roughness'].default_value=.64
        if colorattr:
            color=mat.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name=colorattr.name
            mat.node_tree.links.new(color.outputs['Color'],p.inputs['Base Color'])
        mesh.data.materials.append(mat)
        for poly in mesh.data.polygons:poly.material_index=0
        if is_character and colorattr:
            hair_key='hair_'+character;P.PALETTE[hair_key]={'barista':'423027','creator':'493026','friend_locs':'382B25'}[character]
            mesh.data.materials.append(P.material(hair_key))
            threshold=.58 if asset.endswith('_head') else .86
            max_hair_value=.36 if character=='friend_locs' else .68
            for poly in mesh.data.polygons:
                colors=[colorattr.data[mesh.data.loops[i].vertex_index if colorattr.domain=='POINT' else i].color_srgb[:3] for i in poly.loop_indices]
                brightness=sum(max(c) for c in colors)/len(colors)
                if poly.center.z>height*threshold and brightness<max_hair_value:poly.material_index=1
    smooth=mesh.modifiers.new('Gentle reconstruction cleanup','SMOOTH');smooth.factor=.25;smooth.iterations=5
    parts=[mesh];removed_components=0
    if asset=='croissant_oozing':
        bm=bmesh.new();bm.from_mesh(mesh.data);unseen=set(bm.faces);remove=[]
        while unseen:
            seed=unseen.pop();component={seed};todo=[seed]
            while todo:
                face=todo.pop()
                for edge in face.edges:
                    for other in edge.link_faces:
                        if other in unseen:unseen.remove(other);component.add(other);todo.append(other)
            if len(component)<100:remove.extend(component);removed_components+=1
        if remove:bmesh.ops.delete(bm,geom=list({v for f in remove for v in f.verts}),context='VERTS')
        bm.to_mesh(mesh.data);bm.free()
        bpy.ops.object.select_all(action='DESELECT');mesh.select_set(True);bpy.context.view_layer.objects.active=mesh
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT')
        parts=[o for o in bpy.context.selected_objects if o.type=='MESH']
        assert len(parts)==2,'The broken croissant must expose two editable halves'
        for i,part in enumerate(sorted(parts,key=lambda o:sum(v.co.x for v in o.data.vertices)/len(o.data.vertices))):
            centre=sum((v.co for v in part.data.vertices),Vector())/len(part.data.vertices)
            for v in part.data.vertices:v.co-=centre
            part.location=centre;part.name='Croissant / '+('left half' if i==0 else 'right half')
            part['animation_part']='left_half' if i==0 else 'right_half'
    root=P.empty('Loca / '+asset)
    for part in parts:part.parent=root
    method=report.get('method','local TripoSR reconstruction')
    root['asset_id']=asset;root['method']=method;root['source_sha256']=report['input_sha256']
    root['front_direction']='-Y';root['units']='metres';root['status']='reconstructed_pending_visual_review'
    P.anchor(root,'support',(0,0,0))
    if coffee_plane:P.anchor(root,'liquid_surface',(*coffee_plane['centre'],coffee_plane['z']))
    lo,hi=P.bounds(parts);center=(lo+hi)/2;extent=max(hi-lo)
    collection=bpy.data.collections.new('Loca reconstructed / '+asset);scene.collection.children.link(collection)
    for obj in [root,*root.children_recursive]:
        for c in list(obj.users_collection):c.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark();collection.asset_data.description='Loca image-driven clay asset: '+asset
    out=ROOT/asset/'reconstructed';out.mkdir(parents=True,exist_ok=True)
    bpy.data.libraries.write(str(out/'asset.blend'),{collection},fake_user=True,compress=True)
    P.lighting(center,extent)
    cd=bpy.data.cameras.new('Model review camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam
    cd.type='ORTHO';cd.ortho_scale=extent*1.28
    cam.location=center+Vector((1,-1.7,1.1)).normalized()*extent*4
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True)
    views={'front':(0,-1,0),'back':(0,1,0),'left':(-1,0,0),'right':(1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(1,-1.7,1.1)}
    if is_character:
        views['left'],views['right']=views['right'],views['left']
    if render:
        for view,direction in views.items():
            cam.location=center+Vector(direction).normalized()*extent*4
            cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True)
    metadata=dict(asset=asset,status='rendered_pending_visual_review',method=method,
        model='model.blend',appendable_asset='asset.blend',source_report=str(source.relative_to(ROOT)/'report.json'),
        dimensions_m=list(hi-lo),materials=list(slots),palette_cleanup=palette,original_geometry_preserved=True,
        smoothing='factor 0.25, five iterations',views=list(views),single_view_inference=True,
        source_model_unmodified=True,normals_reoriented_outward=normals_reversed,coffee_plane=coffee_plane,
        mesh_parts=len(parts),tiny_artifact_components_removed=removed_components,dimension_calibration=calibration,fixture_leveling_deg=fixture_leveling,
        coordinates='front=-Y; Z-up; metres; origin at support plane')
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('RECONSTRUCTED_ASSET_PREPARED',asset,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    trial=None
    if '--trial' in args:
        i=args.index('--trial');trial=args[i+1];args=args[:i]+args[i+2:]
    for asset in args:prepare(asset,trial=trial)
