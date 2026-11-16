"""Three practical commercial shot lessons, without character or hand animation."""
import argparse,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_coffee_glass_batch as G
import build_shared_venue as C
import build_assets as P
import prepare_creator_tripo as B
from build_primary_food_scenes import soften_background
from build_coffee_work_guides import bind

DISPLAY='From the customer aisle, hold the phone level with the pastry row. Take one slow sideways step left, keeping the same distance from the case. Let the repeated pastries pass through the frame, finish on one clear group and hold. Keep the lens fixed; include the real labels when they are readable.'
TEXTURE='Put the already opened pastry on a plate at your place setting, with the cut faces toward the window and camera. Start just above the plate, then move through a short left arc while raising the phone a little. Reveal the filling and both halves together, keep the pastry still and hold. Cut after the detail.'
ROOM='From the public aisle beside the table, start with the near chair at the edge of the frame. Take one small diagonal step back and right while raising the phone from chest toward eye height. Reveal the same table for two, its window light and the room behind it. Keep the lens fixed and settle before cutting.'


def setup(scene,key,row):
    P.MATS.clear();C.CACHE.clear();C.CONTACTS.clear()
    removed=[o for o in scene.objects if o.get('asset_family') in ['creator','barista','friend','friend_locs','milk_pitcher','portafilter','espresso_stream_local']]
    roots=[o for o in removed if not any(p in removed for p in parents(o))]
    for root in roots:G.remove(root)
    assert not any(o.type=='ARMATURE' for o in scene.objects),'No human rig belongs in this batch'
    soften_background(scene)
    if key=='commercial-display':
        subject=next(o for o in scene.objects if o.get('asset_family')=='display_case')
        C.role(subject,'hero');scene.camera.data.lens=35
        start=Vector((1.35,2.55,1.18));end=Vector((.45,2.60,1.23))
        first=Vector((.90,4.02,.80));last=Vector((.35,4.02,.80))
        row['hero_family']='display_case';row['fits_entire_subject']=False
        row['staging']=['Use the customer-facing pastry row, with repeated trays creating rhythm',
            'Keep real prices visible when legible; no invented price text',
            'A lateral move reveals range without entering staff space']
    elif key=='commercial-texture':
        for root in [o for o in scene.objects if o.get('asset_family') in ['cake_slice','brunch_toast','burger']]:G.remove(root)
        plate=min((o for o in scene.objects if o.get('asset_family')=='dinner_plate'),key=lambda o:o.location.y)
        subject=C.supported('croissant_oozing',plate,1.,1.38,scale=.88,turn=-.35,quality='approved-v2')
        for part in subject.children_recursive:
            if part.name.startswith('Filling / restrained chocolate core'):
                part.scale.y*=1.4;part.scale.z*=2.2
        C.role(subject,'hero');C.role(plate,'support');scene.camera.data.lens=38
        centre=G.centre(subject)
        start=centre+Vector((.15,-.48,.23));end=centre+Vector((-.14,-.38,.36));first=last=centre
        row['hero_family']='croissant_oozing';row['fits_entire_subject']=True
        row['staging']=['Already opened halves remain supported on one off-centre plate',
            'Cut faces and restrained filling are the main subject, with a cup as scale context',
            'Fixed side light separates the crust and filling; no animated lighting or food manipulation']
    else:
        subject=next(o for o in scene.objects if o.get('asset_family')=='dining_table')
        C.role(subject,'hero');scene.camera.data.lens=18
        for root in scene.objects:
            if root.get('asset_family') in ['dinner_plate','cake_slice','latte_cup','dining_chair','saucer'] and root.location.y<2.7:C.role(root,'support')
        start=Vector((-.30,1.25,1.20));end=Vector((-.10,.55,1.68))
        first=Vector((1.02,1.55,.93));last=Vector((1.18,1.70,1.25))
        row['hero_family']='dining_table';row['fits_entire_subject']=True
        row['staging']=['Two usable opposing place settings; dishes remain away from the table centre',
            'Near chair, table and background move at different speeds through parallax',
            'Window-side table and its lighting tell viewers what sitting here feels like']
    def sample(t):
        u=C.smooth(t,1.2,row['move_end'])
        p=start.lerp(end,u);q=first.lerp(last,u)
        # Small curved translation, with one smooth start and settle.
        p.y-=.055*math.sin(math.pi*u)
        return p,q
    row['sample_camera']=sample;row['subject_name']=subject.name
    return [(0,tuple(start),tuple(first)),(row['duration'],tuple(end),tuple(last))],list(C.CONTACTS)


