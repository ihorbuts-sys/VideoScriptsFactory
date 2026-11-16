"""Read-only inventory of support and chair continuity in the published native projects."""
import bpy
import json
from pathlib import Path
from mathutils import Vector

BASE=Path(__file__).resolve().parents[2]
OUT=BASE/'catalog/continuity-audit'
rows=json.loads((BASE/'catalog/blender-animations/index.json').read_text())['shots']
results=[]
for row in rows:
    if not row['reviewed']:continue
    gid=row['id'];folder=BASE/'catalog/blender-animations'/gid
    spec=json.loads((folder/'scene-spec.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene=bpy.data.scenes['01 Ghost contours'];bpy.context.window.scene=scene
    samples=[1,max(1,spec['frame_count']//3),max(1,2*spec['frame_count']//3),spec['frame_count']]
    moving=[];chairs=[]
    for obj in scene.objects:
        if obj.type in ['CAMERA','LIGHT'] or not obj.animation_data:continue
        positions=[]
        for f in samples:scene.frame_set(f);bpy.context.view_layer.update();positions.append(obj.matrix_world.translation.copy())
        span=max(p.z for p in positions)-min(p.z for p in positions)
        if span<.035:continue
        relatives=[obj,*obj.children_recursive];parent=obj.parent
        while parent:relatives.append(parent);parent=parent.parent
        held=any(o.get('visible_hand_count') for o in relatives)
        if not held and not any(word in obj.name.lower() for word in ['steam','liquid','yolk','rosetta','pour','curl']):
            moving.append(dict(object=obj.name,vertical_travel_m=span,visible_gripping_hand=False))
    scene.frame_set(1);bpy.context.view_layer.update()
    for obj in scene.objects:
        if not obj.name.startswith('Reusable dining chair'):continue
        table=obj.parent
        if not table or not table.name.startswith('Two-person dining table'):continue
        back=next(o for o in obj.children_recursive if o.name.startswith('Dining chair bent back'))
        centre=sum((Vector(v) for v in back.bound_box),Vector())/8
        toward=(table.matrix_world.translation-obj.matrix_world.translation).xy.normalized()
        offset=(back.matrix_world@centre-obj.matrix_world.translation).xy.normalized()
        alignment=offset.dot(toward)
        chairs.append(dict(chair=obj.name,backrest_alignment_toward_table=alignment,facing_table=alignment<-.95))
    result=dict(id=gid,unheld_vertical_motion_candidates=moving,dining_chairs=chairs,
                source_sha256=__import__('hashlib').sha256((folder/'guide.png').read_bytes()).hexdigest())
    results.append(result)
    print('CONTINUITY_AUDIT',gid,'candidates',len(moving),'reversed chairs',sum(not c['facing_table'] for c in chairs),flush=True)
OUT.mkdir(exist_ok=True)
(OUT/'native-scene-inventory.json').write_text(json.dumps(results,indent=2)+'\n')
