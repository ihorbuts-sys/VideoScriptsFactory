"""Measure resting dinner plates against their actual dining tabletop, without changing projects."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))

def inspect(scene):
    scene.frame_set(1);bpy.context.view_layer.update();tables=[]
    for obj in scene.objects:
        if obj.type!='MESH' or not obj.name.startswith('Quiet tabletop'):continue
        vertices=[obj.matrix_world@v.co for v in obj.data.vertices];centre=obj.matrix_world@Vector((0,0,0))
        radius=max((v.xy-centre.xy).length for v in vertices);tables.append((obj,centre,radius,max(v.z for v in vertices)))
    rows=[]
    for plate in scene.objects:
        if plate.type!='MESH' or not plate.name.startswith('Plate with formed rim'):continue
        point=plate.matrix_world.translation;bottom=min((plate.matrix_world@v.co).z for v in plate.data.vertices)
        candidates=[(table,centre,radius,top) for table,centre,radius,top in tables if -.004<=bottom-top<.05 and (point.xy-centre.xy).length<radius]
        if not candidates:continue
        table,centre,radius,top=min(candidates,key=lambda row:(point.xy-row[1].xy).length)
        distance=(point.xy-centre.xy).length
        rows.append(dict(plate=plate.name,table=table.name,table_parent=table.parent.name if table.parent else None,plate_xy=list(point.xy),table_xy=list(centre.xy),table_radius_m=radius,offset_m=distance,offset_ratio=distance/radius,too_central=distance<radius*.42))
    return rows

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);root=BASE/'catalog/blender-animations';work=json.loads((BASE/'guides/blender_motion/work-plan.json').read_text());ids=[row['id'] for row in work['guides'] if row['status']!='deferred_people'];results=[]
    for gid in ids:
        folder=root/gid;spec=json.loads((folder/'scene-spec.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'));scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
        rows=inspect(scene);results.append(dict(guide=gid,plates=rows,needs_correction=any(row['too_central'] for row in rows)))
    out.parent.mkdir(exist_ok=True,parents=True);out.write_text(json.dumps(results,indent=2)+'\n');print('PLACEMENT_AUDIT',len(results),'scenes;',sum(row['needs_correction'] for row in results),'with plates too close to table centre',flush=True)
