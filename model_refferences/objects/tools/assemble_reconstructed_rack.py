"""Functional modular rack: inferred shelf/tray and pastries, authored support posts."""
import bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_reconstructed_scene as C
P=C.P;ROOT=C.ROOT

def run():
    P.clear();scene=bpy.context.scene;P.studio(scene);scene.cycles.samples=12
    scene.name='Loca modular reconstructed pastry rack'
    root=P.empty('Loca / pastry_rack');root['asset_id']='pastry_rack'
    root['method']='Hybrid: locally reconstructed shelf/tray and croissants; authored simple structural posts'
    posts=[]
    for x in [-.472,.472]:
        for y in [-.212,.212]:
            post=P.tube('Frame / sage upright',[(x,y,.028),(x,y,1.522)],.028,'sage');post.parent=root;posts.append(post)
            for z in [.028,1.522]:
                cap=P.ball('Frame / moulded post cap',(x,y,z),(.028,.028,.028),'sage');cap.parent=root;posts.append(cap)
    checks=[];shelves=[]
    for level,z in enumerate([.14,.50,.86,1.22],1):
        shelf=C.instance('rack_shelf_tray',(0,0,z),role='support');shelf.parent=root;shelves.append(shelf)
        for x in [-.29,-.097,.097,.29]:
            y=-.025;support=C.surface_z(shelf,x,y,from_z=z+.12)
            pastry=C.instance('croissant',(x,y,support),role='hero');pastry.parent=root
            low,high=P.bounds(C.meshes(pastry));error=abs(low.z-support)
            assert error<.002,('Pastry is unsupported',error)
            assert low.x>-.42 and high.x<.42 and low.y>-.17 and high.y<.17,'Pastry overhangs the tray'
            checks.append(dict(level=level,x=x,y=y,support_z=support,pastry_base_z=low.z,error_m=error,
                tray_edge_clearance_m=min(low.x+.42,.42-high.x,low.y+.17,.17-high.y)))
    # Preserve a separately usable empty rack collection as well as removable food.
    collection=bpy.data.collections.new('Loca modular / pastry_rack');scene.collection.children.link(collection)
    for obj in [root,*root.children_recursive]:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        collection.objects.link(obj)
    collection.asset_mark();collection.asset_data.description='Long trays, sixteen supported reusable croissants, four open shelf levels'
    out=ROOT/'pastry_rack/reconstructed';out.mkdir(exist_ok=True)
    bpy.data.libraries.write(str(out/'asset.blend'),{collection},fake_user=True,compress=True)
    food=[o for o in root.children_recursive if o.get('asset_id')=='croissant']
    for item in food:
        for mesh in C.meshes(item):mesh.hide_render=True;mesh.hide_viewport=True
    bpy.data.libraries.write(str(out/'empty-asset.blend'),{collection},fake_user=True,compress=True)
    for item in food:
        for mesh in C.meshes(item):mesh.hide_render=False;mesh.hide_viewport=False
    low,high=P.bounds(C.meshes(root));center=(low+high)/2;extent=max(high-low)
    P.lighting(center,extent)
    data=bpy.data.cameras.new('Rack / six-view review');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
    data.type='ORTHO';data.ortho_scale=extent*1.28
    views={'front':(0,-1,0),'back':(0,1,0),'left':(-1,0,0),'right':(1,0,0),'top':(0,0,1),'bottom':(0,0,-1),'preview':(1,-1.7,1.1)}
    for name,direction in views.items():
        camera.location=center+Vector(direction).normalized()*extent*4
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True)
    metadata=dict(asset='pastry_rack',status='rendered_pending_visual_review',method=root['method'],
        model='model.blend',appendable_asset='asset.blend',empty_asset='empty-asset.blend',
        source_report='rack_shelf_tray/reconstructed/metadata.json',dimensions_m=list(high-low),
        coordinates='front=-Y; Z-up; metres; origin at support plane',views=list(views),
        components=dict(reconstructed_shelf_trays=4,reused_reconstructed_croissants=16,authored_uprights=4),
        shelf_levels=4,food_individually_editable=True,contacts=checks,
        minimum_tray_edge_clearance_m=min(c['tray_edge_clearance_m'] for c in checks),
        rejected_trials=['pastry_rack-triposr-v2','pastry_rack-triposg','pastry_rack-triposg-50'],
        limitations=['Structural posts are authored support geometry, not an inferred mesh','Shelf/tray unseen surfaces remain single-view inference'])
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('MODULAR_RACK_PREPARED',len(checks),metadata['minimum_tray_edge_clearance_m'])

if __name__=='__main__':run()
