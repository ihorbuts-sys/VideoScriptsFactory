"""Room-from-table drafts after the 2026-11-10 audit (research venue D: D1 static, D2 plant reveal, D3 pan, D4 tilt)."""
import math
import bpy
from mathutils import Vector
from drafts.common import new_state, finish

IDS = ('room_seated_pan_v2', 'room_reveal_plant_v2', 'room_tilt_up_from_plate', 'room_static_wide')

# Seated lens height 115 cm, pitch 3 deg down at the target (venue D, judgement values in the research).
SEAT = Vector((0, -.25, 1.15))
PITCH = 3.
RAMP = .2  # share of the move spent speeding up (and again slowing down); peak speed = mean / (1 - RAMP)


def even(u, r=RAMP):
    """Fraction of the move done at u: constant speed with linear speed ramps at both ends."""
    u = max(0., min(1., u))
    if u < r:
        return u * u / (2 * r * (1 - r))
    if u > 1 - r:
        return 1 - (1 - u) ** 2 / (2 * r * (1 - r))
    return (u - r / 2) / (1 - r)


def look(position, yaw, pitch, distance=4.):
    """Aim point for a yaw (deg, positive to the right of +Y) and a pitch (deg, positive looking down)."""
    y, p = math.radians(yaw), math.radians(pitch)
    return position + Vector((math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p))) * distance


def build(gid, record, P):
    A = P.A
    state = new_state()
    heroes = P.room()
    if gid == 'room_reveal_plant_v2':
        # Same plant as room_reveal_plant, turned so its tallest front leaf sits at the right-front at lens height.
        plant = P.V.plant((-.22, .85, 0), height=1.5)
        plant.rotation_euler.z = math.radians(PLANT_TURN)
        P.role(plant, 'foreground')
        plant['p0_reveal_plant'] = True
        state['contacts'].append(dict(kind='floor_plant_reveal', plant=plant.name, no_foreground_table=True))
        state['adaptations'].append('Seated beside a floor plant: lens 115 cm, about 7 cm behind its nearest leaf, slide right; no table under the camera or through the plant.')
        end = Vector(PLANT_END)
        aim = look(end, PLANT_YAW, PITCH)
        def sample(u, p, t):
            v = Vector((-PLANT_TRUCK * (1 - even(u)), 0, 0))
            return p + v, t + v
        return finish(state, heroes, end, aim, sample)
    A.table((.1, 0, 0), .55)
    if gid == 'room_tilt_up_from_plate':
        plate = A.pasta((0, .15, .785))
        P.role(plate, 'support')
        A.fork((-.19, .15, .795))
        drink, _ = P.cup(.24, .34, .785, False)
        P.role(drink, 'support')
        def sample(u, p, t):
            return p, look(p, TILT_YAW, PITCH + TILT * (1 - even(u)))
        return finish(state, heroes, SEAT, look(SEAT, TILT_YAW, PITCH), sample)
    if gid == 'room_static_wide':
        # Your cup whole in the lower left; pitch 5 brings the horizon nearer the D1 line at y 40%.
        drink, _ = P.cup(-.14, .24, .785, False)
        P.role(drink, 'foreground')
        return finish(state, heroes, SEAT, look(SEAT, STATIC_YAW, STATIC_PITCH))
    drink, _ = P.cup(-.25, .22, .785, False)
    P.role(drink, 'foreground')
    before = set(bpy.data.objects)
    P.counter()
    P.role(A.group('Counter at left of room', before, (-2.5, 2, 0)), 'background')
    def sample(u, p, t):
        return p, look(p, PAN_END + PAN * (1 - even(u)), PITCH)
    return finish(state, heroes, SEAT, look(SEAT, PAN_END, PITCH), sample)


# Pan: 30 deg leftwards over 4 s, ending on the original end heading (15 deg left of the room axis);
# starts 15 deg later than the 45 deg round-2 pan (owner 2026-11-11 r2), 9.5 deg/s between the ramps as before.
PAN, PAN_END = 30., -15.
# Tilt: 30 deg up from the plate to the room.
TILT, TILT_YAW = 30., -2.
STATIC_YAW, STATIC_PITCH = -2., 5.
# Plant reveal: truck right; the end lens position and heading.
PLANT_TURN, PLANT_TRUCK, PLANT_END, PLANT_YAW = 45., .40, (.52, .44, 1.15), -2.
