"""Reusable café shots built from the approved counter scene and real props."""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_assets as P
import build_shared_venue as C
import prepare_creator_tripo as B
from build_reconstructed_scene import mask_material
from render_coffee_hologram import material as field_material

ROOT = P.BASE / 'catalog/glass-rollout/coffee'
SOURCE = P.BASE / 'catalog/coffee-ordering-v2/scene.blend'
FPS = 15

SCENES = {
    'order': dict(duration=8, guide='over_shoulder_counter_os_hold', template='cafe-first-visit', step='counter',
        title='Order / customer-side counter', capture=7.2, freeze=False,
        path=[(0,(.65,2.25,1.50),(.65,4.25,1.60)),(1,(.65,2.25,1.50),(.65,4.25,1.60)),
              (6.3,(1.0,2.43,1.54),(.80,4.25,1.60)),(8,(1.0,2.43,1.54),(.80,4.25,1.60))],
        direction='Stay on the customer side. Frame the menu and barista above the machine, then move the phone in a short diagonal arc while the espresso brews. Hold the final view and cut to the next step.'),
    'menu-to-cup': dict(duration=5.2, guide='menu_board_low_tiltd_mm', template='cafe-seasonal-drink', step='board',
        title='Menu board to the drink', capture=4, freeze=False,
        path=[(0,(.45,2.75,1.26),(-.035,5.15,2.58)),(.8,(.45,2.75,1.26),(-.035,5.15,2.58)),
              (3.7,(1.05,3.00,1.47),(.69,4.095,1.12)),(5.2,(1.05,3.00,1.47),(.69,4.095,1.12))],
        direction='From the customer aisle, frame the menu board from a slightly low angle. Tilt down while leaning a little right and forward until the same counter drink fills the lower view. Hold, then cut.'),
    'cup-out': dict(duration=6.2, guide='cup_high_out_dm', template='cafe-before-opening', step='door',
        title='Finished espresso / rising reveal', capture=5, freeze=True,
        path=[(0,(.93,3.62,1.36),(.69,4.095,1.105)),(.7,(.93,3.62,1.36),(.69,4.095,1.105)),
              (4.8,(1.47,2.94,1.63),(.76,4.13,1.21)),(6.2,(1.47,2.94,1.63),(.76,4.13,1.21))],
        direction='Keep the filled cup on the machine tray. From the customer side, move back on a short curve and raise the phone slightly to reveal the barista and counter around the same cup. Hold and cut.'),
    'cup-orbit': dict(duration=5.5, guide='cup_eye_orbitr_cc', template='food-review-drink', step='cup',
        title='Coffee cup / eye-level orbit', capture=4, freeze=True, table=True,
        path=None,
        direction='At the off-centre place setting, keep the cup and neighbouring pastry supported. Circle the phone gently to the right while raising it slightly so the handle and far side come around. Hold and cut.'),
    'morning-pair': dict(duration=10, guide='cup_eye_hold_whipout', template='cafe-morning-ritual', step='cup',
        title='Coffee and pastry / connected detail', capture=5, freeze=True, table=True, broken=True,
        path=None,
        direction='Start at cup height with the opened pastry on its plate beside the cup. Rise and lean diagonally to reveal both, then move toward the pastry in the same continuous shot. Keep all food supported.'),
    'morning-room': dict(duration=6.5, guide='interior_pan', template='cafe-morning-ritual', step='light',
        title='Morning room / window to counter', capture=5, freeze=True,
        path=[(0,(-.55,1.38,1.50),(2.60,3.80,1.55)),(.7,(-.55,1.38,1.50),(2.60,3.80,1.55)),
              (5.0,(-.50,1.42,1.52),(.15,4.15,1.45)),(6.5,(-.50,1.42,1.52),(.15,4.15,1.45))],
        direction='Stand in the public aisle. Start on the full-height window, then turn your body smoothly toward the tables, pendant and counter. Keep the phone near chest height. The window light stays fixed.'),
    'entrance': dict(duration=5.5, guide='entrance_inside_eye_in_wm', template='cafe-first-visit', step='entrance',
        title='Arrive / turn toward the entrance', capture=4, freeze=True,
        path=[(0,(-.20,2.30,1.47),(-.80,.15,1.35)),(.7,(-.20,2.30,1.47),(-.80,.15,1.35)),
              (4.0,(-.85,1.45,1.50),(-1.30,.04,1.35)),(5.5,(-.85,1.45,1.50),(-1.30,.04,1.35))],
        direction='From inside the public room, turn gently toward the glazed entrance and take one slow step toward it. Let the same door grow from wide to medium, then hold and cut to the counter.'),
}


