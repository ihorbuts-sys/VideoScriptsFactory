"""Phone-feasible food shots from the reviewed primary-object library."""
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
from build_coffee_work_guides import bind


BURGER = 'Leave the burger on its plate at your place setting. Start with the phone low beside the table edge, then lean forward gently on a short diagonal, raising it a few centimetres to show the layers. Keep the lens fixed, settle on the burger, and cut to the next step.'
BRUNCH = 'Stand beside the table with both feet on the floor. Point the phone straight down over your toast, then lift it slowly from chest to eye height while leaning back slightly. Reveal the second place setting and both cups on this same table. Hold the spread, then cut to the selfie.'
CAKE = 'Keep the dessert plate at your place setting. From a seated position, hold the phone above the plate at an angle and trace a small arc to the left, lowering it gently to reveal the cake layers. Keep the plate and cup supported, settle, then cut to your first-bite reaction.'


def soften_background(scene, preserve=()):
    linear=lambda v:v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
    for obj in scene.objects:
        if obj.type=='MESH' and obj not in preserve and obj.get('ghost_role')!='absent':
            obj.color=(linear(.035),linear(.22),0,1)
            obj['guide_role']='context'


def setup(scene, key, row):
    P.MATS.clear()
    C.CACHE.clear()
    C.CONTACTS.clear()
    bpy.ops.object.select_all(action='DESELECT')
    table = next(o for o in scene.objects if o.get('asset_family') == 'dining_table')
    # Remove whole old place settings before laying out the new shared table.
    old = [o for o in scene.objects if o.get('asset_family') in
           ['latte_cup', 'saucer', 'croissant', 'croissant_oozing'] and .9 < o.location.y < 2.1]
    for obj in old:
        G.remove(obj)
    soften_background(scene)
    C.role(table, 'support')
    placed = []

    def put(aid, support, x, y, scale=1, turn=0, quality=None, role='hero'):
        obj = C.supported(aid, support, x, y, scale=scale, turn=turn, quality=quality)
        C.role(obj, role)
        placed.append(obj)
        if aid == 'latte_cup':
            # Fill the actual hollow cup using its calibrated rim, not a world-space guess.
            anchors=json.loads((P.ROOT/'latte_cup/functional/metadata.json').read_text())['anchors']
            rim=next(o for o in obj.children_recursive if o.get('function')=='rim')
            centre=rim.matrix_world.translation.copy()
            z=centre.z-(anchors['rim'][2]-anchors['liquid_final_z'])*scale
            r=anchors['radius']*.89*scale
            liquid=P.lathe('Table coffee / contained in calibrated cup',
                [(0,-.002),(r,-.002),(r,0),(0,0)],tuple((centre.x,centre.y,z)),'coffee')
            liquid.parent=obj
            liquid.matrix_parent_inverse=obj.matrix_world.inverted()
            liquid.color=next(iter(C.meshes(obj))).color[:]
            liquid['guide_role']=role
            assert z < centre.z-.006
        return obj

    # Opposing reachable settings, with a clear central gap and no centred dish.
    near = put('dinner_plate', table, 1.00, 1.38, turn=-.12)
    food = put('brunch_toast' if key == 'brunch-spread' else 'burger' if key == 'burger-hero' else 'cake_slice',
               near, 1.00, 1.38, turn=.25 if key == 'dessert-orbit' else -.18)
    saucer = put('saucer', table, 1.39, 1.39, scale=.9, quality='local', role='support')
    put('latte_cup', saucer, 1.39, 1.39, scale=.9, turn=-.8, quality='functional', role='support')
    far = put('dinner_plate', table, 1.30, 1.75, role='support')
    put('brunch_toast' if key == 'brunch-spread' else 'cake_slice',
        far, 1.30, 1.75, scale=.88, turn=math.pi+.35, role='support')
    far_saucer = put('saucer', table, .92, 1.75, scale=.9, quality='local', role='support')
    put('latte_cup', far_saucer, .92, 1.75, scale=.9, turn=2.2, quality='functional', role='support')
    bpy.context.view_layer.update()
    lo, hi = B.bounds(C.meshes(table))
    for root in [near, far, saucer, far_saucer]:
        a, b = B.bounds(C.meshes(root))
        assert lo.x < a.x < b.x < hi.x and lo.y < a.y < b.y < hi.y, (root.name, list(a), list(b))
        assert math.hypot(root.location.x-table.location.x, root.location.y-table.location.y) > .16
    # The two independent settings must not intersect in plan view.
    footprints = [(o, B.bounds(C.meshes(o))) for o in [near, far, saucer, far_saucer]]
    for i, (a, (alo, ahi)) in enumerate(footprints):
        for b, (blo, bhi) in footprints[i+1:]:
            assert ahi.x < blo.x or bhi.x < alo.x or ahi.y < blo.y or bhi.y < alo.y, (a.name, b.name)
    centre = G.centre(food)
    if key == 'burger-hero':
        scene.camera.data.lens = 34
        path = [(0, (.91,.83,.91), tuple(centre)),
                (1.2, (.91,.83,.91), tuple(centre)),
                (4.3, (1.08,1.00,.96), tuple(centre)),
                (6, (1.08,1.00,.96), tuple(centre))]
    elif key == 'dessert-orbit':
        scene.camera.data.lens = 31
        path = [(0, (1.19,.97,1.19), tuple(centre)),
                (1.2, (1.19,.97,1.19), tuple(centre)),
                (4.3, (.78,.99,1.10), tuple(centre)),
                (7, (.78,.99,1.10), tuple(centre))]
    else:
        scene.camera.data.lens = 20
        # Slightly nonzero Y delta avoids the exact-vertical quaternion pole.
        path = [(0, (1.00,1.3799,1.30), (1.00,1.38,.745)),
                (1.2, (1.00,1.3799,1.30), (1.00,1.38,.745)),
                (4.3, (1.13,1.5499,1.78), (1.13,1.55,.745)),
                (7, (1.13,1.5499,1.78), (1.13,1.55,.745))]
    row['placement_checks'] = dict(status='passed', table_bounds=[list(lo),list(hi)],
        plate_centres=[[1.,1.38],[1.30,1.75]], separate_place_settings=True,
        primary_food=row['food'], raycast_contacts=list(C.CONTACTS))
    def sample(t):
        u=C.smooth(t,1.2,4.3)
        if key=='dessert-orbit':
            angle=math.radians(25-54*u)
            position=Vector((1.+.455*math.sin(angle),1.38-.455*math.cos(angle),1.19-.09*u))
        else:
            position=Vector(path[0][1]).lerp(Vector(path[-1][1]),u)
        target=Vector(path[0][2]).lerp(Vector(path[-1][2]),u)
        return position,target
    row['sample_camera']=sample
    return path, list(C.CONTACTS)


