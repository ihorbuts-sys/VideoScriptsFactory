"""Bind-pose support markers sampled from actual Tripo geometry, not nominal boxes."""
import bpy,hashlib,json,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
import prepare_creator_tripo as C
REFS=P.ROOT.parent;BASE=REFS.parent

def run(asset,folder):
    folder=Path(folder).resolve();bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'))
    scene=bpy.context.scene;scene.view_layers[0].material_override=None
    root=next(o for o in scene.objects if o.get('asset_id')==asset+'_tripo')
    for o in list(root.children_recursive):
        if o.get('loca_geometry_anchor'):bpy.data.objects.remove(o,do_unlink=True)
    meshes=[o for o in root.children_recursive if o.type=='MESH'];bpy.context.view_layer.update()
    low,high=C.bounds(meshes);height=high.z-low.z
    points=[o.matrix_world@v.co for o in meshes for v in o.data.vertices if (o.matrix_world@v.co).z<height*.12]
    anchors={}
    def add(name,point,basis):
        local=root.matrix_world.inverted()@point;obj=P.anchor(root,name,local);obj['loca_geometry_anchor']=True
        obj.empty_display_type='PLAIN_AXES';obj.empty_display_size=.015
        bpy.context.view_layer.update();error=(obj.matrix_world.translation-point).length;assert error<1e-5
        anchors[name]=dict(world_position=list(point),root_local_position=list(local),basis=basis,placement_error_m=error)
        for collection in list(obj.users_collection):collection.objects.unlink(obj)
        root.users_collection[0].objects.link(obj)
    for xsign in [-1,1]:
        for ysign in [-1,1] if asset=='dining_chair' else [0]:
            selected=[p for p in points if p.x*xsign>.015 and (not ysign or p.y*ysign>.04)]
            assert selected,'Expected foot geometry missing'
            point=min(selected,key=lambda p:p.z)
            name=('left' if xsign>0 else 'right')+('_back' if ysign>0 else '_front' if ysign<0 else '')+'_support'
            add(name,point,'Lowest actual vertex in this foot region; bind pose only')
    if asset=='dining_chair':
        candidates=[]
        for obj in meshes:
            normal_matrix=obj.matrix_world.to_3x3().inverted().transposed()
            for poly in obj.data.polygons:
                point=obj.matrix_world@poly.center;normal=(normal_matrix@poly.normal).normalized()
                if height*.35<point.z<height*.70 and normal.z>.75:
                    candidates.append((point,max(poly.area,1e-10)))
        assert candidates,'No upward-facing seat region was found'
        seed=sum((point*area for point,area in candidates),Vector())/sum(area for point,area in candidates)
        hits=[];deps=bpy.context.evaluated_depsgraph_get()
        for obj in meshes:
            ev=obj.evaluated_get(deps);matrix=ev.matrix_world;origin=matrix.inverted()@Vector((seed.x,seed.y,height*.70))
            direction=matrix.to_3x3().inverted()@Vector((0,0,-1));hit,location,normal,index=ev.ray_cast(origin,direction)
            if hit:
                point=matrix@location
                if height*.35<point.z<height*.70:hits.append(point)
        assert hits,'Seat ray did not hit the actual model surface'
        add('seat_surface',max(hits,key=lambda p:p.z),'Downward ray onto the measured upward-facing seat region')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(folder/'model.blend'),compress=True)
    bpy.data.libraries.write(str(folder/'asset.blend'),{root.users_collection[0]},fake_user=True,compress=True)
    path=folder/'metadata.json';data=json.loads(path.read_text());data['anchors']=anchors
    data['anchor_limitations']='Bind-pose markers; bone parenting and action-specific contacts remain pending'
    assert hashlib.sha256(Path(data['source']).read_bytes()).hexdigest()==data['source_sha256']
    path.write_text(json.dumps(data,indent=2)+'\n');print('TRIPO_GEOMETRY_ANCHORS',asset,len(anchors))

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    for asset in args:
        root=REFS/asset if asset in ['barista','friend_locs'] else P.ROOT/asset
        run(asset,root/'tripo-generated/review')
