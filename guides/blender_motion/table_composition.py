"""Keep personal dishes at usable place settings, away from the centre of dining tables."""
import bpy,math
from mathutils import Vector
from audit_place_settings import inspect


def is_hand(obj):
    while obj is not None:
        if obj.get('visible_hand_count'):return True
        obj=obj.parent
    return False


def enforce(scene):
    before=inspect(scene);changes=[]
    for table_name in dict.fromkeys(row['table'] for row in before if row['too_central']):
        rows=[row for row in before if row['table']==table_name];table=bpy.data.objects[table_name]
        root=table.parent
        assert root and root.name.startswith('Reusable table'),'Review a custom dining table explicitly: '+table_name
        assert not root.animation_data,'Never move an animated table automatically'
        radius=rows[0]['table_radius_m'];centre=Vector((*rows[0]['table_xy'],0));candidates=[]
        tabletop_z=max((table.matrix_world@v.co).z for v in table.data.vertices)
        supported=[]
        for obj in scene.objects:
            if obj.type!='MESH' or obj==table or is_hand(obj):continue
            vertices=[obj.matrix_world@v.co for v in obj.data.vertices]
            low=min(v.z for v in vertices);high=max(v.z for v in vertices)
            if -.003<=low-tabletop_z<=.025 and high-low<.22 and all((v.xy-centre.xy).length<radius+.005 for v in vertices):
                supported.append((obj.name,[v.xy.copy() for v in vertices]))
        for dx in [-.20,-.15,-.10,-.05,0,.05,.10,.15,.20]:
            for dy in [.42,.45,.48,.50,.52,.55,.58,.60,.62]:
                shift=Vector((dx*radius,dy*radius,0));offsets=[(Vector((*row['plate_xy'],0))-centre-shift).length for row in rows]
                # Each entire plate remains on the table, with edge clearance and a clear shared middle.
                if not all(.42*radius<=distance<=radius-.165 for distance in offsets):continue
                if not all((point-centre.xy-shift.xy).length<=radius+.005 for _,points in supported for point in points):continue
                score=(dx*2)**2+(dy-.50)**2
                candidates.append((score,shift,offsets))
        assert candidates,'No safe plate arrangement found for '+table_name
        _,shift,offsets=min(candidates,key=lambda row:row[0]);matrix=root.matrix_world.copy();matrix.translation+=shift;root.matrix_world=matrix
        root['place_setting_policy']='Personal plates off centre, fully supported, with a clear table middle'
        changes.append(dict(table=table_name,root=root.name,shift_xy_m=list(shift.xy),plate_offsets_m=offsets,supported_meshes_kept_on_table=[name for name,_ in supported],reason='Move the tabletop relative to the complete existing place setting; food, utensils, cups and contact actions remain coherent'))
        bpy.context.view_layer.update()
    after=inspect(scene)
    assert not any(row['too_central'] for row in after),'A centred personal plate remains'
    return dict(policy='No personal dish at the table centre',changes=changes,plates=after,status='passed')