def remove(root):
    for obj in list(root.children_recursive)[::-1] + [root]:
        bpy.data.objects.remove(obj, do_unlink=True)


def centre(root):
    lo, hi = B.bounds(C.meshes(root))
    return (lo + hi) / 2


def build(key):
    row = SCENES[key]
    folder = ROOT / key
    folder.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    scene.frame_set(240 if row['freeze'] else 1)
    if row['freeze']:
        for obj in scene.objects:
            obj.animation_data_clear()
    camera = scene.camera
    camera.animation_data_clear()
    camera.data.animation_data_clear()
    camera.data.lens = 32
    scene.render.resolution_x, scene.render.resolution_y = 405, 720
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    count = round(row['duration'] * FPS)
    scene.frame_end = count
    contacts = []
    if row.get('setup'):
        path, contacts = row['setup'](scene, key, row)
    elif row.get('table'):
        # Use the same table and calibrated supports as the reviewed café set.
        table = next(o for o in scene.objects if o.get('asset_family') == 'dining_table')
        cups = [o for o in scene.objects if o.get('asset_family') == 'latte_cup' and o.location.y < 2.5]
        cup = min(cups, key=lambda o:(centre(o)-Vector((1.39,1.36,.8))).length)
        pastries = [o for o in scene.objects if o.get('asset_family') == 'croissant' and o.location.y < 2.5]
        pastry = min(pastries, key=lambda o:(centre(o)-Vector((1.02,1.35,.8))).length)
        if row.get('broken'):
            for obj in pastries:
                remove(obj)
            plates = [o for o in scene.objects if o.get('asset_family') == 'saucer']
            plate = min(plates, key=lambda o:(centre(o)-Vector((1.02,1.35,.8))).length)
            C.CACHE.clear()
            pastry = C.supported('croissant_oozing', plate, 1.02, 1.35,
                                  scale=.80, turn=-.35, quality='approved-v2')
            for obj in pastry.children_recursive:
                if obj.name.startswith('Filling / restrained chocolate core'):
                    obj.scale.y *= 1.4
                    obj.scale.z *= 2.2
            contacts += C.CONTACTS
        C.role(cup, 'hero')
        C.role(pastry, 'hero')
        ct, pt = centre(cup), centre(pastry)
        if key == 'cup-orbit':
            camera.data.lens = 36
            path = []
            for t, angle, height in [(0,-40,.055),(.6,-40,.055),(4,15,.14),(5.5,15,.14)]:
                a = math.radians(angle)
                path.append((t, tuple(ct+Vector((.52*math.sin(a),-.52*math.cos(a),height))),tuple(ct)))
        else:
            pair = (ct+pt)/2
            path = [(0,tuple(ct+Vector((.12,-.48,.07))),tuple(ct)),
                    (.6,tuple(ct+Vector((.12,-.48,.07))),tuple(ct)),
                    (4.0,tuple(pair+Vector((.10,-.66,.45))),tuple(pair)),
                    (5.0,tuple(pair+Vector((.10,-.66,.45))),tuple(pair)),
                    (6.3,tuple(pt+Vector((-.24,-.36,.23))),tuple(pt)),
                    (8.4,tuple(pt+Vector((-.16,-.34,.30))),tuple(pt)),
                    (10,tuple(pt+Vector((-.16,-.34,.30))),tuple(pt))]
        for prop in [cup,pastry]:
            p = centre(prop)
            assert math.hypot(p.x-table.location.x,p.y-table.location.y) > .14
    else:
        path = row['path']
        if key == 'menu-to-cup':
            menu = next(o for o in scene.objects if o.get('asset_family')=='menu_board')
            C.role(menu,'hero')
            menu_centre = tuple(centre(menu))
            path = [(t,p,menu_centre if t<1 else q) for t,p,q in path]
        elif key=='entrance':
            C.role(next(o for o in scene.objects if o.get('asset_family')=='glazed_door'),'hero')
        elif key=='morning-room':
            windows=[o for o in scene.objects if o.get('asset_family')=='window']
            C.role(max(windows,key=lambda o:o.location.y),'hero')
    samples = []
    previous_position = previous_rotation = None
    max_speed = max_turn = 0
    for frame in range(1,count+1):
        t = (frame-1)/FPS
        if row.get('sample_camera'):
            position,target=row['sample_camera'](t)
        else:
            position = C.cubic([(a,b) for a,b,_ in path],t)
            target = C.cubic([(a,c) for a,_,c in path],t)
        if not row.get('locked_camera'):
            position.z += .0015*math.sin(t*1.7)
        assert position.y < 3.7, ('Phone enters staff space',key,list(position))
        assert position.z > .75
        assert (target-position).length > .25
        rotation = (target-position).to_track_quat('-Z','Y')
        if previous_rotation and rotation.dot(previous_rotation) < 0:
            rotation.negate()
        camera.location = position
        camera.rotation_mode = 'QUATERNION'
        camera.rotation_quaternion = rotation
        camera.keyframe_insert('location',frame=frame)
        camera.keyframe_insert('rotation_quaternion',frame=frame)
        if previous_position is not None:
            max_speed = max(max_speed,(position-previous_position).length*FPS)
            max_turn = max(max_turn,math.degrees(previous_rotation.rotation_difference(rotation).angle)*FPS)
        previous_position, previous_rotation = position.copy(),rotation.copy()
        samples.append(dict(frame=frame,position=list(position),target=list(target)))
    assert max_speed < .9, (key,max_speed)
    assert max_turn < 85, (key,max_turn)
    phase_id = 'shot'
    phases = [dict(id=phase_id,start_s=0,end_s=row['duration'])]
    if key == 'morning-pair':
        phases = [dict(id='cup',start_s=0,end_s=5),dict(id='pastry',start_s=5,end_s=10)]
    phases = row.get('phases', phases)
    spec = dict(id=key,title=row['title'],venue='coffee',fps=FPS,frame_count=count,
        duration_s=count/FPS,scope='shot_and_handover' if key=='morning-pair' else 'complete_final_shot',
        handover_status='continuous_same_table' if key=='morning-pair' else 'cut_to_next_step',
        full_script_sequence_complete=False,source_scene=str(SOURCE.relative_to(P.BASE)),
        guide=row['guide'],template=row['template'],step=row['step'],capture_seconds=row['capture'],
        direction=row['direction'],phases=phases,probe_frames=sorted(set([1,round(count*.25),round(count*.5),round(count*.75),count])),
        color_resolution=[405,720],ghost_resolution=[405,720],revision=row.get('revision','coffee-glass-rollout-v1'),
        ghost_style='hologram-glass-v1',composition=['Same approved café set and reusable Tripo assets',
            'Off-centre supported props and usable two-person table settings','Continuous position, pitch and yaw changes',
            'Phone remains in public space'],lighting='Fixed window and practical lights; no scene bloom',
        mobile=row['direction'],contacts=contacts,
        camera=dict(max_speed_m_s=max_speed,max_turn_deg_s=max_turn,samples=samples),
        display=dict(opacity_mode='image_view',image_opacity=.65,background_delay_seconds=2,
                     viewfinder='separate_ui_layer',walls=False,floor=False,ceiling=False))
    if row.get('bindings'):
        spec['guide_bindings'] = row['bindings']
    if row.get('lighting_action'):
        spec['lighting_action'] = row['lighting_action']
        spec['lighting'] = row['lighting_action']
    spec['composition'] += row.get('composition', [])
    spec['probe_frames'] = row.get('probe_frames', spec['probe_frames'])
    scene.frame_set(1)
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
    print('COFFEE_GUIDE_BUILT',key,count,flush=True)
    return scene,spec,folder


