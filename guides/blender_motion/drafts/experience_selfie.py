"""Experience selfie after the session (catalog v3, 2026-11-16): front camera at arm's length on an open training floor.

The standing canonical creator and its open-palm verdict are p0_people's published verdict_eye_level pose (owner
reviewed 2026-11-10), built unchanged; only its cafe furniture (side table, cup and saucer, pendant) and the floor plant are left out and the
approved Tripo dumbbells rest on the floor behind her. Camera rule from verdict_eye_level_v2 (people_v2.place_camera):
front 23 mm, 0.60 m from the eyes at eye height, 5 deg to her right, eyes one third from the top."""
import bpy
from mathutils import Vector
import p0_people as PP
from drafts.people_v2 import place_camera, trim_face_mask, EYE_REST, FRONT_LENS
from drafts.counter_case import library_model

IDS = ('experience_selfie_after',)
CAMERA = ('hand', .60, 0., 5.)
# Three dumbbells on the floor in a row receding behind her left shoulder, in the gap beside her sleeve (judgement).
DUMBBELLS = [((1.66, 2.40, 0), 0.), ((1.84, 2.90, 0), 6.), ((2.00, 3.40, 0), -5.)]


def build(gid, record, P):
    left_out = []

    def dropped(owner, name):
        original = getattr(owner, name)

        def wrapper(*args, **kwargs):
            before = set(bpy.data.objects)
            result = original(*args, **kwargs)
            left_out.extend(o for o in bpy.data.objects if o not in before)
            return result
        return original, wrapper

    patches = [(P.A, 'table'), (P, 'cup'), (P.V, 'pendant'), (P.V, 'plant')]
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

    # Eye line measured on the posed head (gesture at rest), then the v2 selfie camera rule.
    root = state['character_root']
    arm = next(o for o in root.children_recursive if o.type == 'ARMATURE')
    head = PP.named(arm, 'Head')
    eye_local = (arm.matrix_world @ head.matrix).inverted() @ EYE_REST
    state['actions'][0](1.)
    bpy.context.view_layer.update()
    eye = arm.matrix_world @ head.matrix @ eye_local
    position, target, measured = place_camera(CAMERA, eye, FRONT_LENS)
    measured.pop('lens_above_table_m', None)

    for at, turn in DUMBBELLS:
        library_model(P, 'dumbbell', at, 'important_background', turn)

    state['contacts'].append(dict(kind='floor_rest', objects='dumbbell', count=len(DUMBBELLS), floor_z=0.))
    state['contacts'].append(dict(kind='selfie_camera', **measured))
    state['adaptations'] = [
        'Standing canonical creator and open-palm gesture exactly as the published verdict_eye_level (p0_people), plain rig.',
        'Cafe side table, cup, saucer, pendant and floor plant left out (owner 2026-11-17); window kept; three approved Tripo dumbbells '
        'rest on the floor behind her (dot cleanup in memory). Floor and walls are not drawn (STYLE).',
        f'Front camera {FRONT_LENS} mm, lens {measured["lens_to_eye_m"]:.2f} m from the eyes, {measured["lens_above_eye_m"] * 100:+.0f} cm vs '
        f'eye height, {measured["pitch_deg"]:.1f} deg down so the eyes sit one third from the top (verdict_eye_level_v2 rule).',
        'Protected face is the eye line to the chin (people_v2.trim_face_mask).']
    return dict(state, target_position=position, target_aim=target, sample=lambda u, p, t: (p, t))
