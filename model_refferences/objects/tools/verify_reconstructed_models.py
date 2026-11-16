"""Native checks for mesh closure, winding, calibrated size and separate halves."""
import bpy,bmesh,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_assets as P
ROOT=P.ROOT
ASSETS=['croissant','croissant_oozing','dining_chair','dining_table','latte_cup','saucer','bar_counter','bar_stool','wall_shelf','bottle','drinking_glass','rack_shelf_tray','pastry_rack']

def run():
    results=[]
    for asset in ASSETS:
        P.clear();path=ROOT/asset/'reconstructed/asset.blend'
        with bpy.data.libraries.load(str(path),link=False) as (s,d):d.collections=[s.collections[0]]
        collection=d.collections[0];bpy.context.scene.collection.children.link(collection)
        root=next(o for o in collection.objects if o.get('asset_id')==asset)
        objects=[o for o in root.children_recursive if o.type=='MESH'];records=[]
        for mesh in objects:
            bm=bmesh.new();bm.from_mesh(mesh.data);volume=bm.calc_volume(signed=True)
            boundary=sum(e.is_boundary for e in bm.edges)
            assert volume>0,(asset,'Inward-facing normals');assert boundary==0,(asset,'Open reconstructed mesh')
            records.append(dict(name=mesh.name,vertices=len(bm.verts),faces=len(bm.faces),volume_m3=volume,boundary_edges=boundary))
            bm.free()
        if asset=='croissant_oozing':assert len(objects)==2
        lo,hi=P.bounds(objects)
        tolerance=.005 if asset in ['bar_counter','bar_stool','wall_shelf','rack_shelf_tray'] else .001
        assert abs(lo.z)<tolerance,(asset,'Support origin exceeds clay cleanup tolerance',lo.z)
        if asset in ['dining_table','dining_chair','latte_cup','saucer','bar_counter','bar_stool','bottle','drinking_glass']:
            target=P.ASSETS[asset][2][2] if hasattr(P,'ASSETS') else None
            assert abs(hi.z-target)<max(.002,tolerance),(asset,'Wrong calibrated height')
        results.append(dict(asset=asset,geometry='passed',bounds_min=list(lo),bounds_max=list(hi),
            support_origin_error_m=abs(lo.z),support_origin_tolerance_m=tolerance,parts=records))
    (ROOT/'reconstructed-geometry-checks.json').write_text(json.dumps(dict(status='passed',assets=len(results),checks=results),indent=2)+'\n')
    print('RECONSTRUCTED_GEOMETRY_CHECKS_PASSED',len(results))

if __name__=='__main__':run()