def render(key, probes, resume=False, modes=None):
    folder = ROOT/key
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'))
    scene = bpy.context.scene
    spec = json.loads((folder/'scene-spec.json').read_text())
    if spec.get('denoise_color'):
        tree=bpy.data.node_groups.new('Loca / guided color denoising','CompositorNodeTree')
        tree.interface.new_socket(name='Image',in_out='OUTPUT',socket_type='NodeSocketColor')
        layer=scene.view_layers[0]
        layer.use_pass_normal=True;layer.use_pass_diffuse_color=True
        source=tree.nodes.new('CompositorNodeRLayers')
        denoise=tree.nodes.new('CompositorNodeDenoise')
        output=tree.nodes.new('NodeGroupOutput')
        tree.links.new(source.outputs['Image'],denoise.inputs['Image'])
        for field,slot in [('Normal','Normal'),('DiffCol','Albedo')]:
            if source.outputs.get(field) and denoise.inputs.get(slot):
                tree.links.new(source.outputs[field],denoise.inputs[slot])
        tree.links.new(denoise.outputs['Image'],output.inputs['Image'])
        scene.compositing_node_group=tree
        scene.render.use_compositing=True
        scene.eevee.taa_render_samples=spec.get('color_samples',16)
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'),compress=True)
    masks, fields = mask_material(),field_material()
    originals = {o:o.hide_render for o in scene.objects}
    excluded = [o.name for o in scene.objects if o.get('ghost_role')=='absent' or o.name.startswith('Room shell /')]
    mounted = [o.name for o in scene.objects if o.get('asset_family') in ['wall_shelf','menu_board','wall_sconce_local']]
    (folder/'architecture-exclusion.json').write_text(json.dumps(dict(
        walls_and_floor_hidden=True,excluded_objects=excluded,mounted_objects_retained=mounted),indent=2)+'\n')
    numbers = spec['probe_frames'] if probes else range(1,spec['frame_count']+1)
    static=spec.get('cache_static_camera_frames',False)
    if static:
        assert not any(o.animation_data and o.animation_data.action for o in scene.objects if o!=scene.camera)
    reused=0
    modes=modes or ['color','mask','fields']
    for mode in modes:
        poses={}
        if spec.get('denoise_color'):scene.render.use_compositing=mode=='color'
        path = folder/(('probes-' if probes else '')+mode)
        path.mkdir(exist_ok=True)
        scene.view_layers[0].material_override = None if mode=='color' else masks if mode=='mask' else fields
        scene.view_settings.view_transform = 'AgX' if mode=='color' else 'Standard'
        scene.view_settings.exposure = -.1 if mode=='color' else 0
        scene.eevee.taa_render_samples = spec.get('color_samples',16) if mode=='color' else 8
        for obj,hidden in originals.items():
            obj.hide_render = hidden or (mode!='color' and
                (obj.get('glazing') or obj.get('ghost_role')=='absent' or obj.name.startswith('Room shell /') or obj.type=='LIGHT'))
            if mode=='fields' and obj.type=='MESH':
                obj.data.polygons.foreach_set('use_smooth',[True]*len(obj.data.polygons))
        for frame in numbers:
            target=path/f'frame_{frame:04d}.png'
            if resume and target.exists() and target.stat().st_size>1000:
                with target.open('rb') as file:
                    header=file.read(24)
                if header[:8]==b'\x89PNG\r\n\x1a\n' and int.from_bytes(header[16:20],'big')==405 and int.from_bytes(header[20:24],'big')==720:
                    continue
            scene.frame_set(frame)
            if static:
                pose=tuple(round(v,8) for row in scene.camera.matrix_world for v in row)+(scene.camera.data.lens,)
                if pose in poses:
                    target.unlink(missing_ok=True)
                    os.link(poses[pose],target)
                    reused+=1
                    continue
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True)
            if static:poses[pose]=target
    print('COFFEE_GUIDE_RENDERED',key,'probes' if probes else 'full',flush=True)
    if not probes:
        (folder/'render-ready.json').write_text(json.dumps(dict(status='ready',frames=spec['frame_count'],
            resolution=[405,720],color_samples=spec.get('color_samples',16),ghost_fields_samples=8,
            color_denoised=bool(spec.get('denoise_color')),
            rendered_passes=modes,reused_identical_static_frames=reused),indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',action='store_true');p.add_argument('--probes',action='store_true');p.add_argument('--scene',choices=SCENES);p.add_argument('--scenes');p.add_argument('--resume',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    keys=a.scenes.split(',') if a.scenes else [a.scene] if a.scene else list(SCENES)
    assert all(key in SCENES for key in keys)
    for key in keys:
        if a.build:build(key)
        if a.probes or not a.build:render(key,a.probes,a.resume)
