"""The venue entrance filmed from inside: a creator who is already in the venue turns to the door instead of going
back out to the street."""
import assets as A
import venue_assets as V
from motion_paths import camera_path, sequence

IDS = ['entrance_inside_eye_in_wm']


def review(gid):
    return dict(subject='The venue entrance seen from inside: glazed door, its windows, plants and the tables nearest to it',
                angle='Eye level, from the room toward the door',
                motion='A slow curved walk toward the door; height and pitch change together and settle',
                focal_point='The door opening, centred as the phone arrives',
                composition='Tables at the edges frame the aisle; the door and windows form the destination',
                golden_ratio='Practical sight lines and a clear destination take precedence',
                lighting='Fixed daylight through the door and windows lies on the floor; one lit pendant; no animated fixtures or bloom',
                contacts='Tables and chairs stand on the floor; the door stays in its frame',
                handover='Cut on the door to the next shot; the creator never films from the street',
                mobile='Visitor-side phone inside the venue; normal slow walking, about 1.5 m of travel')


def build(scene, spec):
    V.door()
    for x in [-1.25, 1.25]:
        V.window((x, 0, 1.25))
    for x, y in [(-1.15, 1.15), (1.2, 1.7)]:
        V.dining_table((x, y, 0))
    V.plant((-.82, .35, 0), 1.05)
    V.plant((.80, .40, 0), .8)
    V.daylight_patch([(-.50, .06), (.50, .06), (.95, 1.55), (-.85, 1.55)])
    for x in [-1.25, 1.25]:
        V.daylight_patch([(x - .50, .06), (x + .50, .06), (x + .62, .75), (x - .62, .75)], 'Window light on the floor')
    V.pendant((0, 1.0, 2.95))
    A.fixed_side_light((0, .8, 1.2))
    cam = camera_path('From inside toward the entrance', [
        (0, (.45, 3.20, 1.48), (0, 0, 1.25)), (1.2, (.42, 3.15, 1.48), (0, 0, 1.25)),
        (3.0, (.12, 1.95, 1.52), (0, 0, 1.20)), (4, (.06, 1.80, 1.52), (0, 0, 1.20))], 4, 30)
    result = sequence(cam, 4, actions=[
        'From inside, the glazed door and its windows grow as the phone walks toward the entrance',
        'The tables nearest the door pass at the edges; nothing is filmed from the street'])
    result['interior_kind'] = 'dining'
    result['framing_landmarks'] = [obj.name for obj in scene.objects if obj.type == 'MESH' and obj.name.startswith(('Door jamb', 'Door lintel', 'Glazed door'))]
    return result
