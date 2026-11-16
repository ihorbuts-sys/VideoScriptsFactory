"""Visit selfie takeaway (catalog v3, 2026-11-16): front camera at arm's length in front of the reception desk.

Built like experience_selfie_after: the standing canonical creator and its open-palm verdict are p0_people's published
verdict_eye_level pose (owner reviewed 2026-11-10), built unchanged; its cafe furniture (side table, cup and saucer,
pendant) and the window are left out. Behind her stands the approved reception desk composition of visit_reception_pan
(p0_scenes.counter body minus the espresso machine, drying cups and glasses and card holder, Tripo laptop screen to
the staff side), drawn faint as background; the floor plant stays. No other people. Camera rule from
verdict_eye_level_v2 (people_v2.place_camera): front 23 mm, 0.60 m from the eyes at eye height, 5 deg to her right."""
import bpy
import p0_people as PP
from drafts.people_v2 import place_camera, trim_face_mask, EYE_REST, FRONT_LENS
from drafts.counter_case import library_model
from drafts.visit_reception_pan import LAPTOP, REMOVED

IDS = ('visit_selfie_takeaway',)
CAMERA = ('hand', .60, 0., 5.)
# Desk footprint origin (counter frame: customer edge at local y -.15, top at z 1.05); staff side +Y, so its
# customer face looks at the lens. Offset to her left shoulder so the top edge and laptop read beside her head.
DESK = (1.0, 2.75, 0)


def build(gid, record, P):
    A = P.A
    left_out = []

    def dropped(owner, name):
        original = getattr(owner, name)

        def wrapper(*args, **kwargs):
            before = set(bpy.data.objects)
            result = original(*args, **kwargs)
            left_out.extend(o for o in bpy.data.objects if o not in before)
            return result
        return original, wrapper

    patches = [(P.A, 'table'), (P, 'cup'), (P.V, 'pendant'), (P.V, 'window')]
    originals = []
    for owner, name in patches:
        original, wrapper = dropped(owner, name)
        originals.append((owner, name, original))
        setattr(owner, name, wrapper)
    try:
        state = PP.build('verdict_eye_level', record, P)
    finally:
        for owner, name, original in originals:
            setattr(owner, name, original)
    for obj in left_out:
        if obj.name in bpy.data.objects:
            bpy.data.objects.remove(obj, do_unlink=True)

    face = trim_face_mask(state['hero'])
    state.update(hero=face, framing_masks=face, lens_mm=FRONT_LENS)

    root = state['character_root']
    arm = next(o for o in root.children_recursive if o.type == 'ARMATURE')
    head = PP.named(arm, 'Head')
    eye_local = (arm.matrix_world @ head.matrix).inverted() @ EYE_REST
    state['actions'][0](1.)
    bpy.context.view_layer.update()
    eye = arm.matrix_world @ head.matrix @ eye_local
    position, target, measured = place_camera(CAMERA, eye, FRONT_LENS)
    measured.pop('lens_above_table_m', None)

    before = set(bpy.data.objects)
    P.counter(body=True)
    for obj in [o for o in bpy.data.objects if o not in before and o.name.startswith(REMOVED)]:
        bpy.data.objects.remove(obj, do_unlink=True)
    library_model(P, 'laptop', (LAPTOP[0], LAPTOP[1], 1.05), 'background')
    desk = A.group('Reception desk (approved composition)', before, DESK)
    P.role(desk, 'background')

    state['contacts'].append(dict(kind='reception_desk_behind', desk=desk.name,
                                  customer_edge_y=DESK[1] - .15, people=1))
    state['contacts'].append(dict(kind='selfie_camera', **measured))
    state['adaptations'] = [
        'Standing canonical creator and open-palm gesture exactly as the published verdict_eye_level (p0_people), plain rig.',
        'Cafe side table, cup, saucer, pendant and window left out; floor plant kept; the approved reception desk '
        f'composition (visit_reception_pan) stands behind her, customer edge {DESK[1] - .15 - eye.y:.1f} m behind her eyes, '
        'drawn as background (faint). Floor and walls are not drawn (STYLE). No other people.',
        f'Front camera {FRONT_LENS} mm, lens {measured["lens_to_eye_m"]:.2f} m from the eyes, {measured["lens_above_eye_m"] * 100:+.0f} cm vs '
        f'eye height, {measured["pitch_deg"]:.1f} deg down so the eyes sit one third from the top (verdict_eye_level_v2 rule).',
        'Protected face is the eye line to the chin (people_v2.trim_face_mask).']
    return dict(state, target_position=position, target_aim=target, sample=lambda u, p, t: (p, t))