def parents(o):
    p=o.parent
    while p:yield p;p=p.parent

SCENES={
 'commercial-display':dict(duration=7,capture=5,move_end=4.5,guide='shelf_slide_left',template='bakery-fresh-batch',step='shelf',
    title='Commercial / pastry display sweep',direction=DISPLAY,source='creator-bakery',
    purpose='Show the available range clearly before choosing a product.',
    bindings=[bind('shelf_slide_left','bakery-fresh-batch','shelf','shot',5,DISPLAY,'truck','image_motion',.35,'left',4.5,update_global=False,anchor_type='case',anchor_kind='none')]),
 'commercial-texture':dict(duration=7,capture=5,move_end=4.5,guide='pastry_break_eye_hold',template='bakery-fresh-batch',step='break',
    title='Commercial / filling and texture reveal',direction=TEXTURE,source='dessert-orbit',
    purpose='Reveal the product detail that makes the pastry worth ordering, without handling it on camera.',
    bindings=[bind('pastry_break_eye_hold',tid,sid,'shot',5,TEXTURE,'orbit','orbit',None,'left',4.5,update_global=False,anchor_type='bread',arc=34)
        for tid,sid in [('bakery-fresh-batch','break'),('bakery-sell-out','break'),('bakery-ask-the-baker','inside')]]),
 'commercial-room':dict(duration=8,capture=6,move_end=5.4,guide='room_dining_eye_reveal_cw',template='restaurant-date-night',step='room',
    title='Commercial / window-side table and room reveal',direction=ROOM,source='dessert-orbit',
    purpose='Show the seating, light and atmosphere around the same meal, rather than an unrelated interior.',
    bindings=[bind('room_dining_eye_reveal_cw','restaurant-date-night','room','shot',6,ROOM,'dolly_out','image_scale',.65,None,5.4,update_global=False,anchor_type='room',anchor_kind='none')]),
}
for row in SCENES.values():
    row.update(freeze=True,locked_camera=True,setup=setup,revision='commercial-camera-only-2026-11-02-v1')
    row['composition']=['Teach subject staging, fixed side light and a repeatable handheld move',
        'No characters, hands, floating props or digital zoom',
        'One coherent take, ending with a deliberate cut']
    for b in row['bindings']:b['update_capture_seconds']=True

def validate(scene,spec,row,folder):
    subject=bpy.data.objects[row['subject_name']];samples=spec['camera']['samples'];checks=[]
    for frame in [1,round(spec['frame_count']/2),spec['frame_count']]:
        scene.frame_set(frame);bpy.context.view_layer.update()
        pts=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for o in C.meshes(subject) for v in o.data.vertices]
        bounds=[min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts)]
        if row['fits_entire_subject']:assert all(.008<v<.992 for v in bounds),(row['title'],frame,bounds)
        checks.append(dict(frame=frame,bounds=bounds))
    assert spec['camera']['max_speed_m_s']<.65
    report=dict(status='passed',no_humans=True,no_hand_animation=True,fixed_lens_mm=scene.camera.data.lens,
        max_speed_m_s=spec['camera']['max_speed_m_s'],max_turn_deg_s=spec['camera']['max_turn_deg_s'],
        public_camera_positions=all(r['position'][1]<3.7 for r in samples),framing=checks,contacts=spec['contacts'],
        commercial_purpose=row['purpose'],staging=row['staging'])
    (folder/'commercial-review.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',choices=SCENES);p.add_argument('--build',action='store_true');p.add_argument('--probes',action='store_true');p.add_argument('--resume',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    G.SCENES.update(SCENES)
    for key in [a.scene] if a.scene else SCENES:
        row=SCENES[key];G.SOURCE=G.ROOT/row['source']/'scene.blend'
        if a.build:
            scene,spec,folder=G.build(key);review=validate(scene,spec,row,folder)
            spec.update(commercial_purpose=row['purpose'],staging=row['staging'],commercial_review=review,
                generation_credits_used=0,color_samples=16,denoise_color=True,cache_static_camera_frames=True,
                venue='dining' if key=='commercial-room' else 'bakery',venue_kinds=['dining'] if key=='commercial-room' else ['bakery'],
                no_humans=True,no_hand_animation=True)
            (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        if a.probes or not a.build:G.render(key,a.probes,a.resume)