SCENES = {
    'burger-hero': dict(duration=6, guide='burger_low_in_mc', template='quick-budget-run', step='second',
        title='Burger / low diagonal approach', capture=5, freeze=True, setup=setup, food='burger', direction=BURGER,
        bindings=[bind('burger_low_in_mc','quick-budget-run','second','shot',5,BURGER,
                       'dolly_in','image_scale',1.5,move_end=4.3,update_global=False,anchor_type='burger')]),
    'brunch-spread': dict(duration=7, guide='plate_spread_top_out_cw', template='restaurant-weekend-brunch', step='spread',
        title='Brunch / one plate to two place settings', capture=5, freeze=True, locked_camera=True, setup=setup, food='brunch_toast', direction=BRUNCH,
        bindings=[bind('plate_spread_top_out_cw','restaurant-weekend-brunch','spread','shot',5,BRUNCH,
                       'dolly_out','image_scale',.55,move_end=4.3,anchor_type='plate')]),
    'dessert-orbit': dict(duration=7, guide='plate_high_orbitl_cc', template='restaurant-date-night', step='dish',
        title='Dessert / descending seated arc', capture=5, freeze=True, setup=setup, food='cake_slice', direction=CAKE,
        bindings=[bind('plate_high_orbitl_cc','restaurant-date-night','dish','shot',5,CAKE,
                       'orbit','orbit',turn='left',move_end=4.3,anchor_type='plate',arc=54)]),
}
for row in SCENES.values():
    row['locked_camera']=True
    row['revision'] = 'primary-food-glass-2026-10-30-v2'
    row['composition'] = ['Two reachable opposing place settings; no plate at the table centre',
        'Food and cups supported by actual mesh raycasts',
        'Stationary window light, distinct hero and supporting props',
        'One coherent take; deliberate cut to the next step rather than unrelated appended footage']


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--scene',choices=SCENES);p.add_argument('--build',action='store_true');p.add_argument('--probes',action='store_true');p.add_argument('--resume',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    G.SCENES.update(SCENES)
    for key in [a.scene] if a.scene else SCENES:
        if a.build:
            scene,spec,folder=G.build(key)
            spec.update(placement_checks=SCENES[key]['placement_checks'],generation_credits_used=0,color_samples=32,
                cache_static_camera_frames=True,
                viewfinder_axes=['X','Y'] if key=='brunch-spread' else ['X'],
                background_emphasis='Context surfaces at 55% raw strength; food at full strength; one global 65% image-view multiplier',
                reused_primary_objects=['dinner_plate',SCENES[key]['food']],
                venue='dining' if key!='burger-hero' else 'fast-food',
                venue_kinds=['dining'] if key!='burger-hero' else ['fast-food'],
                handover_status='cut_to_next_step')
            from bpy_extras.object_utils import world_to_camera_view
            scene.frame_set(spec['frame_count'])
            main=next(o for o in scene.objects if o.get('asset_family')==SCENES[key]['food'])
            checked=next(o for o in scene.objects if o.get('asset_family')=='dining_table') if key=='brunch-spread' else main
            points=[world_to_camera_view(scene,scene.camera,o.matrix_world@v.co) for o in C.meshes(checked) for v in o.data.vertices]
            bounds=[min(p.x for p in points),max(p.x for p in points),min(p.y for p in points),max(p.y for p in points)]
            assert all(.015<v<.985 for v in bounds),('Final subject outside phone frame',key,bounds)
            spec['final_framing']=dict(object=checked.name,normalized_bounds=bounds)
            (folder/'scene-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
        if a.probes or not a.build:
            G.render(key,a.probes,a.resume)
