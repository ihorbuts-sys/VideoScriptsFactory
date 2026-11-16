"""Connected public café work shots and a real, stationary lights-on take."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_coffee_glass_batch as G
import build_shared_venue as C
import build_assets as P
import prepare_creator_tripo as B


def bind(guide, template, step, phase, capture, direction, action, channel,
         amount=None, turn=None, move_end=None, **extra):
    return dict(guide=guide, template=template, step=step, phase=phase,
        capture=capture, direction=direction, action=action, channel=channel,
        amount=amount, turn=turn, move_end=move_end, **extra)


CORNER = 'From your seated position, frame the supported cup, pastry and open laptop. Lean back slowly and slightly left, raising the phone a little to reveal the usable tabletop and window-side chair. Keep the same objects in view, settle, and end the take.'
ROOM = 'In the public aisle, turn your hips and phone slowly right from the counter toward the window-side work table. After the room take, walk two short steps to your chair and lower the phone into the seated table view shown next. Keep the lens fixed.'
DESK = 'From a seated eye position, show the laptop, cup and pastry together. Lean forward on a small diagonal toward the cup while lowering the phone gently. After the detail, rise back into the wider table view for the Wi-Fi-card handover.'
WIFI = 'From the table-edge view, tilt the phone down and lean slightly right toward the Wi-Fi card beside your laptop. Hold the card and its support clearly in view. This example uses the Wi-Fi-card option; it does not imply a socket exists below this table.'
LIGHTS = 'Ask staff before filming the opening routine. Hold the phone still at the public doorway with the pendant, tables and counter in frame. Record the practical lights switching on, then hold the lit room. Keep chairs and all fixtures in place.'


def card(table):
    """A small folded physical Wi-Fi card, with an icon and no invented code."""
    x, y = 1.48, 1.70
    z = C.surface(table, x, y)
    before = set(bpy.data.objects)
    # Two joined panels form a supported tent, rather than a floating sign.
    vertices = [(x+dx, y+dy, z+dz) for dx,dy,dz in
        [(-.052,-.035,.001),(.052,-.035,.001),(.052,0,.078),(-.052,0,.078),
         (-.052,.035,.001),(.052,.035,.001)]]
    mesh = bpy.data.meshes.new('Folded Wi-Fi card / two connected panels')
    mesh.from_pydata(vertices, [], [(0,1,2,3),(3,2,5,4)])
    mesh.update()
    obj = bpy.data.objects.new(mesh.name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(P.material('cream'))
    solid = obj.modifiers.new('Real folded card thickness', 'SOLIDIFY')
    solid.thickness = .0015
    bevel = obj.modifiers.new('Soft card edges', 'BEVEL')
    bevel.width = .001
    bevel.segments = 3
    # The icon is attached to the front inclined face; never a QR code.
    for radius in [.012, .023, .034]:
        pts = []
        for n in range(25):
            angle = math.radians(42 + n*96/24)
            dx, dz = radius*math.cos(angle), radius*math.sin(angle)
            zz = .024+dz
            yy = -.035 + zz*.035/.077 - .0018
            pts.append((x+dx,y+yy,z+zz))
        P.tube('Wi-Fi card / attached curved symbol', pts, .0017, 'teal')
    P.ball('Wi-Fi card / attached symbol dot',
           (x,y-.0258,z+.024),(.0027,.0019,.0027),'teal')
    root = P.group('Work table / supported Wi-Fi tent card', before)
    root['asset_family'] = 'wifi_card_local'
    root['construction'] = 'Folded card with physical support; no login or QR data'
    C.role(root, 'hero')
    for part in C.meshes(root):
        if 'attached' in part.name:
            part.color[0]=1
            part['semantic_detail']='wifi'
    C.CONTACTS.append(dict(asset='wifi_card_local',support=table.name,
        surface_z=z,lowest_vertex_z=z+.00025,centre_contact_error_m=.00025))
    return root


def work_setup(scene, key, row):
    P.MATS.clear()
    bpy.ops.object.select_all(action='DESELECT')
    C.CACHE.clear()
    C.CONTACTS.clear()
    table = next(o for o in scene.objects if o.get('asset_family')=='dining_table')
    # This is one person's working table: clear the unused far place setting.
    cleared=[o for o in scene.objects if o.get('asset_family') in ['saucer','latte_cup'] and 1.6<o.location.y<2]
    for obj in cleared:G.remove(obj)
    laptop = C.supported('laptop',table,.99,1.67,turn=0)
    C.role(laptop,'hero')
    wifi = card(table)
    cup = next(o for o in scene.objects if o.get('asset_family')=='latte_cup' and o.location.y<1.6)
    pastry = next(o for o in scene.objects if o.get('asset_family')=='croissant' and o.location.y<1.6)
    if key=='work-corner':
        G.remove(pastry)
        plate=next(o for o in scene.objects if o.get('asset_family')=='saucer' and abs(o.location.x-1.02)<.01)
        pastry=C.supported('croissant_oozing',plate,1.02,1.35,scale=.8,turn=-.35,quality='approved-v2')
        for obj in pastry.children_recursive:
            if obj.name.startswith('Filling / restrained chocolate core'):
                obj.scale.y*=1.4;obj.scale.z*=2.2
    for root in [cup,pastry,table]:C.role(root,'hero' if root!=table else 'support')
    bpy.context.view_layer.update()
    lo,hi = B.bounds(C.meshes(laptop))
    assert .25<hi.x-lo.x<.34 and hi.z<1.02,(list(lo),list(hi))
    assert lo.x>.65 and hi.x<1.65 and lo.y>1.18 and hi.y<1.92
    # Independent horizontal footprints must not intersect.
    bounds = {root.name:B.bounds(C.meshes(root)) for root in [laptop,wifi,cup,pastry]}
    names=list(bounds)
    for i,name in enumerate(names):
        a,b=bounds[name]
        for other in names[i+1:]:
            c,d=bounds[other]
            assert b.x<c.x or d.x<a.x or b.y<c.y or d.y<a.y,(name,other)
    scene.camera.data.lens=23
    if key=='work-corner':
        scene.camera.data.lens=23
        path=[(0,(1.16,.78,1.26),(1.19,1.52,.80)),
              (.8,(1.16,.78,1.26),(1.19,1.52,.80)),
              (6.5,(.96,.55,1.38),(1.19,1.53,.90)),
              (8.0,(.96,.55,1.38),(1.19,1.53,.90))]
    else:
        path=[(0,(-.12,1.14,1.48),(-.30,4.4,1.55)),
              (.7,(-.12,1.14,1.48),(-.30,4.4,1.55)),
              (3.8,(-.08,1.15,1.48),(2.5,3.7,1.45)),
              (4.3,(-.08,1.15,1.48),(2.5,3.7,1.45)),
              (7,(1.16,.78,1.26),(1.19,1.52,.80)),
              (7.7,(1.16,.78,1.26),(1.19,1.52,.80)),
              (11.5,(1.33,1.12,1.04),(1.39,1.36,.755)),
              (12,(1.33,1.12,1.04),(1.39,1.36,.755)),
              (14,(1.32,.98,1.22),(1.03,1.67,.93)),
              (14.7,(1.32,.98,1.22),(1.03,1.67,.93)),
              (17.5,(1.48,1.35,1.15),(1.48,1.70,.75)),
              (19,(1.48,1.35,1.15),(1.48,1.70,.75))]
    return path,list(C.CONTACTS)


def lights_setup(scene,key,row):
    P.MATS.clear()
    # This shot records a staff-operated switch. Lights do not travel or pulse.
    practical=[]
    for obj in scene.objects:
        if obj.type=='LIGHT' and obj.name.startswith(('Table / fixed pendant','Wall / fixed soft practical','Shelf / fixed warm wash')):
            target=obj.data.energy
            obj.data=obj.data.copy()
            for seconds,power in [(0,0),(1.2,0),(1.45,target),(6.5,target)]:
                obj.data.energy=power;obj.data.keyframe_insert('energy',frame=round(seconds*15)+1)
            practical.append(obj.name)
    diffusers=[o for o in scene.objects if o.type=='MESH' and
        o.name.startswith(('Pendant / warm opal diffuser','Wall / warm frosted globe'))]
    for obj in diffusers:
        obj.color=(.05,1,0,1)
        for seconds,power in [(0,0),(1.2,0),(1.45,1),(6.5,1)]:
            # B is a localized warm-light field, ignored by old glass scenes.
            obj.color[2]=power;obj.keyframe_insert('color',frame=round(seconds*15)+1)
        obj['guide_role']='hero'
        obj.data=obj.data.copy()
        mat=obj.data.materials[0].copy()
        obj.data.materials.clear();obj.data.materials.append(mat)
        shader=mat.node_tree.nodes.get('Principled BSDF')
        if shader:
            shader.inputs['Emission Color'].default_value=(1,.63,.20,1)
            for seconds,power in [(0,0),(1.2,0),(1.45,.8),(6.5,.8)]:
                shader.inputs['Emission Strength'].default_value=power
                shader.inputs['Emission Strength'].keyframe_insert('default_value',frame=round(seconds*15)+1)
    assert practical and diffusers
    scene.camera.data.lens=18
    row['lighting_checks']=dict(practicals=practical,diffusers=[o.name for o in diffusers],switch_seconds=[1.2,1.45])
    return [(0,(-1.70,.50,1.40),(1.05,2.80,1.50)),
            (6.5,(-1.70,.50,1.40),(1.05,2.80,1.50))],[]


SCENES={
    'work-corner':dict(duration=8,guide='table_corner_pov_out_mw',template='cafe-morning-ritual',step='corner',
        title='Your corner / seated table reveal',capture=7,freeze=True,setup=work_setup,direction=CORNER,
        bindings=[bind('table_corner_pov_out_mw','cafe-morning-ritual','corner','shot',7,CORNER,'dolly_out','image_scale',.65,move_end=6.5)]),
    'work-route':dict(duration=19,guide='room_eye_panr_ww_whipout',template='cafe-work-spot',step='room',
        title='Work spot / room to desk to Wi-Fi',capture=4,freeze=True,setup=work_setup,direction=ROOM,
        probe_frames=[1,58,106,173,211,264,285],
        phases=[dict(id='room',start_s=0,end_s=7,capture_seconds=4,handover_seconds=3,handover_tail_seconds=0),
                dict(id='desk',start_s=7,end_s=14,capture_seconds=5,handover_seconds=2,handover_tail_seconds=0),
                dict(id='wifi',start_s=14,end_s=19,capture_seconds=4,handover_seconds=0)],
        bindings=[bind('room_eye_panr_ww_whipout','cafe-work-spot','room','room',4,ROOM,'pan','gyro_yaw',.85,'right',3.8,update_global=False),
                  bind('table_desk_pov_in_mc','cafe-work-spot','desk','desk',5,DESK,'dolly_in','image_scale',1.6,move_end=4.5),
                  bind('table_outlets_high_tiltd_cc','cafe-work-spot','outlets','wifi',4,WIFI,'tilt','gravity_tilt',.35,'down',3.5)]),
    'lights-on':dict(duration=6.5,guide='room_lights_eye_hold',template='cafe-before-opening',step='lights',
        title='Lights on / a stationary opening take',capture=5.2,freeze=True,locked_camera=True,setup=lights_setup,direction=LIGHTS,
        lighting_action='Staff switches practical lights on once at 1.2 seconds. Window light and fixture positions stay fixed. No bloom, flashing or moving lamps.',
        probe_frames=[1,16,24,48,98],
        bindings=[bind('room_lights_eye_hold','cafe-before-opening','lights','shot',5.2,LIGHTS,'still',None,move_end=3.2,subject_motion='lights on',update_global=False)]),
}
for row in SCENES.values():
    row['revision']='coffee-work-glass-v1'
    row['composition']=['One usable work setting: laptop at the far side, cup to the right and pastry to the left',
        'Shared physical table and camera endpoints for room, desk and Wi-Fi handovers',
        'No invented hand performance or unrelated scene appended to the take']


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--scene',choices=SCENES);parser.add_argument('--build',action='store_true');parser.add_argument('--probes',action='store_true');parser.add_argument('--resume',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    G.SCENES.update(SCENES)
    for key in [args.scene] if args.scene else ['lights-on','work-corner','work-route']:
        if args.build:
            scene,spec,folder=G.build(key)
            spec.update(scope='connected_step_sequence' if key=='work-route' else 'complete_final_shot',
                handover_status='continuous_same_room' if key=='work-route' else 'cut_to_next_step')
            if key=='lights-on':spec['lighting_checks']=SCENES[key]['lighting_checks']
            if key=='work-route':
                spec['generation_credits_used']=40
                spec['new_reusable_models']=['laptop']
            if key!='lights-on':
                from bpy_extras.object_utils import world_to_camera_view
                scene.frame_set(106 if key=='work-route' else 1)
                bpy.context.view_layer.update()
                fits=[]
                for root in scene.objects:
                    if root.get('asset_family') in ['laptop','latte_cup','croissant','croissant_oozing'] and root.location.y<2:
                        pts=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for o in C.meshes(root) for v in o.data.vertices]
                        bounds=[min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)]
                        assert all(.005<v<.995 for v in bounds),(root.name,bounds)
                        fits.append(dict(object=root.name,normalized_bounds=bounds))
                spec['table_start_framing']=fits
            (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        if args.probes or not args.build:G.render(key,args.probes,args.resume)
